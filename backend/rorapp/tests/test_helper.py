from django.db.models.query import QuerySet
from django.test import TestCase
from rest_framework.test import APIClient
from rorapp.functions import get_step
from rorapp.models import Action, Phase, Player, Step, Turn
from django.contrib.auth.models import User
from typing import Callable


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
    step = get_step(game_id)
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
    latest_step = get_step(game_id)
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


def submit_actions(
    test_case: TestCase,
    game_id: int,
    potential_actions: QuerySet[Action, Action],
    action_processor: Callable[[Action], object] = lambda _: {},
) -> None:
    starting_action_count = len(potential_actions)
    completed_action_count = 0
    for action in potential_actions:
        submit_action(
            test_case,
            game_id,
            action,
            action_processor,
        )
        completed_action_count += 1
        check_all_actions(
            test_case,
            game_id,
            action.type,
            completed_action_count,
            starting_action_count,
        )


def submit_action(
    test_case: TestCase,
    game_id: int,
    potential_action: Action,
    action_processor: Callable[[Action], object],
) -> None:
    assert isinstance(potential_action.faction.player, Player)
    assert isinstance(potential_action.faction.player.user, User)
    user = User.objects.get(id=potential_action.faction.player.user.id)
    data = action_processor(potential_action)
    assert isinstance(test_case.client, APIClient)
    test_case.client.force_authenticate(user=user)
    response = test_case.client.post(
        f"/api/games/{game_id}/submit-action/{potential_action.id}/",
        data,
    )
    test_case.assertEqual(response.status_code, 200)


def check_latest_phase(
    test_case: TestCase,
    game_id: int,
    expected_latest_phase_name: str,
    expected_phase_count: int | None = None,
) -> None:
    """
    Check that the latest phase has the expected name, and matches the latest step and latest turn.
    """
    latest_turn = Turn.objects.filter(game=game_id).order_by("-index").first()
    phases = Phase.objects.filter(turn=latest_turn).order_by("-index")
    if expected_phase_count:
        test_case.assertEqual(phases.count(), expected_phase_count)
    latest_phase = phases.first()
    latest_step = get_step(game_id)
    assert isinstance(latest_phase, Phase)
    assert isinstance(latest_step, Step)
    test_case.assertEqual(latest_phase.id, latest_step.phase.id)
    test_case.assertEqual(latest_phase.name, expected_latest_phase_name)
