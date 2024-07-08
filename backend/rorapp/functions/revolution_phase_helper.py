from typing import List

from rorapp.functions.chromatic_order_helper import get_next_faction_in_chromatic_order
from rorapp.functions.progress_helper import get_latest_phase, get_latest_step
from rorapp.functions.websocket_message_helper import create_websocket_message
from rorapp.models import Action, Faction, Secret, Senator, Step
from rorapp.serializers import ActionSerializer, StepSerializer


def generate_assign_concessions_action(faction: Faction) -> List[dict]:
    messages_to_send = []

    faction_secrets = Secret.objects.filter(faction=faction)

    latest_step = get_latest_step(faction.game.id)
    # Need to get latest phase because the latest step might not be from the current revolution phase
    latest_phase = get_latest_phase(faction.game.id)
    new_step = Step(index=latest_step.index + 1, phase=latest_phase)
    new_step.save()
    messages_to_send.append(
        create_websocket_message("step", StepSerializer(new_step).data)
    )

    if faction_secrets.count() == 0:
        next_faction = get_next_faction_in_chromatic_order(faction)
        messages_to_send.extend(generate_assign_concessions_action(next_faction))
    else:
        senators = Senator.objects.filter(faction=faction, alive=True)
        senator_id_list = [senator.id for senator in senators]
        concession_secrets = faction_secrets.filter(type="concession").exclude(name="Land Commissioner")
        concession_secret_id_list = [concession.id for concession in concession_secrets]
        action = Action(
            step=new_step,
            faction=faction,
            type="assign_concessions",
            required=True,
            parameters={
                "senators": senator_id_list,
                "concession_secrets": concession_secret_id_list,
            },
        )
        action.save()
        messages_to_send.append(
            create_websocket_message("action", ActionSerializer(action).data)
        )

    return messages_to_send
