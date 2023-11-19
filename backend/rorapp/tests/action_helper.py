from typing import List
from django.test import TestCase
from rorapp.models import Action, Step


def get_and_check_actions(
    self: TestCase,
    game_id: int,
    completed: bool,
    action_type: str,
    action_count: int,
    step_index: int = -1,
) -> List[Action]:
    latest_step = (
        Step.objects.filter(phase__turn__game=game_id).order_by("-index")[
            (-1 * step_index) - 1
        ]
        if step_index < 0
        else Step.objects.get(index=step_index)
    )
    potential_actions_for_all_players = Action.objects.filter(
        step=latest_step.id,
        completed=completed,
        type=action_type,
    )
    self.assertEqual(potential_actions_for_all_players.count(), action_count)
    faction_ids_with_correct_action = []
    for action in potential_actions_for_all_players:
        self.assertEqual(action.type, action_type)
        faction_ids_with_correct_action.append(action.faction.id)
    self.assertEqual(len(set(faction_ids_with_correct_action)), action_count)
    return potential_actions_for_all_players
