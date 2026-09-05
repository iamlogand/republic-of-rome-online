from typing import List, Optional, Tuple

from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import RandomResolver
from rorapp.helpers.combat_results import (
    DEFEAT,
    STALEMATE,
    VICTORY,
    combat_losses,
    combat_result,
)
from rorapp.helpers.game_data import get_senator_codes
from rorapp.helpers.kill_senator import CauseOfDeath, kill_senators
from rorapp.helpers.text import format_list
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import Campaign, Fleet, Game, Legion, Log, Senator, War

RESULT_NAMES = {
    VICTORY: "Senate Victory",
    STALEMATE: "Civil War Stalemate",
    DEFEAT: "Senate Defeat",
}


def _rebel_campaign(war: War) -> Optional[Campaign]:
    if not war.primary_rebel:
        return None
    return Campaign.objects.filter(
        game=war.game_id, commander=war.primary_rebel
    ).first()


def _promote_veteran(
    legions: List[Legion],
    commander: Optional[Senator],
    random_resolver: RandomResolver,
    game_id: int,
) -> None:
    promoted = random_resolver.select_veteran([l for l in legions if not l.veteran])
    if not promoted:
        return
    promoted.veteran = True
    promoted.allegiance = commander
    promoted.save()
    log_text = f"Legion {promoted.name} hardened into a Veteran Legion"
    log_text += f", owing allegiance to {commander.display_name}." if commander else "."
    Log.create_object(game_id, log_text)


def _disband(campaign: Campaign) -> None:
    Legion.objects.filter(campaign=campaign).update(campaign=None)
    Fleet.objects.filter(campaign=campaign).update(campaign=None)
    campaign.delete()


def fail_revolt(war: War, kill_primary_rebel: bool) -> None:
    """End a revolt, returning every force to the Senate (1.11.372)."""

    game_id = war.game_id
    primary_rebel = war.primary_rebel

    rebel_campaign = _rebel_campaign(war)
    if rebel_campaign:
        _disband(rebel_campaign)

    # Senate armies that had not achieved a victory return to Rome (1.11.372)
    returning: List[Senator] = []
    for campaign in Campaign.objects.filter(game=game_id, war=war):
        for senator in [campaign.commander, campaign.master_of_horse]:
            if senator and senator.alive:
                senator.location = "Rome"
                senator.save()
                returning.append(senator)
        _disband(campaign)
    war.delete()
    if returning:
        Log.create_object(
            game_id,
            f"{format_list([s.display_name for s in returning])} returned to Rome "
            "now that the revolt is over.",
        )

    rebels = Senator.objects.filter(game=game_id, rebel=True, alive=True)
    if primary_rebel and not kill_primary_rebel:
        rebels = rebels.exclude(id=primary_rebel.id)
    kill_senators(list(rebels), CauseOfDeath.BATTLE)


def resolve_civil_war(
    game_id: int, campaign_id: int, random_resolver: RandomResolver
) -> bool:
    """Fight a battle between a Senate army and the Primary Rebel (1.11.37)."""

    campaign = Campaign.objects.get(game=game_id, id=campaign_id)
    campaign.pending = False
    campaign.imminent = False
    campaign.save()

    war = campaign.war
    commander = campaign.commander
    master_of_horse = campaign.master_of_horse
    if not war or not commander or not war.primary_rebel:
        return False

    rebel = war.primary_rebel
    rebel_campaign = _rebel_campaign(war)
    rebel_master_of_horse = rebel_campaign.master_of_horse if rebel_campaign else None
    rebel_strength = war.land_strength

    senate_legions = list(campaign.legions.all())
    rebel_legions = list(rebel_campaign.legions.all()) if rebel_campaign else []

    game = Game.objects.get(id=game_id)
    land_force = sum(l.strength for l in senate_legions)
    combined_military = commander.military + (
        master_of_horse.military if master_of_horse else 0
    )
    positive_modifier = land_force + min(combined_military, land_force)
    evil_omens_level = game.count_effect(GameEffect.EVIL_OMENS)
    unmodified_result = random_resolver.roll_dice(3)
    modified_result = (
        unmodified_result + positive_modifier - rebel_strength - evil_omens_level
    )
    result = combat_result(modified_result)

    war.fought_land_battle = True
    war.save()

    senate_losses = combat_losses(result, modified_result, len(senate_legions))
    # The Rebel Army suffers no losses in a Senate Defeat (1.11.37)
    rebel_losses = (
        0
        if result == DEFEAT
        else combat_losses(result, modified_result, len(rebel_legions))
    )

    destroyed_senate, surviving_senate = random_resolver.select_casualties(
        senate_legions, senate_losses
    )
    destroyed_rebel, surviving_rebel = random_resolver.select_casualties(
        rebel_legions, rebel_losses
    )
    destroyed = destroyed_senate + destroyed_rebel

    log_text = (
        f"In a civil war battle, {commander.display_name} met with a "
        f"{RESULT_NAMES[result]}."
    )
    for side, lost in [
        ("The Senate", destroyed_senate),
        ("The rebels", destroyed_rebel),
    ]:
        if lost:
            log_text += f" {side} lost {unit_list_to_string(lost, [])}."
    if not destroyed:
        log_text += " No legions were lost."
    if result == VICTORY and game.change_unrest(-1) == -1:
        game.save()
        log_text += " Unrest lowered by 1."
    Log.create_object(game_id, log_text)

    for legion in destroyed:
        legion.delete()

    # Mortality chits are drawn for the Senate's losses alone, but can affect
    # either commander and either Master of Horse (1.10.7)
    codes = {str(c) for c in random_resolver.draw_mortality_chits(senate_losses)}

    def drawn(senator: Optional[Senator]) -> bool:
        if not senator:
            return False
        return get_senator_codes(senator.code)[0] in codes

    commander_killed = drawn(commander)
    master_of_horse_killed = drawn(master_of_horse)
    rebel_killed = drawn(rebel)
    rebel_master_of_horse_killed = drawn(rebel_master_of_horse)

    # A Senate Defeat kills the Senate commander and his Master of Horse (1.11.373)
    if result == DEFEAT:
        commander_killed = True
        master_of_horse_killed = bool(master_of_horse)

    # A commander loses 1 popularity for every 2 legions lost (1.10.61)
    for senator, losses in [(commander, senate_losses), (rebel, rebel_losses)]:
        change = senator.change_popularity(-(losses // 2))
        senator.save()
        if change < 0:
            Log.create_object(
                game_id,
                f"Loss of legions caused {senator.display_name} to lose "
                f"{-change} popularity.",
            )

    # One surviving legion on each winning side hardens into a veteran (1.10.5)
    promotions: List[Tuple[List[Legion], Optional[Senator]]] = []
    if result != DEFEAT:
        promotions.append((surviving_senate, None if commander_killed else commander))
    if result != VICTORY:
        promotions.append((surviving_rebel, None if rebel_killed else rebel))
    for legions, owner in promotions:
        _promote_veteran(legions, owner, random_resolver, game_id)

    # The Senate commander's glory is half the strength he beat (1.11.371)
    if result == VICTORY and not commander_killed:
        glory = (rebel_strength + 1) // 2
        popularity_change = commander.change_popularity(glory)
        commander.influence += glory
        commander.save()
        glory_log_text = (
            f"Victory over the rebels rewards {commander.display_name} with "
            f"{glory} influence"
        )
        if popularity_change > 0:
            glory_log_text += f" and {popularity_change} popularity"
        glory_log_text += "."
        Log.create_object(game_id, glory_log_text)
        campaign.land_victory = True
        campaign.war = None
        campaign.save()

    revolt_failed = result == VICTORY or rebel_killed or not surviving_rebel
    if revolt_failed:
        if result == VICTORY:
            revolt_log_text = f"The revolt of {rebel.display_name} was crushed."
        elif rebel_killed:
            revolt_log_text = f"The revolt died with {rebel.display_name}."
        else:
            revolt_log_text = (
                f"{rebel.display_name} lost the last of his army, and his revolt "
                "with it."
            )
        Log.create_object(game_id, revolt_log_text)

    if revolt_failed:
        fail_revolt(war, kill_primary_rebel=result == VICTORY or rebel_killed)
    elif rebel_master_of_horse and rebel_master_of_horse_killed:
        kill_senators([rebel_master_of_horse], CauseOfDeath.BATTLE)

    casualties: List[Senator] = []
    if commander_killed:
        casualties.append(commander)
    if master_of_horse and master_of_horse_killed:
        casualties.append(master_of_horse)
    if casualties:
        kill_senators(casualties, CauseOfDeath.BATTLE)

    if result == DEFEAT and not revolt_failed:
        # Every surviving Senate army returns to the reserve (1.11.373)
        for senate_campaign in Campaign.objects.filter(game=game_id, war=war):
            _disband(senate_campaign)

    return True
