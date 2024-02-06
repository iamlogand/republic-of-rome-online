import os
import json
import random
from typing import List
from django.test import TestCase
from rest_framework.test import APIClient
from rorapp.functions import delete_all_games, generate_game, start_game
from rorapp.functions.faction_leader_helper import set_faction_leader
from rorapp.functions.forum_phase_starter import start_forum_phase
from rorapp.models import Action, ActionLog, Faction, Senator, Situation, Title
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
        """
        Ensure the forum phase generally works.
        """

        delete_all_games()
        for player_count in range(3, 7):
            self.do_forum_phase_test(player_count)

    def test_new_family(self) -> None:
        """
        Ensure that a new senator is created when the new family situation is initiated.
        """

        game_id, _ = self.setup_game_in_forum_phase(3)

        # Delete all non-senator situations to ensure that the next situation is a senator situation
        non_senator_situations = Situation.objects.filter(game=game_id).exclude(
            type="senator"
        )
        non_senator_situations.delete()

        # Ensure that there are no non-senator situations and the correct number of situations remain
        remaining_situations = Situation.objects.filter(game=game_id)
        # There should be 11 senator situations at the start of a 3-player game
        self.assertEqual(remaining_situations.count(), 11)
        for situation in remaining_situations:
            self.assertEqual(situation.type, "senator")

        original_senator_count = Senator.objects.filter(game=game_id).count()

        # Initiate senator situation
        check_latest_phase(self, game_id, "Forum")
        situation_potential_actions = get_and_check_actions(
            self, game_id, False, "initiate_situation", 1
        )
        submit_actions(
            self,
            game_id,
            situation_potential_actions,
            self.faction_leader_action_processor,
        )

        latest_action_log = (
            ActionLog.objects.filter(step__phase__turn__game=game_id)
            .order_by("index")
            .last()
        )
        self.assertEqual(latest_action_log.type, "new_family")

        new_senator_id = latest_action_log.data["senator"]
        new_senator = Senator.objects.get(id=new_senator_id)

        remaining_situations = Situation.objects.filter(game=game_id)
        self.assertEqual(remaining_situations.count(), 10)
        remaining_situation_senator_names = [
            situation.name for situation in remaining_situations
        ]
        self.assertNotIn(new_senator.name, remaining_situation_senator_names)

        new_senator_count = Senator.objects.filter(game=game_id).count()
        self.assertEqual(new_senator_count, original_senator_count + 1)

    def faction_leader_action_processor(self, action: Action) -> dict:
        faction = Faction.objects.filter(player=action.faction.player.id).get(
            game=action.faction.game.id
        )
        senators = Senator.objects.filter(faction=faction).order_by("name")
        first_senator = senators[0]
        return {"leader_id": first_senator.id}

    def do_forum_phase_test(self, player_count: int) -> None:
        game_id, faction_ids_with_leadership = self.setup_game_in_forum_phase(
            player_count
        )

        # Ensure that the game starts with correct number of situations
        situations = Situation.objects.filter(game=game_id)
        self.assertEqual(situations.count(), 64 - player_count * 6)

        for _ in range(0, player_count):
            check_latest_phase(self, game_id, "Forum")
            situation_potential_actions = get_and_check_actions(
                self, game_id, False, "initiate_situation", 1
            )
            submit_actions(
                self,
                game_id,
                situation_potential_actions,
                self.faction_leader_action_processor,
            )
            check_latest_phase(self, game_id, "Forum")
            faction_leader_potential_actions = get_and_check_actions(
                self, game_id, False, "select_faction_leader", 1
            )
            faction_leader_titles = Title.objects.filter(
                name="Faction Leader",
                senator__faction=faction_leader_potential_actions[0].faction,
                end_step=None,
            )

            # If the faction already has a leader, then there should be no existing faction leader title.
            self.assertEqual(
                len(faction_leader_titles),
                1
                if faction_leader_potential_actions[0].faction.id
                in faction_ids_with_leadership
                else 0,
            )
            submit_actions(
                self,
                game_id,
                faction_leader_potential_actions,
                self.faction_leader_action_processor,
            )
            faction_leader_titles = Title.objects.filter(
                name="Faction Leader",
                senator__faction=faction_leader_potential_actions[0].faction,
                end_step=None,
            )
            self.assertEqual(len(faction_leader_titles), 1)
        check_latest_phase(self, game_id, "Mortality")
        check_old_actions_deleted(self, game_id)

    def setup_game_in_forum_phase(self, player_count: int) -> (int, List[int]):
        self.client = APIClient()
        random.seed(1)
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
    senator_in_faction_1 = Senator.objects.filter(
        game=game_id, faction=first_faction
    ).first()
    senator_in_faction_2 = Senator.objects.filter(
        game=game_id, faction=second_faction
    ).first()
    set_faction_leader(senator_in_faction_1.id)
    set_faction_leader(senator_in_faction_2.id)
    return [
        senator_in_faction_1.faction.id,
        senator_in_faction_2.faction.id,
    ]
