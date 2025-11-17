import random
from rorapp.helpers.hrao import set_hrao
from rorapp.helpers.kill_senator import CauseOfDeath, kill_senator
from rorapp.helpers.mortality_chits import draw_mortality_chits
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import Campaign, Game, Log, Senator


def resolve_combat(game_id: int, campaign_id: int) -> bool:
    campaign = Campaign.objects.get(game=game_id, id=campaign_id)
    if not campaign:
        return False
    campaign.pending = False
    campaign.imminent = False
    campaign.save()

    war = campaign.war
    commander = campaign.commander
    if not commander:
        return False

    # Determine dice roll and modifier
    unmodified_result = (
        random.randint(1, 6) + random.randint(1, 6) + random.randint(1, 6)
    )
    naval_battle = war.naval_strength > 0
    if naval_battle:
        naval_force = len(campaign.fleets.all())
        effective_commander_strength = (
            commander.military if naval_force > commander.military else naval_force
        )
        positive_modifier = naval_force + effective_commander_strength
        negative_modifier = war.naval_strength
        war.fought_naval_battle = True
    else:
        land_force = sum(l.strength for l in campaign.legions.all())
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
    fleets = campaign.fleets.all()
    legions = campaign.legions.all()
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

    fleets_bag = list(fleets)
    random.shuffle(fleets_bag)
    destroyed_fleets = fleets_bag[:fleet_losses]
    destroyed_fleets = sorted(destroyed_fleets, key=lambda f: f.number)
    fleet_survivals = len(fleets_bag) - fleet_losses

    legions_bag = list(legions)
    random.shuffle(legions_bag)
    destroyed_legions = legions_bag[:legion_losses]
    destroyed_legions = sorted(destroyed_legions, key=lambda l: l.number)
    legion_survivals = len(legions_bag) - legion_losses

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
    if len(destroyed_legions) > 0:
        destroyed_legion_names = unit_list_to_string(list(destroyed_legions))
        log_text += f" {len(destroyed_legions)} {'legions' if len(destroyed_legions) > 1 else 'legion'} ({destroyed_legion_names})"
        if len(destroyed_fleets) > 0:
            log_text += " and"
    if len(destroyed_fleets) > 0:
        destroyed_fleet_names = unit_list_to_string(list(destroyed_fleets))
        log_text += f" {len(destroyed_fleets)} {'fleets' if len(destroyed_fleets) > 1 else 'fleet'} ({destroyed_fleet_names})"
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
        game.unrest -= 1
        game.save()
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
        codes = draw_mortality_chits(fleet_losses + legion_losses)
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
            displayed_pop_gain = -1 * popularity_loss + popularity_change
            if displayed_pop_gain > 0:
                commander_log_text += f" and {displayed_pop_gain} popularity"
            commander_log_text += "."
        commander.save()
        displayed_pop_loss = -1 * glory_amount + popularity_change
        if displayed_pop_loss < 0:
            if result == "victory":
                commander_log_text += " "
            commander_log_text += f"Loss of legions causes {commander.display_name} to lose {displayed_pop_loss} popularity."
        if commander_log_text:
            Log.create_object(game_id=game_id, text=commander_log_text)

    # Handle end of war
    if war_ends:
        campaigns = Campaign.objects.filter(game=game_id, war=war)
        for war_campaign in campaigns:
            if war_campaign.commander:
                war_campaign.commander.location = "Rome"
                war_campaign.commander.remove_title(Senator.Title.PROCONSUL)
                war_campaign.commander.save()
                set_hrao(game_id)
        war.delete()  # Also deletes campaigns via cascade

    # Naval victory
    elif result == "victory":
        war.naval_strength = 0
        war.save()

    # Delete campaign if commander killed and no units survived
    if commander_killed:
        campaign_exits = True
        try:
            campaign = Campaign.objects.get(game=game_id, id=campaign_id)
        except Campaign.DoesNotExist:
            campaign_exits = False
        if campaign_exits and (fleet_survivals + legion_survivals) == 0:
            campaign.delete()

    return True
