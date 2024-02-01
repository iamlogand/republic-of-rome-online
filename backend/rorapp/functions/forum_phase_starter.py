from typing import List
from rorapp.functions.action_helper import delete_old_actions
from rorapp.functions.faction_leader_helper import generate_select_faction_leader_action
from rorapp.functions.websocket_message_helper import create_websocket_message
from rorapp.models import (
    Faction,
    Phase,
    Step,
)
from rorapp.serializers import (
    StepSerializer,
    PhaseSerializer,
)


def start_forum_phase(game_id) -> List[dict]:
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
    new_step = Step(index=latest_step.index + 1, phase=new_phase)
    new_step.save()
    messages_to_send.append(
        create_websocket_message("step", StepSerializer(new_step).data)
    )

    # Create actions
    first_faction = Faction.objects.filter(game__id=game_id).order_by("rank").first()
    messages_to_send.append(
        generate_select_faction_leader_action(first_faction, new_step)
    )
    messages_to_send.extend(delete_old_actions(game_id))
    return messages_to_send
