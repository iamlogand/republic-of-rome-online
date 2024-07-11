from rorapp.functions.progress_helper import (
    create_step_and_message,
    get_latest_step,
)
from rorapp.functions.websocket_message_helper import create_websocket_message
from rorapp.models import ActionLog, Game, Senator, Title, Phase
from rorapp.serializers import ActionLogSerializer, SenatorSerializer, PhaseSerializer
from rorapp.functions.forum_phase_starter import start_forum_phase


def generate_personal_revenue(game_id: Game) -> dict:
    """
    Generate personal revenue for all aligned senators.

    Args:
        game_id (int): The game ID.

    Returns:
        dict: The WebSocket messages to send.
    """

    messages_to_send = []

    # Progress to the revenue phase
    latest_step = get_latest_step(game_id)
    new_phase = Phase(
        name="Revenue", index=latest_step.phase.index + 1, turn=latest_step.phase.turn
    )
    new_phase.save()
    messages_to_send.append(
        create_websocket_message("phase", PhaseSerializer(new_phase).data)
    )
    new_step, message = create_step_and_message(game_id)
    messages_to_send.append(message)

    # Generate personal revenue for all aligned senators
    aligned_senators = Senator.objects.filter(
        game=game_id, alive=True, faction__isnull=False
    )
    faction_leader_titles = Title.objects.filter(
        senator__game=game_id, name="Faction Leader", end_step__isnull=True
    )
    faction_leader_senator_ids = [title.senator.id for title in faction_leader_titles]
    for senator in aligned_senators:
        if senator.id in faction_leader_senator_ids:
            senator.talents += 3
        else:
            senator.talents += 1
        senator.save()
        messages_to_send.append(
            create_websocket_message("senator", SenatorSerializer(senator).data)
        )

    # Create action log
    latest_action_log = (
        ActionLog.objects.filter(step__phase__turn__game__id=game_id)
        .order_by("index")
        .last()
    )
    action_log = ActionLog(
        index=latest_action_log.index,
        step=new_step,
        type="personal_revenue",
    )
    action_log.save()
    messages_to_send.append(
        create_websocket_message("action_log", ActionLogSerializer(action_log).data)
    )

    # Proceed to the forum phase
    messages_to_send.extend(start_forum_phase(game_id))

    return messages_to_send
