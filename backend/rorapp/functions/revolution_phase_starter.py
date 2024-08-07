from typing import List
from rorapp.functions.progress_helper import create_phase_and_message
from rorapp.functions.concession_helper import generate_assign_concessions_action


def start_revolution_phase(game_id: int) -> List[dict]:
    messages_to_send = []

    # Progress to the revolution phase
    _, phase_message = create_phase_and_message(game_id, "Revolution")
    messages_to_send.append(phase_message)
    messages_to_send.extend(generate_assign_concessions_action(game_id))

    return messages_to_send
