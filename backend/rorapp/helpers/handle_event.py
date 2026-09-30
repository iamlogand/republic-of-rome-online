from rorapp.classes.concession import Concession
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import RandomResolver
from rorapp.helpers.destroy_concession import destroy_concession
from rorapp.helpers.game_data import get_senator_codes
from rorapp.helpers.kill_senator import CauseOfDeath, kill_senators
from rorapp.helpers.storm_at_sea import destroy_storm_fleets
from rorapp.helpers.text import format_list, pluralize, to_sentence_case
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
    if event_name == "Ally deserts":
        advances = handle_ally_deserts(game, current_faction)
    elif event_name == "Allied enthusiasm":
        advances = handle_allied_enthusiasm(game, current_faction)
    elif event_name == "Drought":
        advances = handle_drought(game, current_faction)
    elif event_name == "Enemy leader dies":
        advances = handle_enemy_leader_dies(game, current_faction)
    elif event_name == "Enemy's ally deserts":
        advances = handle_enemys_ally_deserts(game, current_faction)
    elif event_name == "Epidemic":
        advances = handle_epidemic(game, current_faction, random_resolver)
    elif event_name == "Evil omens":
        advances = handle_evil_omens(game, current_faction)
    elif event_name == "Manpower shortage":
        advances = handle_manpower_shortage(game, current_faction)
    elif event_name == "Mob violence":
        advances = handle_mob_violence(game, current_faction, random_resolver)
    elif event_name == "Natural disaster":
        advances = handle_natural_disaster(game, current_faction, random_resolver)
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


def handle_enemy_leader_dies(game: Game, current_faction: Faction) -> bool:
    level = game.count_effect(GameEffect.ENEMY_LEADER_DIES)

    if level < 2:
        game.add_effect(GameEffect.ENEMY_LEADER_DIES)
        game.save()

    prefix = f"{current_faction.display_name} drew enemy leader dies."
    if level == 0:
        Log.create_object(
            game.id,
            f"{prefix} At the end of the forum phase, the HRAO will choose an enemy leader to die.",
        )
    elif level == 1:
        Log.create_object(
            game.id,
            f"{prefix} Disheartened by the loss of their leader, the enemy will also sue for peace in that leader's largest war.",
        )
    else:
        Log.create_object(
            game.id,
            f"{prefix} The enemy is already suing for peace so there is no additional effect.",
        )
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


def handle_mob_violence(
    game: Game, current_faction: Faction, random_resolver: RandomResolver
) -> bool:
    level = game.count_effect(GameEffect.MOB_VIOLENCE)
    unrest = game.unrest
    chit_count = unrest
    threshold = unrest

    if level > 0:
        # More mob violence draws extra chits and puts one more rank of
        # popularity at risk, and every later draw is resolved as more mob
        # violence (1.07.21)
        evil_omens_level = game.count_effect(GameEffect.EVIL_OMENS)
        chit_count += max(0, random_resolver.roll_dice() - evil_omens_level)
        threshold = unrest + 1

    game.add_effect(GameEffect.MOB_VIOLENCE)
    game.save()

    codes = set(random_resolver.draw_mortality_chits(chit_count))

    senators = Senator.objects.filter(
        game=game.id, alive=True, location="Rome"
    ).select_related("faction")
    caught = [s for s in senators if get_senator_codes(s.code)[0] in codes]

    # Only senators less popular than the threshold are at risk, however many
    # chits are drawn (1.07.21)
    victims = [s for s in caught if s.popularity < threshold]
    spared = [s for s in caught if s.popularity >= threshold]

    prefix = f"{current_faction.display_name} drew mob violence."
    if chit_count == 0:
        message = f"{prefix} Due to low unrest, the mob dispersed without violence."
    elif caught:
        message = f"{prefix} An outraged mob rioted in Rome."
    else:
        message = f"{prefix} An outraged mob rioted in Rome, but every senator survived."

    Log.create_object(game.id, message)

    kill_senators(victims, CauseOfDeath.MOB)

    if spared:
        names = to_sentence_case(
            format_list([s.display_name_with_faction for s in spared])
        )
        verb = "was" if len(spared) == 1 else "were"
        pronoun = "his" if len(spared) == 1 else "their"
        Log.create_object(
            game.id,
            f"{names} {verb} caught by the mob but quickly released thanks to {pronoun} popularity.",
        )

    # Reload the game, since deaths may have released concessions to the forum
    game.refresh_from_db()
    return True
