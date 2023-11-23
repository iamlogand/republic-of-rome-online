from django.db.models.query import QuerySet
from django.test import TestCase
from rorapp.models import Action, Step


def check_all_actions(
    test_case: TestCase,
    game_id: int,
    action_type: str,
    completed_action_count: int,
    total_action_count: int,
) -> None:
    if completed_action_count < total_action_count:
        get_and_check_actions(
            test_case,
            game_id,
            False,
            action_type,
            total_action_count - completed_action_count,
        )
        get_and_check_actions(
            test_case,
            game_id,
            True,
            action_type,
            completed_action_count,
        )


def get_and_check_actions(
    test_case: TestCase,
    game_id: int,
    completed: bool,
    action_type: str,
    action_count: int,
) -> QuerySet[Action]:
    step = Step.objects.filter(phase__turn__game=game_id).order_by("-index").first()
    potential_actions_for_all_players = Action.objects.filter(
        step=step,
        completed=completed,
        type=action_type,
    )
    test_case.assertEqual(potential_actions_for_all_players.count(), action_count)
    faction_ids_with_correct_action = []
    for action in potential_actions_for_all_players:
        test_case.assertEqual(action.type, action_type)
        faction_ids_with_correct_action.append(action.faction.id)
    test_case.assertEqual(len(set(faction_ids_with_correct_action)), action_count)
    return potential_actions_for_all_players


def check_old_actions_deleted(test_case: TestCase, game_id: int) -> None:
    latest_step = (
        Step.objects.filter(phase__turn__game=game_id).order_by("-index").first()
    )
    actions = Action.objects.filter(
        step__phase__turn__game=game_id, step__index__lt=latest_step.index
    )
    fail_message_intro = f"Expected all old actions (with step index < {latest_step.index}) to have been deleted, but found: "
    fail_message = fail_message_intro
    for action in actions:
        if fail_message != fail_message_intro:
            fail_message += ", "
        fail_message += (
            f"{action.type} for {action.faction} in step index {action.step.index}"
        )
    test_case.assertEqual(actions.count(), 0, fail_message + ".")
