from rorapp.classes.game_effect_item import GameEffect
from rorapp.models import Faction, Game, Log


def handle_event(game: Game, current_faction: Faction, event_name: str) -> bool:
    """Apply the event effect. Returns True if the event is implemented, False if not."""
    if event_name == "Allied enthusiasm":
        advances = handle_allied_enthusiasm(game, current_faction)
    elif event_name == "Drought":
        advances = handle_drought(game, current_faction)
    else:
        return False

    if advances:
        game.sub_phase = Game.SubPhase.PERSUASION_ATTEMPT
        game.save()
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
