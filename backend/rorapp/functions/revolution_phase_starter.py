from typing import List

from rorapp.functions.progress_helper import get_latest_step
from rorapp.functions.revolution_phase_helper import generate_assign_concessions_action
from rorapp.functions.websocket_message_helper import create_websocket_message
from rorapp.models import Faction, Phase
from rorapp.serializers import PhaseSerializer


def start_revolution_phase(game_id: int) -> List[dict]:
    messages_to_send = []

    # Progress to the revolution phase
    latest_step = get_latest_step(game_id)
    new_phase = Phase(
        name="Revolution",
        index=latest_step.phase.index + 1,
        turn=latest_step.phase.turn,
    )
    new_phase.save()
    messages_to_send.append(
        create_websocket_message("phase", PhaseSerializer(new_phase).data)
    )

    first_faction = Faction.objects.filter(game__id=game_id).order_by("rank").first()
    messages_to_send.extend(generate_assign_concessions_action(first_faction))

    return messages_to_send



