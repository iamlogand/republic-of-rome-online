from rorapp.classes.concession import Concession
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import RandomResolver
from rorapp.helpers.destroy_concession import destroy_concession
from rorapp.helpers.game_data import get_senator_codes
from rorapp.helpers.kill_senator import CauseOfDeath, kill_senators
from rorapp.helpers.rhodian_alliance import RHODIAN_FLEETS
from rorapp.helpers.storm_at_sea import destroy_storm_fleets
from rorapp.helpers.text import pluralize
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import Faction, Fleet, Game, Log, Senator, War

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
    if event_name == "Ally deserts":
        advances = handle_ally_deserts(game, current_faction)
    elif event_name == "Allied enthusiasm":
        advances = handle_allied_enthusiasm(game, current_faction)
    elif event_name == "Drought":
        advances = handle_drought(game, current_faction)
    elif event_name == "Enemy's ally deserts":
        advances = handle_enemys_ally_deserts(game, current_faction)
    elif event_name == "Epidemic":
        advances = handle_epidemic(game, current_faction, random_resolver)
    elif event_name == "Evil omens":
        advances = handle_evil_omens(game, current_faction)
    elif event_name == "Manpower shortage":
        advances = handle_manpower_shortage(game, current_faction)
    elif event_name == "Natural disaster":
        advances = handle_natural_disaster(game, current_faction, random_resolver)
    elif event_name == "Rhodian alliance":
        advances = handle_rhodian_alliance(game, current_faction)
    elif event_name == "Storm at sea":
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
    raw_result = random_resolver.roll_dice(count=2)
    evil_omens = game.count_effect(GameEffect.EVIL_OMENS)
    modified_result = max(0, raw_result - evil_omens)
    fleets = list(Fleet.objects.filter(game=game).order_by("number"))
    fleet_losses = min(modified_result, len(fleets))
    prefix = f"{current_faction.display_name} drew storm at sea."

    if fleet_losses == 0:
        Log.create_object(game.id, f"{prefix} No fleets were lost.")
        return True

    if fleet_losses == len(fleets):
        Log.create_object(game.id, prefix)
        destroy_storm_fleets(game, fleets)
        return True

    hrao = Senator.objects.select_related("faction").get(
        game=game,
        alive=True,
        location="Rome",
        faction__isnull=False,
        titles__contains=[Senator.Title.HRAO.value],
    )
    hrao_faction = hrao.faction
    assert hrao_faction is not None
    hrao_faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
    hrao_faction.save(update_fields=["status_items"])

    game.storm_at_sea_fleet_losses = fleet_losses
    game.sub_phase = Game.SubPhase.STORM_AT_SEA
    game.save()
    Log.create_object(
        game.id,
        f"{prefix} The HRAO must choose {pluralize(fleet_losses, 'Roman fleet')} to eliminate.",
    )
    return False


def handle_rhodian_alliance(game: Game, current_faction: Faction) -> bool:
    level = game.count_effect(GameEffect.RHODIAN_ALLIANCE)
    prefix = f"{current_faction.display_name} drew Rhodian maritime alliance."

    if level == 2:
        Log.create_object(
            game.id,
            f"{prefix} Rhodes is already fully committed, so there is no additional effect.",
        )
        return True

    if level == 0:
        wars = [
            w
            for w in War.objects.filter(game=game).exclude(status=War.Status.DEFEATED)
            if w.fleet_support + w.naval_strength > 0
        ]
        if not wars:
            Log.create_object(
                game.id, f"{prefix} With no war requiring fleets, Rhodes sent none."
            )
            return True

        # Defeating any one of the Wars tied for the most Fleets ends the alliance (1.07.21)
        most = max(w.fleet_support + w.naval_strength for w in wars)
        War.objects.filter(
            id__in=[w.id for w in wars if w.fleet_support + w.naval_strength == most]
        ).update(rhodian_alliance=True)

    # The fleets count towards the 25 fleet limit (1.07.21)
    taken = set(Fleet.objects.filter(game=game).values_list("number", flat=True))
    numbers = [n for n in range(1, 26) if n not in taken]
    count = RHODIAN_FLEETS[level + 1] - RHODIAN_FLEETS.get(level, 0)
    fleets = [
        Fleet.objects.create(game=game, number=n, recently_raised=False)
        for n in numbers[:count]
    ]

    game.add_effect(GameEffect.RHODIAN_ALLIANCE)
    game.rhodian_alliance_rejectable = True
    game.save()

    wars_text = " or ".join(
        f"the {w.name}"
        for w in War.objects.filter(game=game, rhodian_alliance=True).order_by("id")
    )
    units = unit_list_to_string([], fleets)
    if not fleets:
        lent = "The State already has 25 fleets, so Rhodes lent none."
    elif level == 0:
        lent = f"Rhodes lent the State {units} until {wars_text} is defeated."
    else:
        lent = f"Rhodes increased its involvement, lending the State another {units} until {wars_text} is defeated."
    Log.create_object(game.id, f"{prefix} {lent}")
    return True


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


def handle_ally_deserts(game: Game, current_faction: Faction) -> bool:
    level = game.count_effect(GameEffect.ALLIED_DESERTION)

    if level < 2:
        game.add_effect(GameEffect.ALLIED_DESERTION)
        game.save()

    prefix = f"{current_faction.display_name} drew allied desertion."
    if level == 0:
        Log.create_object(
            game.id,
            f"{prefix} Rome's allies are wavering, so the enemy may be strengthened in battle.",
        )
    elif level == 1:
        Log.create_object(
            game.id,
            f"{prefix} With Rome's allies already wavering, Roman troops are shaken too, so the enemy may be strengthened further in battle.",
        )
    else:
        Log.create_object(
            game.id,
            f"{prefix} Rome's allies are already wavering so there is no additional effect.",
        )
    return True


def handle_enemys_ally_deserts(game: Game, current_faction: Faction) -> bool:
    level = game.count_effect(GameEffect.ENEMY_DESERTION)

    if level < 2:
        game.add_effect(GameEffect.ENEMY_DESERTION)
        game.save()

    prefix = f"{current_faction.display_name} drew enemy desertion."
    if level == 0:
        Log.create_object(
            game.id,
            f"{prefix} Enemy allies are wavering, so the enemy may be weakened in battle.",
        )
    elif level == 1:
        Log.create_object(
            game.id,
            f"{prefix} With the enemy's allies already wavering, their mercenaries are deserting too, so the enemy may be weakened further in battle.",
        )
    else:
        Log.create_object(
            game.id,
            f"{prefix} Enemy allies are already wavering so there is no additional effect.",
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
