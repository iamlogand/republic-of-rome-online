from typing import List
from rorapp.functions.chromatic_order_helper import get_next_faction_in_chromatic_order
from rorapp.functions.progress_helper import create_step_and_message
from rorapp.functions.websocket_message_helper import create_websocket_message
from rorapp.functions.turn_starter import start_next_turn
from rorapp.models import Action, Faction, Secret, Senator
from rorapp.serializers import ActionSerializer


def generate_assign_concessions_action(
    game_id: int, faction: Faction | None
) -> List[dict]:
    messages_to_send = []

    if faction is None:
        messages_to_send.extend(start_next_turn(game_id))
        return messages_to_send

    faction_secrets = Secret.objects.filter(faction=faction)

    if faction_secrets.count() == 0:
        next_faction = get_next_faction_in_chromatic_order(faction)
        if isinstance(next_faction, Faction):
            messages_to_send.extend(
                generate_assign_concessions_action(game_id, next_faction)
            )
        else:
            messages_to_send.extend(start_next_turn(faction.game.id))
        return messages_to_send

    # Create step
    step, step_message = create_step_and_message(game_id)
    messages_to_send.append(step_message)

    # Generate action for assigning concessions
    senators = Senator.objects.filter(faction=faction, alive=True)
    senator_id_list = [senator.id for senator in senators]
    concession_secrets = faction_secrets.filter(type="concession").exclude(
        name="Land Commissioner"
    )
    concession_secret_id_list = [concession.id for concession in concession_secrets]
    action = Action(
        step=step,
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
