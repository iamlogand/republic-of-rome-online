from typing import List
from rorapp.functions.progress_helper import create_phase_and_message
from rorapp.functions.concession_helper import generate_assign_concessions_action
from rorapp.models import Faction


def start_revolution_phase(game_id: int) -> List[dict]:
    messages_to_send = []

    # Progress to the revolution phase
    _, phase_message = create_phase_and_message(game_id, "Revolution")
    messages_to_send.append(phase_message)

    first_faction = Faction.objects.filter(game__id=game_id).order_by("rank").first()
    assert isinstance(first_faction, Faction)
    messages_to_send.extend(generate_assign_concessions_action(game_id, first_faction))

    return messages_to_send
