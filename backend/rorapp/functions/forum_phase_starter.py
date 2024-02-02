from typing import List
from rorapp.functions.action_helper import delete_old_actions
from rorapp.functions.forum_phase_helper import generate_initiate_situation_action
from rorapp.functions.websocket_message_helper import create_websocket_message
from rorapp.models import (
    Faction,
    Phase,
    Step,
)
from rorapp.serializers import PhaseSerializer


def start_forum_phase(game_id: int) -> List[dict]:
    """
    Start the forum phase.

    Args:
        game_id (int): The game ID.

    Returns:
        List[dict]: The WebSocket messages to send.
    """
    messages_to_send = []
    latest_step = Step.objects.filter(phase__turn__game=game_id).order_by("-index")[0]

    # Progress to the forum phase
    new_phase = Phase(
        name="Forum", index=latest_step.phase.index + 1, turn=latest_step.phase.turn
    )
    new_phase.save()
    messages_to_send.append(
        create_websocket_message("phase", PhaseSerializer(new_phase).data)
    )

    # Create action and new step
    first_faction = Faction.objects.filter(game__id=game_id).order_by("rank").first()
    messages_to_send.extend(generate_initiate_situation_action(first_faction))
    messages_to_send.extend(delete_old_actions(game_id))
    return messages_to_send
