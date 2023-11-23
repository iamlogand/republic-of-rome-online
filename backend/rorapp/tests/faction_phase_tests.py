import random
from typing import List
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rorapp.functions import delete_all_games, generate_game, start_game
from rorapp.models import Action, Faction, Phase, Senator, Title
from rorapp.tests.action_helper import (
    check_old_actions_deleted,
    check_all_actions,
    get_and_check_actions,
)


class FactionPhaseTests(TestCase):
    """
    Ensure that players can select their first faction leader during the faction phase.
    """

    def test_faction_phase(self) -> None:
        self.client = APIClient()
        delete_all_games()
        for player_count in range(3, 7):
            self.do_faction_phase_test(player_count)

    def do_faction_phase_test(self, player_count: int) -> None:
        game_id = self.setup_game_in_faction_phase(player_count)
        self.check_latest_phase(game_id, 1, "Faction")
        potential_actions_for_all_players = get_and_check_actions(
            self, game_id, False, "select_faction_leader", player_count
        )
        self.submit_actions(game_id, player_count, potential_actions_for_all_players)
        self.check_faction_leader_titles(game_id, player_count)
        self.check_latest_phase(game_id, 2, "Mortality")
        check_old_actions_deleted(self, game_id)

    def setup_game_in_faction_phase(self, player_count: int) -> int:
        game_id = generate_game(player_count)
        random.seed(1)
        start_game(game_id)
        self.assertEqual(Faction.objects.filter(game=game_id).count(), player_count)
        return game_id

    def check_latest_phase(
        self,
        game_id: int,
        expected_phase_count: int,
        expected_latest_phase_name: str,
    ) -> None:
        phases = Phase.objects.filter(turn__game=game_id)
        self.assertEqual(phases.count(), expected_phase_count)
        latest_phase = phases[len(phases) - 1]
        self.assertEqual(latest_phase.name, expected_latest_phase_name)

    def submit_actions(
        self,
        game_id: int,
        player_count: int,
        potential_actions_for_all_players: List[Action],
    ) -> None:
        for player_number in range(1, player_count + 1):
            self.submit_action(
                player_number, game_id, potential_actions_for_all_players
            )

    def submit_action(
        self,
        player_number: int,
        game_id: int,
        potential_actions_for_all_players: List[Action],
    ) -> None:
        user = User.objects.get(username=f"TestUser{player_number}")
        faction = Faction.objects.filter(player__user=user).get(game=game_id)
        potential_actions = potential_actions_for_all_players.filter(faction=faction)
        self.assertEqual(len(potential_actions), 1)
        potential_action = potential_actions[0]
        senators = Senator.objects.filter(faction=faction).order_by("name")
        first_senator = senators[0]

        self.client.force_authenticate(user=user)
        response = self.client.post(
            f"/api/games/{game_id}/submit-action/{potential_action.id}/",
            data={"leader_id": first_senator.id},
        )
        self.assertEqual(response.status_code, 200)
        check_all_actions(
            self,
            game_id,
            "select_faction_leader",
            player_number,
            len(potential_actions_for_all_players),
        )

    def check_faction_leader_titles(self, game_id: int, player_count: int) -> None:
        titles = Title.objects.filter(
            senator__faction__game=game_id, name="Faction Leader"
        )
        self.assertEqual(titles.count(), player_count)
