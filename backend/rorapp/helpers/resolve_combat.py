from typing import List, Optional
from rorapp.classes.random_resolver import RandomResolver, RealRandomResolver
from rorapp.helpers.kill_senator import CauseOfDeath, kill_senator
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import Campaign, Game, Log, Senator
from rorapp.models.fleet import Fleet
from rorapp.models.legion import Legion


def resolve_combat(
    game_id: int, campaign_id: int, random_resolver: RandomResolver
) -> bool:

    uncommanded_campaign = Campaign.objects.get(game=game_id, id=campaign_id)
    if not uncommanded_campaign:
        return False
    uncommanded_campaign.pending = False
    uncommanded_campaign.imminent = False
    uncommanded_campaign.save()

    war = uncommanded_campaign.war
    commander = uncommanded_campaign.commander
    if not commander:
        return False

    # Determine dice roll and modifier
    unmodified_result = random_resolver.roll_dice()
    naval_battle = war.naval_strength > 0
    if naval_battle:
        naval_force = len(uncommanded_campaign.fleets.all())
        effective_commander_strength = (
            commander.military if naval_force > commander.military else naval_force
        )
        positive_modifier = naval_force + effective_commander_strength
        negative_modifier = war.naval_strength
        war.fought_naval_battle = True
    else:
        land_force = sum(l.strength for l in uncommanded_campaign.legions.all())
        effective_commander_strength = (
            commander.military if land_force > commander.military else land_force
        )
        positive_modifier = land_force + effective_commander_strength
        negative_modifier = war.land_strength
        war.fought_land_battle = True
    modifier = positive_modifier - negative_modifier
    modified_result = unmodified_result + modifier

    # Determine result
    if (
        unmodified_result in war.disaster_numbers
        and unmodified_result not in war.spent_disaster_numbers
    ):
        result = "disaster"
        war.spent_disaster_numbers.append(unmodified_result)
    elif (
        unmodified_result in war.standoff_numbers
        and unmodified_result not in war.spent_standoff_numbers
    ):
        result = "standoff"
        war.spent_standoff_numbers.append(unmodified_result)
    elif modified_result < 8:
        result = "defeat"
    elif modified_result < 14:
        result = "stalemate"
    else:
        result = "victory"

    war.save()

    # Determine losses
    fleets = list(uncommanded_campaign.fleets.all())
    legions = list(uncommanded_campaign.legions.all())
    if result == "disaster":
        fleet_losses = (len(fleets) + 1) // 2
        legion_losses = (len(legions) + 1) // 2
    elif result == "standoff":
        fleet_losses = (len(fleets) + 3) // 4
        legion_losses = (len(legions) + 3) // 4
    elif result == "defeat":
        if modified_result < 4:
            fleet_losses = len(fleets)
            legion_losses = len(legions)
        else:
            fleet_losses = min(8 - modified_result, len(fleets))
            legion_losses = min(8 - modified_result, len(legions))
    elif result == "stalemate":
        fleet_losses = min(13 - modified_result, len(fleets))
        legion_losses = min(13 - modified_result, len(legions))
    elif result == "victory":
        if modified_result < 18:
            fleet_losses = min(18 - modified_result, len(fleets))
            legion_losses = min(18 - modified_result, len(legions))
        else:
            fleet_losses = legion_losses = 0

    destroyed_fleets: List[Fleet]
    surviving_fleets: List[Fleet]
    destroyed_fleets, surviving_fleets = random_resolver.select_casualties(
        fleets, fleet_losses
    )
    fleet_survivals = len(surviving_fleets)

    destroyed_legions: List[Legion]
    surviving_legions: List[Legion]
    destroyed_legions, surviving_legions = random_resolver.select_casualties(
        legions, legion_losses
    )
    legion_survivals = len(surviving_legions)

    war_ends = False
    if result == "victory" and (
        (naval_battle and war.land_strength == 0)
        or (not naval_battle and war.naval_strength == 0)
    ):
        war_ends = True

    # Start building the main notification
    log_text = "In a "
    log_text += "naval" if naval_battle else "land"
    log_text += f" battle, {commander.display_name}"
    log_text += "'" if commander.display_name.endswith("s") else "'s"
    log_text += " Campaign"
    log_text += " won" if result == "victory" else " met with"
    log_text += f" a {result}"

    if war_ends:
        log_text += f", bringing an end to the {war.name}."
    elif result == "victory":
        log_text += f", eliminating enemy naval control in the {war.name}."
    else:
        log_text += f", allowing the {war.name} to continue."
    if len(destroyed_legions) + len(destroyed_fleets) > 0:
        log_text += (
            f" {unit_list_to_string(list(destroyed_legions), list(destroyed_fleets))}"
        )
    if len(destroyed_legions) > 0 or len(destroyed_fleets) > 0:
        if len(destroyed_legions) + len(destroyed_fleets) > 1:
            log_text += " were"
        else:
            log_text += " was"
    else:
        log_text += " No"
        if len(legions) > 0:
            log_text += " legions"
            if len(fleets) > 0:
                log_text += " or"
        if len(fleets) > 0:
            log_text += " fleets"
        log_text += " were"
    log_text += " lost."

    game = Game.objects.get(id=game_id)

    # Update unrest
    if result in ["defeat", "disaster"]:
        if result == "defeat":
            unrest_change = 2
        elif result == "disaster":
            unrest_change = 1
        game.unrest += unrest_change
        game.save()
        log_text += f" Unrest increased by {unrest_change}."
    elif result == "victory":
        unrest_change = game.change_unrest(-1)
        game.save()
        if unrest_change == -1:
            log_text += f" Unrest lowered by 1."

    # Spoils
    if war_ends:
        log_text += f" The State Treasury gained {war.spoils}T in spoils of war."
        game.state_treasury += war.spoils
        game.save()

    Log.create_object(game_id=game_id, text=log_text)

    # Apply losses
    for fleet in destroyed_fleets:
        fleet.delete()
    for legion in destroyed_legions:
        legion.delete()

    # Kill commander
    commander_killed = False
    if result == "defeat":
        commander_killed = True
    else:
        codes = random_resolver.draw_mortality_chits(fleet_losses + legion_losses)
        if any(commander.code.startswith(str(c)) for c in codes):
            commander_killed = True
    if commander_killed:
        kill_senator(game_id, commander.id, CauseOfDeath.BATTLE)

    # Update commander stats
    commander_log_text = ""
    if not commander_killed:
        glory_amount = 0
        popularity_loss = legion_losses // 2
        if result == "victory":
            glory_amount = (
                (war.naval_strength + 1) // 2
                if naval_battle
                else (war.land_strength + 1) // 2
            )
        popularity_change = commander.change_popularity(glory_amount - popularity_loss)
        if result == "victory":
            commander.influence += glory_amount
            commander_log_text += f"Military glory rewards {commander.display_name} with {glory_amount} influence"
            displayed_pop_gain = -popularity_loss + popularity_change
            if displayed_pop_gain > 0:
                commander_log_text += f" and {displayed_pop_gain} popularity"
            commander_log_text += "."
        commander.save()
        displayed_pop_loss = -glory_amount + popularity_change
        if displayed_pop_loss < 0:
            if result == "victory":
                commander_log_text += " "
            commander_log_text += f"Loss of legions causes {commander.display_name} to lose {displayed_pop_loss} popularity."
        if commander_log_text:
            Log.create_object(game_id=game_id, text=commander_log_text)

    # Handle end of war
    if war_ends:
        returning_commanders = []
        returning_legions: List[Legion] = []
        returning_fleets: List[Fleet] = []

        war_campaigns = Campaign.objects.filter(
            game=game_id, war=war, commander__isnull=False
        ).select_related("commander")
        for war_campaign in war_campaigns:
            if not war_campaign.commander:
                continue
            war_campaign.commander.location = "Rome"
            war_campaign.commander.remove_title(Senator.Title.PROCONSUL)
            war_campaign.commander.save()
            returning_commanders.append(war_campaign.commander)
            surviving_legions = list(
                Legion.objects.filter(game=game, campaign=war_campaign)
            )
            surviving_fleets = list(
                Fleet.objects.filter(game=game, campaign=war_campaign)
            )
            if len(surviving_legions) > 0:
                returning_legions.extend(surviving_legions)
            if len(surviving_fleets) > 0:
                returning_fleets.extend(surviving_fleets)
        war.delete()  # Also deletes campaigns via cascade

        return_log_text = ""
        if len(returning_commanders) > 0:
            for i in range(len(returning_commanders)):
                returning_commander = returning_commanders[i]
                if i > 0:
                    if i == len(returning_commanders) - 1:
                        return_log_text += " and "
                    else:
                        return_log_text += ", "
                return_log_text += f"{returning_commander.display_name}"
            return_log_text += " returned to Rome."
            if len(returning_legions) + len(returning_fleets) > 0:
                return_log_text += " "
        if len(returning_legions) + len(returning_fleets) > 0:
            return_log_text += f"{unit_list_to_string(returning_legions, returning_fleets)} returned to the reserve forces."
        Log.create_object(game_id, return_log_text)

    # Naval victory
    elif result == "victory":
        war.naval_strength = 0
        war.save()

    # Delete campaign if commander killed and no units survived
    if commander_killed and (fleet_survivals + legion_survivals) == 0:
        try:
            uncommanded_campaign = Campaign.objects.get(game=game_id, id=campaign_id)
            uncommanded_campaign.delete()
        except Campaign.DoesNotExist:
            pass

    return True
