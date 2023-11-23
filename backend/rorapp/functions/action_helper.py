from rorapp.models import Action, Step


def delete_old_actions(game_id: int) -> dict:
    latest_step = (
        Step.objects.filter(phase__turn__game=game_id).order_by("-index").first()
    )
    actions = Action.objects.filter(
        step__phase__turn__game=game_id, step__index__lt=latest_step.index
    )
    actions.delete()
