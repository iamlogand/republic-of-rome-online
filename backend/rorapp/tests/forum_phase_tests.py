import random
from typing import List
from django.test import TestCase
from rest_framework.test import APIClient
from rorapp.functions import delete_all_games, generate_game, start_game
from rorapp.functions.faction_leader_helper import set_faction_leader
from rorapp.functions.forum_phase_starter import start_forum_phase
from rorapp.models import Action, Faction, Senator, Title
from rorapp.tests.test_helper import (
    check_latest_phase,
    check_old_actions_deleted,
    get_and_check_actions,
    submit_actions,
)


class ForumPhaseTests(TestCase):
    """
    Ensure that players can select their faction leader during the forum phase.
    """

    def test_forum_phase(self) -> None:
        self.client = APIClient()
        delete_all_games()
        for player_count in range(3, 7):
            self.do_forum_phase_test(player_count)

    def action_processor(self, action: Action) -> dict:
        faction = Faction.objects.filter(player=action.faction.player.id).get(
            game=action.faction.game.id
        )
        senators = Senator.objects.filter(faction=faction).order_by("name")
        first_senator = senators[0]
        return {"leader_id": first_senator.id}

    def do_forum_phase_test(self, player_count: int) -> None:
        random.seed(1)
        game_id, faction_ids_with_leadership = self.setup_game_in_forum_phase(player_count)
        for _ in range(0, player_count):
            check_latest_phase(self, game_id, "Forum")
            potential_actions = get_and_check_actions(
                self, game_id, False, "select_faction_leader", 1
            )
            self.assertEqual(len(potential_actions), 1)
            faction_leader_titles = Title.objects.filter(
                name="Faction Leader",
                senator__faction=potential_actions[0].faction,
                end_step=None
            )
            
            # If the faction already has a leader, then there should be no existing faction leader title.
            self.assertEqual(len(faction_leader_titles), 1 if potential_actions[0].faction.id in faction_ids_with_leadership else 0)
            submit_actions(
                self,
                game_id,
                potential_actions,
                self.action_processor,
            )
            self.assertEqual(len(potential_actions), 1)
            faction_leader_titles = Title.objects.filter(
                name="Faction Leader",
                senator__faction=potential_actions[0].faction,
                end_step=None
            )
            self.assertEqual(len(faction_leader_titles), 1)
        check_latest_phase(self, game_id, "Mortality")
        check_old_actions_deleted(self, game_id)

    def setup_game_in_forum_phase(self, player_count: int) -> (int, List[int]):
        game_id = generate_game(player_count)
        start_game(game_id)
        faction_ids_with_leadership = set_some_faction_leaders(game_id)
        start_forum_phase(game_id)
        return (game_id, faction_ids_with_leadership)
    
def set_some_faction_leaders(game_id: int) -> List[int]:
    """
    Assigns faction leader titles to 2 senators then returns their faction IDs.
    """
    factions = Faction.objects.filter(game=game_id)
    first_faction = factions.first()
    second_faction = factions.last()
    senator_in_faction_1 = Senator.objects.filter(game=game_id, faction=first_faction).first()
    senator_in_faction_2 = Senator.objects.filter(game=game_id, faction=second_faction).first()
    set_faction_leader(senator_in_faction_1.id)
    set_faction_leader(senator_in_faction_2.id)
    return [
        senator_in_faction_1.faction.id,
        senator_in_faction_2.faction.id,
    ]

