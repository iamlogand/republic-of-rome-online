import random
from django.test import TestCase
from rest_framework.test import APIClient
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from rorapp.functions import (
    delete_all_games,
    generate_game,
    setup_mortality_phase,
    start_game,
)
from rorapp.functions import resolve_mortality
from rorapp.tests.action_helper import get_and_check_actions
from rorapp.models import Action, ActionLog, Faction, Phase, Senator, Step


class MortalityPhaseTests(TestCase):
    """
    Ensure that players can face mortality and mortality is resolved correctly.
    """

    def setUp(self) -> None:
        random.seed(5)
        self.client = APIClient()
        delete_all_games()

    def test_mortality_phase_api(self) -> None:
        """
        Ensure that the face mortality action submission works correctly.
        """

        for player_count in range(3, 7):
            self.do_mortality_phase_test(player_count)

    def test_resolve_mortality(self) -> None:
        """
        Ensure that the `resolve_mortality` function works correctly.
        """

        game_id = self.setup_game_in_mortality_phase(3)
        self.kill_hrao(game_id)

    def do_mortality_phase_test(self, player_count: int) -> None:
        game_id = self.setup_game_in_mortality_phase(player_count)
        potential_actions_for_all_players = get_and_check_actions(
            self, game_id, False, "face_mortality", player_count
        )
        self.submit_actions(game_id, potential_actions_for_all_players)
        get_and_check_actions(
            self, game_id, True, "face_mortality", player_count, step_index=-2
        )
        self.check_action_log(game_id)
        latest_phase = Phase.objects.filter(turn__game=game_id).latest("index")
        self.assertEqual(latest_phase.name, "Forum")

    def setup_game_in_mortality_phase(self, player_count: int) -> int:
        game_id = generate_game(player_count)
        start_game(game_id)
        setup_mortality_phase(game_id)
        return game_id

    def submit_actions(
        self,
        game_id: int,
        potential_actions_for_all_players: QuerySet[Action],
    ) -> None:
        for player_number in range(1, len(potential_actions_for_all_players) + 1):
            self.submit_action(
                player_number, game_id, potential_actions_for_all_players
            )

    def submit_action(
        self,
        player_number: int,
        game_id: int,
        potential_actions_for_all_players: QuerySet[Action],
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

    def check_action_log(self, game_id: int) -> None:
        previous_step = Step.objects.filter(phase__turn__game=game_id).order_by(
            "-index"
        )[1]
        action_log = ActionLog.objects.filter(step=previous_step)
        # It's possible to have more than 1 action log in the event if more than one senator dies,
        # but in this deterministic test no more than one senator should die
        self.assertEqual(action_log.count(), 1)
        self.assertEqual(action_log[0].type, "face_mortality")

    def kill_hrao(self, game_id: int) -> None:
        highest_ranking_senator = (
            Senator.objects.filter(faction__game=game_id).order_by("rank").first()
        )
        self.assertEqual(highest_ranking_senator.name, "Aemilius")
        resolve_mortality(game_id, [highest_ranking_senator.code])
        latest_action_logs = ActionLog.objects.filter(
            step__phase__turn__game=game_id, type="face_mortality"
        ).order_by("index")
        self.assertEqual(len(latest_action_logs), 1)
        latest_action_log = latest_action_logs.first()
        self.assertEqual(latest_action_log.faction.position, 1)
        self.assertIsNotNone(latest_action_log.data["senator"])
        self.assertIsNone(latest_action_log.data["heir_senator"])
        self.assertEqual(latest_action_log.data["major_office"], "Temporary Rome Consul")
