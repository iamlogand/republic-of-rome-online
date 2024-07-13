import random
from django.test import TestCase
from rest_framework.test import APIClient
from rorapp.functions import delete_all_games, generate_game, start_game
from rorapp.models import Action, Faction, Senator, Title
from rorapp.tests.test_helper import (
    check_latest_phase,
    check_old_actions_deleted,
    get_and_check_actions,
    submit_actions,
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

    def action_processor(self, action: Action) -> dict:
        if action.faction.player is None:
            raise ValueError("Player is None")
        faction = Faction.objects.filter(player=action.faction.player.id).get(
            game=action.faction.game.id
        )
        senators = Senator.objects.filter(faction=faction).order_by("name")
        first_senator = senators[0]
        return {"leader_id": first_senator.id}

    def do_faction_phase_test(self, player_count: int) -> None:
        game_id = self.setup_game_in_faction_phase(player_count)
        check_latest_phase(self, game_id, "Faction", 1)
        potential_actions_for_all_players = get_and_check_actions(
            self, game_id, False, "select_faction_leader", player_count
        )
        submit_actions(
            self,
            game_id,
            potential_actions_for_all_players,
            self.action_processor,
        )
        self.check_faction_leader_titles(game_id, player_count)
        check_latest_phase(self, game_id, "Mortality", 2)
        check_old_actions_deleted(self, game_id)

    def setup_game_in_faction_phase(self, player_count: int) -> int:
        game_id = generate_game(player_count)
        random.seed(1)
        start_game(game_id)
        self.assertEqual(Faction.objects.filter(game=game_id).count(), player_count)
        return game_id

    def check_faction_leader_titles(self, game_id: int, player_count: int) -> None:
        titles = Title.objects.filter(
            senator__faction__game=game_id, name="Faction Leader"
        )
        self.assertEqual(titles.count(), player_count)
