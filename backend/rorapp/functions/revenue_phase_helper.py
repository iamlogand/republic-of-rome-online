from rorapp.functions.progress_helper import get_latest_step
from rorapp.functions.websocket_message_helper import create_websocket_message
from rorapp.models import ActionLog, Game, Senator, Title
from rorapp.serializers import ActionLogSerializer, SenatorSerializer


def generate_personal_revenue(game_id: Game) -> dict:
    """
    Generate personal revenue for all aligned senators.

    Args:
        game_id (int): The game ID.

    Returns:
        dict: The WebSocket messages to send.
    """

    messages_to_send = []

    aligned_senators = Senator.objects.filter(
        game=game_id, alive=True, faction__isnull=False
    )
    faction_leader_titles = Title.objects.filter(
        senator__game=game_id, name="Faction Leader", end_step__isnull=True
    )
    faction_leader_senator_ids = [title.senator.id for title in faction_leader_titles]

    # Generate personal revenue for all aligned senators
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
    latest_step = get_latest_step(game_id)
    latest_action_log = (
        ActionLog.objects.filter(step=latest_step).order_by("index").last()
    )
    action_log = ActionLog(
        index=latest_action_log.index,
        step=latest_step,
        type="personal_revenue",
    )
    action_log.save()
    messages_to_send.append(
        create_websocket_message("action_log", ActionLogSerializer(action_log).data)
    )

    return messages_to_send
