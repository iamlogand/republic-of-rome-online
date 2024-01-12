import random
from typing import List
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
from rorapp.tests.action_helper import (
    check_all_actions,
    check_old_actions_deleted,
    get_and_check_actions,
)
from rorapp.models import Action, ActionLog, Faction, Phase, Senator, Step, Title


class MortalityPhaseTests(TestCase):
    """
    Ensure that players can face mortality and mortality is resolved correctly.
    """

    def setUp(self) -> None:
        random.seed(5)
        self.client = APIClient()
        delete_all_games()

    def test_face_mortality(self) -> None:
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
        self.kill_regular_senator(game_id)
        self.kill_two_senators(game_id)

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
        living_senator_count = Senator.objects.filter(
            game=game_id, death_step=None
        ).count()
        highest_ranking_senator = self.get_senators_with_title(
            game_id, "Temporary Rome Consul"
        )[0]

        action_logs, messages = self.kill_senators(game_id, [highest_ranking_senator.id])
        self.assertEqual(len(messages), 18)
        latest_action_log = action_logs[0]

        self.assertIsNone(latest_action_log.data["heir_senator"])
        self.assertEqual(
            latest_action_log.data["major_office"], "Temporary Rome Consul"
        )
        post_death_living_senator_count = Senator.objects.filter(
            game=game_id, death_step=None
        ).count()
        self.assertEqual(living_senator_count - 1, post_death_living_senator_count)
        prior_consul_titles = Title.objects.filter(senator=highest_ranking_senator, name="Prior Consul")
        self.assertEqual(prior_consul_titles.count(), 1)
        prior_consul_title = prior_consul_titles[0]
        self.assertEqual(prior_consul_title.end_step, latest_action_log.step)

    def kill_faction_leader(self, game_id: int) -> None:
        living_senator_count = Senator.objects.filter(
            game=game_id, death_step=None
        ).count()
        faction_leader = self.get_senators_with_title(game_id, "Faction Leader")[0]
        self.assertEqual(faction_leader.name, "Aurelius")
        faction_leader_title = Title.objects.get(senator=faction_leader)

        action_logs, messages = self.kill_senators(game_id, [faction_leader.id])
        self.assertEqual(len(messages), 11)
        latest_action_log = action_logs[0]

        heir_id = latest_action_log.data["heir_senator"]
        heir = Senator.objects.get(id=heir_id)
        self.assertEqual(heir.name, "Aurelius")
        heir_title = Title.objects.get(senator=heir.id)
        self.assertEqual(heir_title.start_step, latest_action_log.step)

        self.assertIsNone(latest_action_log.data["major_office"])
        faction_leader = Senator.objects.get(id=faction_leader.id)
        self.assertEqual(faction_leader.death_step, latest_action_log.step)
        old_faction_leader_title = Title.objects.get(id=faction_leader_title.id)
        self.assertEqual(old_faction_leader_title.end_step, latest_action_log.step)
        post_death_living_senator_count = Senator.objects.filter(
            game=game_id, death_step=None
        ).count()
        self.assertEqual(living_senator_count, post_death_living_senator_count)

    def kill_regular_senator(self, game_id: int) -> None:
        living_senator_count = Senator.objects.filter(
            game=game_id, death_step=None
        ).count()
        regular_senator = self.get_senators_with_title(game_id, None)[0]

        action_logs, messages = self.kill_senators(game_id, [regular_senator.id])
        self.assertEqual(len(messages), 8)
        latest_action_log = action_logs[0]

        self.assertIsNone(latest_action_log.data["heir_senator"])
        self.assertIsNone(latest_action_log.data["major_office"])
        post_death_living_senator_count = Senator.objects.filter(
            game=game_id, death_step=None
        ).count()
        self.assertEqual(living_senator_count - 1, post_death_living_senator_count)

    def kill_two_senators(self, game_id: int) -> None:
        living_senator_count = Senator.objects.filter(
            game=game_id, death_step=None
        ).count()
        two_regular_senators = self.get_senators_with_title(game_id, None)[0:2]
        senator_ids = [senator.id for senator in two_regular_senators]
        latest_action_log, messages = self.kill_senators(game_id, senator_ids)
        self.assertEqual(len(messages), 14)
        post_death_living_senator_count = Senator.objects.filter(
            game=game_id, death_step=None
        ).count()
        self.assertEqual(living_senator_count - 2, post_death_living_senator_count)

    def kill_senators(self, game_id: int, senator_ids: List[int]) -> (List[ActionLog], dict):
        senators = Senator.objects.filter(id__in=senator_ids)
        senator_codes = [senator.code for senator in senators]
        self.assertEqual(len(senator_codes), len(senator_ids))
        messages = resolve_mortality(game_id, senator_codes)
        latest_step = Step.objects.filter(phase__turn__game=game_id).order_by("-index")[
            1
        ]
        latest_action_logs = ActionLog.objects.filter(
            step=latest_step, type="face_mortality"
        ).order_by("index")
        self.assertEqual(len(latest_action_logs), len(senator_ids))
        for action_log in latest_action_logs:
            self.assertIsNotNone(action_log.data["senator"])
            matching_senator = senators.get(id=action_log.data["senator"])
            self.assertEqual(
                action_log.faction.position, matching_senator.faction.position
            )
        return latest_action_logs, messages

    def get_senators_with_title(
        self, game_id: int, title_name: str | None
    ) -> List[Senator]:
        living_senators = Senator.objects.filter(
            game=game_id, death_step=None
        ).order_by("name")
        matching_senators = []
        for senator in living_senators:
            titles = Title.objects.filter(senator=senator)
            if title_name is None and len(titles) == 0:
                matching_senators.append(senator)
            matching_titles = titles.filter(name=title_name)
            if len(matching_titles) > 0:
                matching_senators.append(senator)
        return matching_senators
