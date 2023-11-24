from typing import List
from rorapp.functions.websocket_message_helper import (
    create_websocket_message,
)
from rorapp.models import (
    Action,
    Faction,
    Game,
    Phase,
    Step,
    Turn,
)
from rorapp.serializers import (
    ActionSerializer,
    StepSerializer,
    PhaseSerializer,
)


def setup_mortality_phase(game_id: int) -> List[dict]:
    """
    Setup the mortality phase.

    Includes creation of a new step, phase, and actions for each faction.

    Args:
        game_id (int): The game ID.

    Returns:
        List[dict]: The list of WebSocket messages to send.
    """

    messages_to_send = []
    game = Game.objects.get(id=game_id)
    latest_step = Step.objects.filter(phase__turn__game=game).order_by("-index")[0]
    turn = Turn.objects.get(id=latest_step.phase.turn.id)
    new_phase = Phase(name="Mortality", index=1, turn=turn)
    new_phase.save()
    messages_to_send.append(
        create_websocket_message("phase", PhaseSerializer(new_phase).data)
    )

    new_step = Step(index=latest_step.index + 1, phase=new_phase)
    new_step.save()
    messages_to_send.append(
        create_websocket_message("step", StepSerializer(new_step).data)
    )

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
