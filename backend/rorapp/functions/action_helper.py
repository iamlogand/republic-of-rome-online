from rorapp.functions.progress_helper import get_step
from rorapp.functions.websocket_message_helper import destroy_websocket_message
from rorapp.models import Action


def delete_old_actions(game_id: int) -> list[dict]:
    websocket_messages = []

    latest_step = get_step(game_id)
    actions = Action.objects.filter(
        step__phase__turn__game=game_id, step__index__lt=latest_step.index
    )
    for action in actions:
        websocket_messages.append(destroy_websocket_message("action", action.id))
    actions.delete()

    return websocket_messages


def delete_all_actions(game_id: int) -> list[dict]:
    websocket_messages = []

    actions = Action.objects.filter(step__phase__turn__game=game_id)
    for action in actions:
        websocket_messages.append(destroy_websocket_message("action", action.id))
    actions.delete()

    return websocket_messages
