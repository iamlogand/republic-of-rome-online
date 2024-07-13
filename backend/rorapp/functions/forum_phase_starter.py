from rorapp.functions.action_helper import delete_old_actions
from rorapp.functions.forum_phase_helper import generate_initiate_situation_action
from rorapp.functions.progress_helper import create_phase_and_message
from rorapp.models import Faction


def start_forum_phase(game_id: int) -> list[dict]:
    """
    Start the forum phase.

    Args:
        game_id (int): The game ID.

    Returns:
        list[dict]: The WebSocket messages to send.
    """
    messages_to_send = []

    # Progress to the forum phase
    _, phase_message = create_phase_and_message(game_id, "Forum")
    messages_to_send.append(phase_message)

    # Create action and new step
    first_faction = Faction.objects.filter(game__id=game_id).order_by("rank").first()
    assert isinstance(first_faction, Faction)
    messages_to_send.extend(generate_initiate_situation_action(first_faction))
    messages_to_send.extend(delete_old_actions(game_id))
    return messages_to_send
