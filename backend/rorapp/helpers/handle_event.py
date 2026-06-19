from rorapp.classes.game_effect_item import GameEffect
from rorapp.models import Game, Log


def handle_event(
    game: Game, game_id: int, faction_display_name: str, event_name: str
) -> bool:
    """Apply the event effect. Returns True if the event is implemented, False if not."""
    if event_name == "Allied enthusiasm":
        level = game.count_effect(GameEffect.ALLIED_ENTHUSIASM)
        if level < 2:
            game.add_effect(GameEffect.ALLIED_ENTHUSIASM)
            new_level = game.count_effect(GameEffect.ALLIED_ENTHUSIASM)
            card_name = (
                "allied enthusiasm" if new_level == 1 else "extreme allied enthusiasm"
            )
            bonus = 50 if new_level == 1 else 75
            Log.create_object(
                game_id,
                f"{faction_display_name} drew {card_name}. The State will receive {bonus}T in the next revenue phase.",
            )
        return True
    return False
