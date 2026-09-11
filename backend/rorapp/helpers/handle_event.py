from rorapp.classes.concession import Concession
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import RandomResolver
from rorapp.helpers.destroy_concession import destroy_concession
from rorapp.helpers.game_data import get_senator_codes
from rorapp.helpers.kill_senator import CauseOfDeath, kill_senators
from rorapp.helpers.hrao import set_hrao
from rorapp.helpers.storm_at_sea import (
    clear_storm_at_sea_decision,
    destroy_storm_fleets,
)
from rorapp.models import Faction, Fleet, Game, Log, Senator

NATURAL_DISASTER_CONCESSIONS = {
    1: Concession.MINING,
    2: Concession.MINING,
    3: Concession.HARBOR_FEES,
    4: Concession.HARBOR_FEES,
    5: Concession.ARMAMENTS,
    6: Concession.SHIP_BUILDING,
}


def handle_event(
    game: Game,
    current_faction: Faction,
    event_name: str,
    random_resolver: RandomResolver,
) -> bool:
    """Apply the event effect. Returns True if the event is implemented, False if not."""
    if event_name == "Allied enthusiasm":
        advances = handle_allied_enthusiasm(game, current_faction)
    elif event_name == "Drought":
        advances = handle_drought(game, current_faction)
    elif event_name == "Epidemic":
        advances = handle_epidemic(game, current_faction, random_resolver)
    elif event_name == "Evil Omens":
        advances = handle_evil_omens(game, current_faction)
    elif event_name == "Manpower Shortage":
        advances = handle_manpower_shortage(game, current_faction)
    elif event_name == "Natural Disaster":
        advances = handle_natural_disaster(game, current_faction, random_resolver)
    elif event_name == "Storm at Sea":
        advances = handle_storm_at_sea(game, current_faction, random_resolver)
    else:
        return False

    if advances:
        game.sub_phase = Game.SubPhase.PERSUASION_ATTEMPT
        game.save()
    return True


def handle_storm_at_sea(
    game: Game, current_faction: Faction, random_resolver: RandomResolver
) -> bool:
    clear_storm_at_sea_decision(game)
    raw_result = random_resolver.roll_dice(count=2)
    evil_omens = game.count_effect(GameEffect.EVIL_OMENS)
    modified_result = max(0, raw_result - evil_omens)
    fleets = list(Fleet.objects.filter(game=game).order_by("number"))
    fleet_losses = min(modified_result, len(fleets))
    prefix = f"{current_faction.display_name} drew storm at sea."

    if not fleets:
        Log.create_object(game.id, f"{prefix} Rome had no fleets to lose.")
        return True

    if fleet_losses == 0:
        Log.create_object(game.id, f"{prefix} No fleets were lost.")
        return True

    if fleet_losses == len(fleets):
        elimination_text = (
            "The only existing Roman fleet must be eliminated."
            if fleet_losses == 1
            else f"All {fleet_losses} existing Roman fleets must be eliminated."
        )
        Log.create_object(
            game.id,
            f"{prefix} {elimination_text}",
        )
        destroy_storm_fleets(game, fleets)
        return True

    set_hrao(game.id)
    hrao = Senator.objects.filter(
        game=game,
        alive=True,
        location="Rome",
        faction__isnull=False,
        titles__contains=[Senator.Title.HRAO.value],
    ).first()
    if hrao is None or hrao.faction_id is None:
        raise RuntimeError("Storm at sea cannot be resolved without an HRAO faction.")

    factions = list(Faction.objects.filter(game=game))
    for faction in factions:
        faction.remove_status_item(FactionStatusItem.AWAITING_DECISION)
        if faction.id == hrao.faction_id:
            faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
    Faction.objects.bulk_update(factions, ["status_items"])

    game.storm_at_sea_fleet_losses = fleet_losses
    game.sub_phase = Game.SubPhase.STORM_AT_SEA
    game.save()
    fleet_noun = "fleet" if fleet_losses == 1 else "fleets"
    Log.create_object(
        game.id,
        f"{prefix} The HRAO must choose {fleet_losses} Roman {fleet_noun} to eliminate.",
    )
    return False


def handle_evil_omens(game: Game, current_faction: Faction) -> bool:
    level = game.count_effect(GameEffect.EVIL_OMENS)
    if level == 0:
        game.state_treasury -= 20
    game.add_effect(GameEffect.EVIL_OMENS)
    game.save()

    prefix = f"{current_faction.display_name} drew evil omens."
    if level == 0:
        Log.create_object(
            game.id,
            f"{prefix} The State paid 20T for sacrifices and temple repair. The omens make military campaigns more perilous and senators more susceptible to persuasion.",
        )
    else:
        Log.create_object(
            game.id,
            f"{prefix} With Rome already afflicted by evil omens, further omens make military campaigns even more perilous and senators even more susceptible to persuasion.",
        )
    return True


def handle_drought(game: Game, current_faction: Faction) -> bool:
    level = game.count_effect(GameEffect.DROUGHT)
    game.add_effect(GameEffect.DROUGHT)
    game.save()

    prefix = f"{current_faction.display_name} drew drought."
    if level == 0:
        Log.create_object(
            game.id,
            f"{prefix} Famine severity has increased.",
        )
    elif level == 1:
        Log.create_object(
            game.id,
            f"{prefix} Drought conditions have worsened to a severe drought, increasing famine severity further.",
        )
    else:
        Log.create_object(
            game.id,
            f"{prefix} The severe drought has worsened, increasing famine severity further.",
        )
    return True


def handle_manpower_shortage(game: Game, current_faction: Faction) -> bool:
    level = game.count_effect(GameEffect.MANPOWER_SHORTAGE)
    game.add_effect(GameEffect.MANPOWER_SHORTAGE)
    game.save()

    prefix = f"{current_faction.display_name} drew manpower shortage."
    if level == 0:
        Log.create_object(
            game.id,
            f"{prefix} Recruitment costs have increased to 20T per unit.",
        )
    else:
        cost = 10 * (level + 2)
        Log.create_object(
            game.id,
            f"{prefix} The manpower shortage has worsened, increasing recruitment costs to {cost}T per unit.",
        )
    return True


def handle_allied_enthusiasm(game: Game, current_faction: Faction) -> bool:
    level = game.count_effect(GameEffect.ALLIED_ENTHUSIASM)

    if level < 2:
        game.add_effect(GameEffect.ALLIED_ENTHUSIASM)
        game.save()

    prefix = f"{current_faction.display_name} drew allied enthusiasm."
    if level == 0:
        Log.create_object(
            game.id,
            f"{prefix} With Rome's allies contributing additional funds, the State will receive 50T in the next revenue phase.",
        )
    elif level == 1:
        Log.create_object(
            game.id,
            f"{prefix} With Rome's allies already enthusiastic, they are now extremely enthusiastic. The State will receive 75T in the next revenue phase.",
        )
    else:
        Log.create_object(
            game.id,
            f"{prefix} Rome's allies are already extremely enthusiastic so there is no additional effect.",
        )
    return True


def handle_epidemic(
    game: Game, current_faction: Faction, random_resolver: RandomResolver
) -> bool:
    codes = set(random_resolver.draw_mortality_chits(6))
    senators = Senator.objects.filter(game=game.id, alive=True)
    victims = [
        s
        for s in senators
        if s.location == "Rome" and get_senator_codes(s.code)[0] in codes
    ]

    prefix = f"{current_faction.display_name} drew epidemic."
    if victims:
        Log.create_object(
            game.id,
            f"{prefix} A plague swept through Rome.",
        )
    else:
        Log.create_object(
            game.id,
            f"{prefix} A plague swept through Rome, but every senator survived.",
        )

    kill_senators(victims, CauseOfDeath.EPIDEMIC)

    # Reload the game, since deaths may have released concessions to the forum
    game.refresh_from_db()
    return True


def handle_natural_disaster(
    game: Game, current_faction: Faction, random_resolver: RandomResolver
) -> bool:
    level = game.count_effect(GameEffect.NATURAL_DISASTER)

    if level == 0:
        game.state_treasury -= 50
    game.add_effect(GameEffect.NATURAL_DISASTER)
    game.save()

    prefix = f"{current_faction.display_name} drew natural disaster."
    if level == 0:
        Log.create_object(
            game.id,
            f"{prefix} The State paid 50T for relief.",
        )
    else:
        Log.create_object(
            game.id,
            f"{prefix} The disaster has spread.",
        )

    # Evil omens do not modify the roll for which concession is struck (1.07.21)
    concession = NATURAL_DISASTER_CONCESSIONS[random_resolver.roll_dice()]
    destroyed, holder = destroy_concession(game, concession)

    if destroyed:
        if holder:
            Log.create_object(
                game.id,
                f"The {concession.value} concession held by {holder.display_name} was destroyed.",
            )
        else:
            Log.create_object(
                game.id,
                f"The unawarded {concession.value} concession was destroyed.",
            )

    return True
