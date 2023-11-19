from django.test import TestCase
from rest_framework.test import APIClient
from rorapp.functions import (
    delete_all_games,
    generate_game,
    setup_mortality_phase,
    start_game,
)
from rorapp.tests.action_helper import get_and_check_actions


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

    def setup_game_in_mortality_phase(self: TestCase, player_count: int) -> int:
        game_id = generate_game(player_count)
        start_game(game_id, seed=1)
        setup_mortality_phase(game_id)
        potential_actions_for_all_players = get_and_check_actions(
            self, game_id, False, "face_mortality", player_count
        )
        return game_id
