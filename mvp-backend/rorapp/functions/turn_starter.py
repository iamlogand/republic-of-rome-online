from typing import List
from rorapp.functions.progress_helper import (
    create_phase_and_message,
    create_step_and_message,
)
from rorapp.functions.websocket_message_helper import create_websocket_message
from rorapp.models import Faction, Action, Game, Turn
from rorapp.serializers import ActionSerializer, TurnSerializer


def start_next_turn(game_id) -> List[dict]:
    """
    Start the next turn

    Args:
        game_id (int): The game ID.
        step (Step): The step that the turn is being started from.

    Returns:
        List[dict]: A list of websocket messages to send.
    """

    messages_to_send = []

    # Create the next turn
    turn = Turn.objects.filter(game__id=game_id).order_by("-index").first()
    assert isinstance(turn, Turn)
    game = Game.objects.get(id=game_id)
    new_turn = Turn(index=turn.index + 1, game=game)
    new_turn.save()
    messages_to_send.append(
        create_websocket_message("turn", TurnSerializer(new_turn).data)
    )

    # Create the mortality phase
    _, phase_message = create_phase_and_message(game_id, "Mortality")
    messages_to_send.append(phase_message)

    # Create a new step in the mortality phase
    new_step, step_message = create_step_and_message(game_id)
    messages_to_send.append(step_message)

    # Create actions for next mortality phase
    factions = Faction.objects.filter(game__id=game.id)
    for faction in factions:
        action = Action(
            step=new_step,
            faction=faction,
            type="face_mortality",
            required=True,
            parameters=None,
        )
        action.save()
        messages_to_send.append(
            create_websocket_message("action", ActionSerializer(action).data)
        )

    return messages_to_send
