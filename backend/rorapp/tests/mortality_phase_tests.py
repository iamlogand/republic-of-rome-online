import random
from typing import List
from django.db.models.query import QuerySet
from django.test import TestCase
from rest_framework.test import APIClient
from rorapp.functions import (
    delete_all_games,
    generate_game,
    setup_mortality_phase,
    start_game,
)
from rorapp.functions import resolve_mortality
from rorapp.functions.faction_leader_helper import select_faction_leader
from rorapp.tests.test_helper import (
    check_latest_phase,
    check_old_actions_deleted,
    get_and_check_actions,
    submit_actions,
)
from rorapp.models import ActionLog, Faction, Senator, Title


class MortalityPhaseTests(TestCase):
    """
    Ensure that players can face mortality and mortality is resolved correctly.
    """

    def setUp(self) -> None:
        random.seed(6)
        self.client = APIClient()
        delete_all_games()

    def test_face_mortality(self) -> None:
        """
        Ensure that the face mortality action submission works correctly.
        """

        for player_count in range(3, 7):
            self.do_face_mortality_test(player_count)

    def test_resolve_mortality(self) -> None:
        """
        Ensure that the `resolve_mortality` function works correctly.
        """

        game_id = self.setup_game_in_mortality_phase(3)
        self.kill_hrao(game_id)
        self.kill_faction_leader(game_id)
        self.kill_regular_senator(game_id)
        self.kill_two_senators(game_id)

    def do_face_mortality_test(self, player_count: int) -> None:
        game_id = self.setup_game_in_mortality_phase(player_count)
        potential_actions_for_all_players = get_and_check_actions(
            self, game_id, False, "face_mortality", player_count
        )
        submit_actions(self, game_id, potential_actions_for_all_players)
        latest_mortality_logs = self.get_logs_from_latest_mortality(game_id)
        self.assertEqual(len(latest_mortality_logs), 1)
        check_latest_phase(self, game_id, "Forum")
        check_old_actions_deleted(self, game_id)

    def setup_game_in_mortality_phase(self, player_count: int) -> int:
        """
        This doesn't run through all the actions that would normally happen prior to the mortality phase.
        It just creates a game, sets some faction leaders, and starts the mortality phase.
        """
        game_id = generate_game(player_count)
        start_game(game_id)
        self.select_faction_leaders(game_id)
        setup_mortality_phase(game_id)
        return game_id

    def select_faction_leaders(self, game_id: int) -> None:
        senator_in_faction_1 = Senator.objects.filter(
            game=game_id, faction__position=1
        ).first()
        senator_in_faction_2 = Senator.objects.filter(
            game=game_id, faction__position=3
        ).first()
        senator_in_faction_3 = Senator.objects.filter(
            game=game_id, faction__position=5
        ).first()
        assert isinstance(senator_in_faction_1, Senator)
        assert isinstance(senator_in_faction_2, Senator)
        assert isinstance(senator_in_faction_3, Senator)
        select_faction_leader(senator_in_faction_1.id)
        select_faction_leader(senator_in_faction_2.id)
        select_faction_leader(senator_in_faction_3.id)

    def check_action_log(self, game_id: int) -> None:
        latest_mortality_log = (
            ActionLog.objects.filter(step__phase__turn__game=game_id, type="mortality")
            .order_by("index")
            .last()
        )
        assert isinstance(latest_mortality_log, ActionLog)
        latest_mortality_logs = ActionLog.objects.filter(
            step=latest_mortality_log.step
        ).order_by("index")
        # It's possible to have more than 1 action log in the event that more than one senator dies,
        # but in this deterministic test no more than one senator should die
        self.assertEqual(latest_mortality_logs.count(), 1)

    def kill_hrao(self, game_id: int) -> None:
        living_senator_count = Senator.objects.filter(game=game_id, alive=True).count()
        highest_ranking_senator = self.get_senators_with_title(
            game_id, "Temporary Rome Consul"
        )[0]

        logs, messages = self.kill_senators(game_id, [highest_ranking_senator.id])
        self.assertEqual(len(messages), 37)
        latest_log = logs[0]

        self.assertIsNone(latest_log.data["heir_senator"])
        self.assertEqual(latest_log.data["major_office"], "Temporary Rome Consul")
        post_death_living_senator_count = Senator.objects.filter(
            game=game_id, alive=True
        ).count()
        self.assertEqual(living_senator_count - 1, post_death_living_senator_count)
        prior_consul_titles = Title.objects.filter(
            senator=highest_ranking_senator, name="Prior Consul"
        )
        self.assertEqual(prior_consul_titles.count(), 1)
        prior_consul_title = prior_consul_titles[0]
        self.assertEqual(prior_consul_title.end_step, latest_log.step)

    def kill_faction_leader(self, game_id: int) -> None:
        living_senator_count = Senator.objects.filter(game=game_id, alive=True).count()
        faction_leader = self.get_senators_with_title(game_id, "Faction Leader")[0]
        self.assertEqual(faction_leader.name, "Aemilius")
        faction_leader_title = Title.objects.get(senator=faction_leader)

        logs, _ = self.kill_senators(game_id, [faction_leader.id])
        latest_log = logs[0]

        heir_id = latest_log.data["heir_senator"]
        heir = Senator.objects.get(id=heir_id)
        self.assertEqual(heir.name, "Aemilius")
        heir_title = Title.objects.get(senator=heir.id)
        self.assertEqual(heir_title.start_step, latest_log.step)

        self.assertIsNone(latest_log.data["major_office"])
        faction_leader = Senator.objects.get(id=faction_leader.id)
        self.assertFalse(faction_leader.alive)
        old_faction_leader_title = Title.objects.get(id=faction_leader_title.id)
        self.assertEqual(old_faction_leader_title.end_step, latest_log.step)
        post_death_living_senator_count = Senator.objects.filter(
            game=game_id, alive=True
        ).count()
        self.assertEqual(living_senator_count, post_death_living_senator_count)

    def kill_regular_senator(self, game_id: int) -> None:
        living_senator_count = Senator.objects.filter(game=game_id, alive=True).count()
        regular_senator = self.get_senators_with_title(game_id, None)[0]

        logs, _ = self.kill_senators(game_id, [regular_senator.id])
        latest_log = logs[0]

        self.assertIsNone(latest_log.data["heir_senator"])
        self.assertIsNone(latest_log.data["major_office"])
        post_death_living_senator_count = Senator.objects.filter(
            game=game_id, alive=True
        ).count()
        self.assertEqual(living_senator_count - 1, post_death_living_senator_count)

    def kill_two_senators(self, game_id: int) -> None:
        living_senator_count = Senator.objects.filter(game=game_id, alive=True).count()
        two_regular_senators = self.get_senators_with_title(game_id, None)[0:2]
        senator_ids = [senator.id for senator in two_regular_senators]
        self.kill_senators(game_id, senator_ids)
        post_death_living_senator_count = Senator.objects.filter(
            game=game_id, alive=True
        ).count()
        self.assertEqual(living_senator_count - 2, post_death_living_senator_count)

    def get_logs_from_latest_mortality(
        self, game_id: int
    ) -> QuerySet[ActionLog, ActionLog]:
        latest_mortality_log = (
            ActionLog.objects.filter(step__phase__turn__game=game_id, type="mortality")
            .order_by("index")
            .last()
        )
        assert isinstance(latest_mortality_log, ActionLog)
        return ActionLog.objects.filter(step=latest_mortality_log.step).order_by(
            "index"
        )

    def kill_senators(
        self, game_id: int, senator_ids: List[int]
    ) -> tuple[QuerySet[ActionLog, ActionLog], List[dict]]:
        senators = Senator.objects.filter(id__in=senator_ids)
        senator_codes = [senator.code for senator in senators]
        self.assertEqual(len(senator_codes), len(senator_ids))
        messages = resolve_mortality(game_id, senator_codes)
        latest_mortality_logs = self.get_logs_from_latest_mortality(game_id)
        self.assertEqual(len(latest_mortality_logs), len(senator_ids))
        for action_log in latest_mortality_logs:
            self.assertIsNotNone(action_log.data["senator"])
            matching_senator = senators.get(id=action_log.data["senator"])
            assert isinstance(action_log.faction, Faction)
            assert isinstance(matching_senator.faction, Faction)
            self.assertEqual(
                action_log.faction.position, matching_senator.faction.position
            )
        return latest_mortality_logs, messages

    def get_senators_with_title(
        self, game_id: int, title_name: str | None
    ) -> List[Senator]:
        living_senators = Senator.objects.filter(game=game_id, alive=True).order_by(
            "name"
        )
        matching_senators = []
        for senator in living_senators:
            titles = Title.objects.filter(senator=senator)
            if title_name is None and len(titles) == 0:
                matching_senators.append(senator)
            matching_titles = titles.filter(name=title_name)
            if len(matching_titles) > 0:
                matching_senators.append(senator)
        return matching_senators
