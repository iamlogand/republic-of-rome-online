import json
from typing import Tuple
from rest_framework.response import Response
from rorapp.functions.action_helper import delete_old_actions
from rorapp.functions.chromatic_order_helper import get_next_faction_in_chromatic_order
from rorapp.functions.progress_helper import (
    create_new_step_and_message,
    get_latest_phase,
    get_latest_step,
)
from rorapp.functions.revolution_phase_starter import generate_assign_concessions_action
from rorapp.functions.turn_starter import start_next_turn
from rorapp.functions.websocket_message_helper import create_websocket_message, destroy_websocket_message
from rorapp.models import Action, ActionLog, Faction, Senator, Secret, Step
from rorapp.serializers.action_log import ActionLogSerializer
from rorapp.serializers.step import StepSerializer


def assign_concessions(action_id: int, data: dict) -> Tuple[Response, dict]:
    """
    Assign concessions to senators.

    This function is called when a player reveals their concession secrets to assign the concessions to senators.
    Requires data to contain a secret_senator_map JSON object that maps concession secret IDs to senator IDs.

    Args:
        action_id (int): The action ID.

    Returns:
        Response: The response with a message and a status code.
    """

    messages_to_send = []

    # The action and faction IDs are known to be valid
    action = Action.objects.get(id=action_id)
    faction = Faction.objects.get(id=action.faction.id)

    # Try to get the secret_senator_map data
    try:
        secret_senator_map = data.get("secret_senator_map")
    except KeyError:
        return Response({"message": "secret_senator_map must be provided"}, status=400)

    # Try to parse the secret_senator_map JSON
    try:
        secret_senator_map_json = json.loads(secret_senator_map)
    except json.JSONDecodeError:
        return Response(
            {"message": "Invalid JSON format in secret_senator_map"}, status=400
        )
    if len(secret_senator_map_json) > 0:
        for secret_id, senator_id in secret_senator_map_json.items():
            if senator_id is not None:
                # Try to parse the secret and senator IDs into integers
                try:
                    parsed_secret_id = int(secret_id)
                except ValueError:
                    return Response({"message": "Secret ID must be an integer"}, status=400)
                try:
                    parsed_senator_id = int(senator_id)
                except ValueError:
                    return Response(
                        {"message": "Senator ID must be an integer"}, status=400
                    )

                # Try to get the secret
                try:
                    secret = Secret.objects.filter(faction=faction, type="concession").get(
                        id=parsed_secret_id
                    )
                except Secret.DoesNotExist:
                    return Response(
                        {"message": "Selected secret was not found"}, status=404
                    )

                # Try to get the senator
                try:
                    senator: Senator = Senator.objects.filter(faction=faction).get(
                        id=parsed_senator_id
                    )
                except Senator.DoesNotExist:
                    return Response(
                        {"message": "Selected senator was not found"}, status=404
                    )

                # Assign the concession to the senator
                messages_to_send.extend(assign_concession(faction, secret, senator))

    # Delete old actions
    messages_to_send.extend(delete_old_actions(faction.game.id))

    # Proceed to next turn or next faction
    next_faction = get_next_faction_in_chromatic_order(faction)
    if next_faction is None:
        messages_to_send.extend(start_next_turn(faction.game.id))
    else:
        messages_to_send.extend(generate_assign_concessions_action(next_faction))

    return Response(
        {"message": "Concession assignment completed"}, status=200
    ), messages_to_send


def assign_concession(
    faction: Faction, secret: Secret, senator: Senator | None
) -> Tuple[Response, dict]:
    messages_to_send = []

    # Delete secret
    messages_to_send.append(
        destroy_websocket_message("secret", secret.id)
    )
    secret.delete()

    # TODO: Create concession
    

    return messages_to_send
