from typing import List
from rorapp.functions.websocket_message_helper import destroy_websocket_message
from rorapp.models import Action, Step


def delete_old_actions(game_id: int) -> List[dict]:
    latest_step = (
        Step.objects.filter(phase__turn__game=game_id).order_by("-index").first()
    )
    actions = Action.objects.filter(
        step__phase__turn__game=game_id, step__index__lt=latest_step.index
    )
    actions.delete()
    websocket_messages = []
    for action in actions:
        websocket_messages.append(destroy_websocket_message("action", action.id))
    return websocket_messages
