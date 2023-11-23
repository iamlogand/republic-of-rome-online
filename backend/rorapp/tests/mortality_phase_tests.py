import random
from django.test import TestCase
from rest_framework.test import APIClient
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from rorapp.functions import (
    delete_all_games,
    generate_game,
    setup_mortality_phase,
    set_faction_leader,
    start_game,
)
from rorapp.functions import resolve_mortality
from rorapp.tests.action_helper import check_all_actions, check_old_actions_deleted, get_and_check_actions
from rorapp.models import Action, ActionLog, Faction, Phase, Senator, Step, Title


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
        self.kill_faction_leader(game_id)

    def do_mortality_phase_test(self, player_count: int) -> None:
        game_id = self.setup_game_in_mortality_phase(player_count)
        potential_actions_for_all_players = get_and_check_actions(
            self, game_id, False, "face_mortality", player_count
        )
        self.submit_actions(game_id, potential_actions_for_all_players)
        self.check_action_log(game_id)
        latest_phase = Phase.objects.filter(turn__game=game_id).latest("index")
        self.assertEqual(latest_phase.name, "Forum")
        check_old_actions_deleted(self, game_id)

    def setup_game_in_mortality_phase(self, player_count: int) -> int:
        game_id = generate_game(player_count)
        start_game(game_id)
        self.set_faction_leaders(game_id)
        setup_mortality_phase(game_id)
        return game_id

    def set_faction_leaders(self, game_id: int) -> None:
        senator_in_faction_1 = Senator.objects.filter(game=game_id, faction__position=1)
        senator_in_faction_2 = Senator.objects.filter(game=game_id, faction__position=3)
        senator_in_faction_3 = Senator.objects.filter(game=game_id, faction__position=5)
        set_faction_leader(senator_in_faction_1.first().id)
        set_faction_leader(senator_in_faction_2.first().id)
        set_faction_leader(senator_in_faction_3.first().id)

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
        check_all_actions(
            self,
            game_id,
            "face_mortality",
            player_number,
            len(potential_actions_for_all_players),
        )

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
        latest_action_log = self.kill_senator(game_id, highest_ranking_senator.id)
        self.assertIsNone(latest_action_log.data["heir_senator"])
        self.assertEqual(
            latest_action_log.data["major_office"], "Temporary Rome Consul"
        )

    def kill_faction_leader(self, game_id: int) -> None:
        faction_leader_title = Title.objects.filter(
            senator__game=game_id, name="Faction Leader"
        ).first()
        faction_leader = Senator.objects.filter(
            id=faction_leader_title.senator.id
        ).first()
        self.assertEqual(faction_leader.name, "Aurelius")

    def kill_senator(self, game_id: int, senator_id: int) -> ActionLog:
        senator = Senator.objects.get(id=senator_id)
        resolve_mortality(game_id, [senator.code])
        latest_step = Step.objects.filter(phase__turn__game=game_id).order_by("-index")[
            1
        ]
        latest_action_logs = ActionLog.objects.filter(
            step=latest_step, type="face_mortality"
        ).order_by("index")
        self.assertEqual(len(latest_action_logs), 1)
        latest_action_log = latest_action_logs.first()
        self.assertEqual(latest_action_log.faction.position, senator.faction.position)
        self.assertEqual(latest_action_log.data["senator"], senator.id)
        return latest_action_log
