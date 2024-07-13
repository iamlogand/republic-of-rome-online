from rorapp.models import Action, Faction
from rorapp.serializers import ActionSerializer
from rorapp.functions.progress_helper import (
    create_phase_and_message,
    create_step_and_message,
)
from rorapp.functions.websocket_message_helper import (
    create_websocket_message,
)


def setup_mortality_phase(game_id: int) -> list[dict]:
    """
    Setup the mortality phase.

    Includes creation of a new step, phase, and actions for each faction.

    Args:
        game_id (int): The game ID.

    Returns:
        list[dict]: The list of WebSocket messages to send.
    """

    messages_to_send = []
    _, phase_message = create_phase_and_message(game_id, "Mortality")
    messages_to_send.append(phase_message)
    step, step_messages = create_step_and_message(game_id)
    messages_to_send.append(step_messages)

    factions = Faction.objects.filter(game__id=game_id)
    for faction in factions:
        action = Action(
            step=step,
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
