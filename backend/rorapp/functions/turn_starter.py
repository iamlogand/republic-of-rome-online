from rorapp.functions.websocket_message_helper import create_websocket_message
from rorapp.models import Faction, Action, Step, Phase, Turn, ActionLog
from rorapp.serializers import (
    ActionLogSerializer,
    ActionSerializer,
    StepSerializer,
    PhaseSerializer,
    TurnSerializer,
)


def start_next_turn(game, step) -> [dict]:
    """
    Start the next turn
    """

    messages_to_send = []

    # Create the next turn
    turn = Turn.objects.get(id=step.phase.turn.id)
    new_turn = Turn(index=turn.index + 1, game=game)
    new_turn.save()
    messages_to_send.append(create_websocket_message("turn", TurnSerializer(new_turn).data))

    # Create the mortality phase
    new_phase = Phase(name="Mortality", index=0, turn=new_turn)
    new_phase.save()
    messages_to_send.append(create_websocket_message("phase", PhaseSerializer(new_phase).data))

    # Create a new step in the mortality phase
    new_step = Step(index=step.index + 1, phase=new_phase)
    new_step.save()
    messages_to_send.append(create_websocket_message("step", StepSerializer(new_step).data))

    # Issue a notification to say that the next turn has started
    new_action_log_index = (
        ActionLog.objects.filter(step__phase__turn__game=game)
        .order_by("-index")[0]
        .index
        + 1
    )
    action_log = ActionLog(
        index=new_action_log_index,
        step=step,
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
