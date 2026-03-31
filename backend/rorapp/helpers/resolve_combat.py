import math
from typing import List
from rorapp.classes.random_resolver import RandomResolver
from rorapp.helpers.game_data import load_statesmen
from rorapp.helpers.kill_senator import CauseOfDeath, kill_senator
from rorapp.helpers.text import format_list
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import Campaign, EnemyLeader, Game, Log, Senator
from rorapp.models.fleet import Fleet
from rorapp.models.legion import Legion
from rorapp.models.war import War


def _get_matching_war_multiplier(war: War) -> int:
    """Return the strength multiplier from active matching wars (1, 2, 3, or 4)."""
    if not war.series_name:
        return 1
    return max(
        1,
        War.objects.filter(
            game=war.game_id,
            series_name=war.series_name,
            status=War.Status.ACTIVE,
        ).count(),
    )


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
    unmodified_result = random_resolver.roll_dice(3)
    naval_battle = war.naval_strength > 0
    active_leaders = list(
        EnemyLeader.objects.filter(
            game=game_id, series_name=war.series_name, active=True
        )
    )
    leader_strength = sum(l.strength for l in active_leaders)
    matching_war_multiplier = _get_matching_war_multiplier(war)

    if naval_battle:
        naval_force = len(uncommanded_campaign.fleets.all())
        effective_commander_strength = (
            commander.military if naval_force > commander.military else naval_force
        )
        positive_modifier = naval_force + effective_commander_strength
        negative_modifier = (
            war.naval_strength * matching_war_multiplier + leader_strength
        )
        war.fought_naval_battle = True
    else:
        land_force = sum(l.strength for l in uncommanded_campaign.legions.all())
        effective_commander_strength = (
            commander.military if land_force > commander.military else land_force
        )
        positive_modifier = land_force + effective_commander_strength
        negative_modifier = (
            war.land_strength * matching_war_multiplier + leader_strength
        )
        war.fought_land_battle = True
    modifier = positive_modifier - negative_modifier
    modified_result = unmodified_result + modifier

    # Check if the commander is a statesman who nullifies disaster/standoff for this war's series
    commander_data = None
    if commander.statesman_name:
        statesmen_dict = load_statesmen()
        commander_data = next(
            (v for v in statesmen_dict.values() if v["code"] == commander.code), None
        )
    nullified = (
        commander_data is not None
        and bool(war.series_name)
        and war.series_name in commander_data.get("nullifies_series", [])
    )
    roll_would_be_disaster = (
        unmodified_result in war.disaster_numbers
        and unmodified_result not in war.spent_disaster_numbers
    )
    roll_would_be_standoff = (
        unmodified_result in war.standoff_numbers
        and unmodified_result not in war.spent_standoff_numbers
    )

    # Determine result
    result = None
    if (
        not nullified
        and unmodified_result in war.disaster_numbers
        and unmodified_result not in war.spent_disaster_numbers
    ):
        result = "disaster"
        war.spent_disaster_numbers.append(unmodified_result)
    elif (
        not nullified
        and unmodified_result in war.standoff_numbers
        and unmodified_result not in war.spent_standoff_numbers
    ):
        result = "standoff"
        war.spent_standoff_numbers.append(unmodified_result)
    else:
        for leader in active_leaders:
            if (
                unmodified_result == leader.disaster_number
                and leader.disaster_number not in war.spent_disaster_numbers
            ):
                result = "disaster"
                war.spent_disaster_numbers.append(leader.disaster_number)
                Log.create_object(
                    game_id,
                    f"{leader.name}'s tactical skill caused an automatic disaster.",
                )
                break
            elif (
                unmodified_result == leader.standoff_number
                and leader.standoff_number not in war.spent_standoff_numbers
            ):
                result = "standoff"
                war.spent_standoff_numbers.append(leader.standoff_number)
                Log.create_object(
                    game_id,
                    f"{leader.name}'s tactical skill caused an automatic standoff.",
                )
                break

    if result is None:
        if modified_result < 8:
            result = "defeat"
        elif modified_result < 14:
            result = "stalemate"
        else:
            result = "victory"

    war.save()

    if nullified and (roll_would_be_disaster or roll_would_be_standoff):
        outcome = "disaster" if roll_would_be_disaster else "standoff"
        Log.create_object(
            game_id=game_id,
            text=f"A statesman's ability prevented a {outcome}.",
        )

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

    original_fleet_losses = fleet_losses
    original_legion_losses = legion_losses
    if commander_data and "halves_losses" in commander_data.get("special", []):
        fleet_losses = math.ceil(fleet_losses / 2)
        legion_losses = math.ceil(legion_losses / 2)
    fabius_saved_fleets = original_fleet_losses - fleet_losses
    fabius_saved_legions = original_legion_losses - legion_losses

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
    if destroyed_legions or destroyed_fleets:
        log_text += (
            f" {unit_list_to_string(list(destroyed_legions), list(destroyed_fleets))}"
        )
    if destroyed_legions or destroyed_fleets:
        if len(destroyed_legions) + len(destroyed_fleets) > 1:
            log_text += " were"
        else:
            log_text += " was"
    else:
        log_text += " No"
        if legions:
            log_text += " legions"
            if fleets:
                log_text += " or"
        if fleets:
            log_text += " fleets"
        log_text += " were"
    log_text += " lost."

    if fabius_saved_legions > 0 or fabius_saved_fleets > 0:
        saved_parts = []
        if fabius_saved_legions > 0:
            saved_parts.append(
                f"{fabius_saved_legions} {'legion' if fabius_saved_legions == 1 else 'legions'}"
            )
        if fabius_saved_fleets > 0:
            saved_parts.append(
                f"{fabius_saved_fleets} {'fleet' if fabius_saved_fleets == 1 else 'fleets'}"
            )
        log_text += f" Fabius' delaying tactics saved {' and '.join(saved_parts)} from destruction."

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
            if popularity_change > 0:
                commander_log_text += f" and {popularity_change} popularity"
            commander_log_text += "."
        commander.save()
        if popularity_change < 0:
            if commander_log_text:
                commander_log_text += " "
            subject = "him" if commander_log_text else commander.display_name
            commander_log_text += f"Loss of legions caused {subject} to lose {-popularity_change} popularity."
        if commander_log_text:
            Log.create_object(game_id=game_id, text=commander_log_text)

    # Handle end of war
    if war_ends:
        returning_commanders = []
        returning_legions: List[Legion] = []
        returning_fleets: List[Fleet] = []

        war_campaigns = Campaign.objects.filter(
            game_id=game_id, war_id=war.id, commander__isnull=False
        )
        for war_campaign in war_campaigns:
            if not war_campaign.commander:
                continue
            # Fetch fresh commander from database to avoid stale object issues
            campaign_commander = Senator.objects.get(id=war_campaign.commander.id)
            campaign_commander.location = "Rome"
            campaign_commander.remove_title(Senator.Title.PROCONSUL)
            campaign_commander.save()
            returning_commanders.append(campaign_commander)
            surviving_legions = list(
                Legion.objects.filter(game=game, campaign=war_campaign)
            )
            surviving_fleets = list(
                Fleet.objects.filter(game=game, campaign=war_campaign)
            )
            if surviving_legions:
                returning_legions.extend(surviving_legions)
            if surviving_fleets:
                returning_fleets.extend(surviving_fleets)
        war.delete()  # Also deletes campaigns via cascade

        # Deactivate enemy leaders if they have no remaining active matching war
        survived_leaders = []
        for leader in active_leaders:
            matching_wars = War.objects.filter(
                game=game_id,
                series_name=leader.series_name,
                status=War.Status.ACTIVE,
            )
            if not matching_wars.exists():
                leader.active = False
                leader.save()
                survived_leaders.append(leader.name)
        if survived_leaders:
            Log.create_object(
                game_id,
                f"{format_list(survived_leaders)} withdrew following Rome's victory.",
            )

        return_log_text = ""
        if returning_commanders:
            commander_names = [c.display_name for c in returning_commanders]
            return_log_text += f"{format_list(commander_names)} returned to Rome."
            if returning_legions or returning_fleets:
                return_log_text += " "
        if returning_legions or returning_fleets:
            return_log_text += f"{unit_list_to_string(returning_legions, returning_fleets)} returned to the reserve forces."
        Log.create_object(game_id, return_log_text)

    # Naval victory
    elif result == "victory":
        war.naval_strength = 0
        war.save()
        if not commander_killed and legion_survivals == 0:
            uncommanded_campaign.commander = None
            uncommanded_campaign.save()
            commander.location = "Rome"
            commander.remove_title(Senator.Title.FIELD_CONSUL)
            commander.remove_title(Senator.Title.ROME_CONSUL)
            commander.save()
        elif not commander_killed and legion_survivals > 0:
            if fleet_survivals >= war.fleet_support and war.land_strength > 0:
                commander.add_status_item(Senator.StatusItem.CONSIDERING_LAND_BATTLE)
                commander.save()

    # Delete campaign if commander killed and no units survived
    if commander_killed and (fleet_survivals + legion_survivals) == 0:
        try:
            uncommanded_campaign = Campaign.objects.get(game=game_id, id=campaign_id)
            uncommanded_campaign.delete()
        except Campaign.DoesNotExist:
            pass

    return True
