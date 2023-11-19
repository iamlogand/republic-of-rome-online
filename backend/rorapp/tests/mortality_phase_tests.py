from typing import List
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rorapp.functions import (
    delete_all_games,
    generate_game,
    setup_mortality_phase,
    start_game,
)
from rorapp.tests.action_helper import get_and_check_actions
from rorapp.models import Action, Faction


class MortalityPhaseTests(TestCase):
    """
    These tests check that players can face mortality and mortality is resolved correctly.
    """

    def test_mortality_phase(self: TestCase) -> None:
        self.client = APIClient()
        delete_all_games()
        for player_count in range(3, 7):
            self.do_mortality_phase_test(player_count)

    def do_mortality_phase_test(self: TestCase, player_count: int) -> None:
        game_id = self.setup_game_in_mortality_phase(player_count)
        potential_actions_for_all_players = get_and_check_actions(
            self, game_id, False, "face_mortality", player_count
        )
        self.submit_actions(game_id, player_count, potential_actions_for_all_players)
        get_and_check_actions(
            self, game_id, True, "face_mortality", player_count, step_index=-2
        )

    def setup_game_in_mortality_phase(self: TestCase, player_count: int) -> int:
        game_id = generate_game(player_count)
        start_game(game_id, seed=1)
        setup_mortality_phase(game_id)
        return game_id

    def submit_actions(
        self: TestCase,
        game_id: int,
        player_count: int,
        potential_actions_for_all_players: List[Action],
    ) -> None:
        for player_number in range(1, player_count + 1):
            self.submit_action(
                player_number, game_id, potential_actions_for_all_players
            )

    def submit_action(
        self: TestCase,
        player_number: int,
        game_id: int,
        potential_actions_for_all_players: List[Action],
    ) -> None:
        user = User.objects.get(username=f"TestUser{player_number}")
        faction = Faction.objects.filter(player__user=user).get(game=game_id)
        potential_actions = potential_actions_for_all_players.filter(faction=faction)
        self.assertEqual(len(potential_actions), 1)
        potential_action = potential_actions[0]
        self.client.force_authenticate(user=user)
        response = self.client.post(
            f"/api/games/{game_id}/submit-action/{potential_action.id}/",
        )
        self.assertEqual(response.status_code, 200)
