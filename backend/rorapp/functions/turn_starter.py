from typing import List
from rorapp.functions.progress_helper import get_latest_step
from rorapp.functions.websocket_message_helper import create_websocket_message
from rorapp.models import Faction, Action, Step, Phase, Game, Turn, ActionLog
from rorapp.serializers import (
    ActionLogSerializer,
    ActionSerializer,
    StepSerializer,
    PhaseSerializer,
    TurnSerializer,
)


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
    game = Game.objects.get(id=game_id)
    new_turn = Turn(index=turn.index + 1, game=game)
    new_turn.save()
    messages_to_send.append(
        create_websocket_message("turn", TurnSerializer(new_turn).data)
    )

    # Create the mortality phase
    new_phase = Phase(name="Mortality", index=0, turn=new_turn)
    new_phase.save()
    messages_to_send.append(
        create_websocket_message("phase", PhaseSerializer(new_phase).data)
    )

    # Create a new step in the mortality phase
    last_step = get_latest_step(game_id)
    new_step = Step(index=last_step.index + 1, phase=new_phase)
    new_step.save()
    messages_to_send.append(
        create_websocket_message("step", StepSerializer(new_step).data)
    )

    # Issue a notification to say that the next turn has started
    new_action_log_index = (
        ActionLog.objects.filter(step__phase__turn__game=game)
        .order_by("-index")[0]
        .index
        + 1
    )
    action_log = ActionLog(
        index=new_action_log_index,
        step=new_step,
        type="new_turn",
        data={"turn_index": new_turn.index},
    )
    action_log.save()
    messages_to_send.append(
        create_websocket_message("action_log", ActionLogSerializer(action_log).data)
    )

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
