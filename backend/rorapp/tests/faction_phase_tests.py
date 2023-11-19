from typing import List
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rorapp.functions import delete_all_games, generate_game, start_game
from rorapp.models import Action, Faction, Phase, Senator, Title
from rorapp.tests.action_helper import get_and_check_actions


class FactionPhaseTests(TestCase):
    """
    These tests check that players can select their first faction leader during the faction phase.
    """

    def test_faction_phase(self: TestCase) -> None:
        self.client = APIClient()
        delete_all_games()
        for player_count in range(3, 7):
            self.do_faction_phase_test(player_count)

    def do_faction_phase_test(self: TestCase, player_count: int) -> None:
        game_id = self.setup_game_in_faction_phase(player_count)
        self.check_latest_phase(game_id, 1, "Faction")
        potential_actions_for_all_players = get_and_check_actions(
            self, game_id, False, "select_faction_leader", player_count
        )
        self.submit_actions(game_id, player_count, potential_actions_for_all_players)
        get_and_check_actions(
            self, game_id, True, "select_faction_leader", player_count, step_index=-2
        )
        self.check_faction_leader_titles(game_id, player_count)
        self.check_latest_phase(game_id, 2, "Mortality")

    def setup_game_in_faction_phase(self: TestCase, player_count: int) -> int:
        game_id = generate_game(player_count)
        start_game(game_id, seed=1)
        self.assertEqual(Faction.objects.filter(game=game_id).count(), player_count)
        return game_id

    def check_latest_phase(
        self: TestCase,
        game_id: int,
        expected_phase_count: int,
        expected_latest_phase_name: str,
    ) -> None:
        phases = Phase.objects.filter(turn__game=game_id)
        self.assertEqual(phases.count(), expected_phase_count)
        latest_phase = phases[len(phases) - 1]
        self.assertEqual(latest_phase.name, expected_latest_phase_name)

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
        user_faction_id = Faction.objects.filter(player__user=user).get(game=game_id).id
        user_potential_action_id = potential_actions_for_all_players.get(
            faction=user_faction_id
        ).id
        user_senators = Senator.objects.filter(faction=user_faction_id).order_by("name")
        user_first_senator_id = user_senators[0].id

        self.client.force_authenticate(user=user)
        response = self.client.post(
            f"/api/games/{game_id}/submit-action/{user_potential_action_id}/",
            data={"leader_id": user_first_senator_id},
        )
        self.assertEqual(response.status_code, 200)

    def check_faction_leader_titles(
        self: TestCase, game_id: int, player_count: int
    ) -> None:
        titles = Title.objects.filter(
            senator__faction__game=game_id, name="Faction Leader"
        )
        self.assertEqual(titles.count(), player_count)
