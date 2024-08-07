import json
from typing import List
from rest_framework.response import Response
from rorapp.functions.action_helper import delete_all_actions
from rorapp.functions.chromatic_order_helper import get_next_faction_in_chromatic_order
from rorapp.functions.mortality_phase_starter import setup_mortality_phase
from rorapp.functions.progress_helper import (
    create_step_and_message,
    get_phase,
    get_step,
)
from rorapp.functions.turn_starter import start_next_turn
from rorapp.functions.websocket_message_helper import (
    create_websocket_message,
    destroy_websocket_message,
)
from rorapp.models import (
    Action,
    ActionLog,
    Concession,
    Faction,
    Senator,
    SenatorActionLog,
    Secret,
)
from rorapp.serializers import (
    ActionSerializer,
    ActionLogSerializer,
    ConcessionSerializer,
    SenatorActionLogSerializer,
)


def generate_assign_concessions_action(
    game_id: int, faction: Faction | None = None
) -> List[dict]:
    messages_to_send = []

    if faction is None:
        faction = Faction.objects.filter(game__id=game_id).order_by("rank").first()

    if not isinstance(faction, Faction):
        raise ValueError("Couldn't find a faction")

    faction_secrets = Secret.objects.filter(faction=faction)

    if faction_secrets.count() == 0:
        next_faction = get_next_faction_in_chromatic_order(faction)
        if isinstance(next_faction, Faction):
            messages_to_send.extend(
                generate_assign_concessions_action(game_id, next_faction)
            )
        else:
            phase = get_phase(game_id)
            if phase.name == "Revolution":
                messages_to_send.extend(start_next_turn(game_id))
            else:
                messages_to_send.extend(setup_mortality_phase(game_id))
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


def assign_concessions(action_id: int, data: dict) -> tuple[Response, List[dict]]:
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
    game_id = faction.game.id

    # Try to get the secret_senator_map data
    try:
        secret_senator_map = data.get("secret_senator_map")
        assert isinstance(secret_senator_map, str)
    except KeyError:
        return Response(
            {"message": "secret_senator_map must be provided"}, status=400
        ), []

    # Try to parse the secret_senator_map JSON
    try:
        secret_senator_map_json = json.loads(secret_senator_map)
    except json.JSONDecodeError:
        return Response(
            {"message": "Invalid JSON format in secret_senator_map"}, status=400
        ), []
    if len(secret_senator_map_json) > 0:
        for secret_id, senator_id in secret_senator_map_json.items():
            if senator_id is not None:
                # Try to parse the secret and senator IDs into integers
                try:
                    parsed_secret_id = int(secret_id)
                except ValueError:
                    return Response(
                        {"message": "Secret ID must be an integer"}, status=400
                    ), []
                try:
                    parsed_senator_id = int(senator_id)
                except ValueError:
                    return Response(
                        {"message": "Senator ID must be an integer"}, status=400
                    ), []

                # Try to get the secret
                try:
                    secret = Secret.objects.filter(
                        faction=faction, type="concession"
                    ).get(id=parsed_secret_id)
                except Secret.DoesNotExist:
                    return Response(
                        {"message": "Selected secret was not found"}, status=404
                    ), []

                # Try to get the senator
                try:
                    senator: Senator = Senator.objects.filter(faction=faction).get(
                        id=parsed_senator_id
                    )
                except Senator.DoesNotExist:
                    return Response(
                        {"message": "Selected senator was not found"}, status=404
                    ), []

                # Assign the concession to the senator
                messages_to_send.extend(assign_concession(faction, secret, senator))

    # Delete old actions
    messages_to_send.extend(delete_all_actions(game_id))

    # Proceed to next turn or next faction
    next_faction = get_next_faction_in_chromatic_order(faction)
    if next_faction:
        messages_to_send.extend(
            generate_assign_concessions_action(game_id, next_faction)
        )
    else:
        phase = get_phase(game_id)
        if phase.name == "Revolution":
            messages_to_send.extend(start_next_turn(game_id))
        else:
            messages_to_send.extend(setup_mortality_phase(game_id))

    return Response(
        {"message": "Concession assignment completed"}, status=200
    ), messages_to_send


def assign_concession(faction: Faction, secret: Secret, senator: Senator) -> List[dict]:
    messages_to_send = []

    # Delete secret
    messages_to_send.append(destroy_websocket_message("secret", secret.id))
    secret.delete()

    # Create concession
    concession = Concession(name=secret.name, game=faction.game, senator=senator)
    concession.save()
    messages_to_send.append(
        create_websocket_message("concession", ConcessionSerializer(concession).data)
    )

    # Create action log
    latest_action_log = (
        ActionLog.objects.filter(step__phase__turn__game=faction.game.id)
        .order_by("index")
        .last()
    )
    assert isinstance(latest_action_log, ActionLog)
    latest_step = get_step(faction.game.id)
    action_log = ActionLog(
        index=latest_action_log.index + 1,
        step=latest_step,
        type="new_concession",
        data={
            "concession": concession.id,
            "senator": senator.id,
        },
        faction=faction,
    )
    action_log.save()
    messages_to_send.append(
        create_websocket_message("action_log", ActionLogSerializer(action_log).data)
    )

    # Create senator action log
    senator_action_log = SenatorActionLog(senator=senator, action_log=action_log)
    senator_action_log.save()
    messages_to_send.append(
        create_websocket_message(
            "senator_action_log", SenatorActionLogSerializer(senator_action_log).data
        )
    )

    return messages_to_send
