from typing import List
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rorapp.functions import delete_all_games, generate_game, start_game
from rorapp.models import Action, Faction, Phase, Player, Senator, Title


class FactionPhaseTests(TestCase):
    """
    These tests check that players can select their first faction leader during the faction phase.
    """
    
    def setUp(self):
        delete_all_games()

    def test_faction_phase(self):
        # Create 4 games with 3, 4, 5, and 6 players
        game_ids = []
        for player_count in range(3, 7):
            game_id = generate_game(player_count)
            start_game(game_id, seed=1)
            game_ids.append(game_id)
        self.game_ids: List[int] = game_ids

        for game_id in self.game_ids:
            player_count = Player.objects.filter(game=game_id).count()

            # Ensure phase is correct
            phases = Phase.objects.filter(turn__game=game_id)
            self.assertEqual(phases.count(), 1)
            latest_phase = phases[0]
            self.assertEqual(latest_phase.name, "Faction")

            # Ensure potential actions are correct
            potential_actions_for_all_players = Action.objects.filter(
                step__phase__turn__game=game_id, completed=False
            )
            self.assertEqual(potential_actions_for_all_players.count(), player_count)
            faction_ids_with_correct_action = []
            for action in potential_actions_for_all_players:
                self.assertEqual(action.type, "select_faction_leader")
                faction_ids_with_correct_action.append(action.faction.id)
            self.assertEqual(len(set(faction_ids_with_correct_action)), player_count)

            # Submit actions to select faction leaders
            for player_number in range(1, player_count + 1):
                user = User.objects.get(username=f"TestUser{player_number}")
                user_faction_id = (
                    Faction.objects.filter(player__user=user).get(game=game_id).id
                )
                user_potential_action_id = potential_actions_for_all_players.get(
                    faction=user_faction_id
                ).id
                user_senators = Senator.objects.filter(
                    faction=user_faction_id
                ).order_by("name")
                user_first_senator_id = user_senators[0].id

                self.client = APIClient()
                self.client.force_authenticate(user=user)
                response = self.client.post(
                    f"/api/games/{game_id}/submit-action/{user_potential_action_id}/",
                    data={"leader_id": user_first_senator_id},
                )
                self.assertEqual(response.status_code, 200)

            # Ensure actions are completed
            potential_actions_for_all_players = Action.objects.filter(
                step__phase__turn__game=game_id,
                completed=False,
                type="select_faction_leader",
            )
            self.assertEqual(potential_actions_for_all_players.count(), 0)
            completed_actions_for_all_players = Action.objects.filter(
                step__phase__turn__game=game_id, completed=True
            )
            self.assertEqual(completed_actions_for_all_players.count(), player_count)

            # Ensure faction leader titles have been assigned
            titles = Title.objects.filter(
                senator__faction__game=game_id, name="Faction Leader"
            )
            self.assertEqual(titles.count(), player_count)

            # Ensure phase is mortality
            phases = Phase.objects.filter(turn__game=game_id).order_by("-index")
            self.assertEqual(phases.count(), 2)
            latest_phase = phases[0]
            self.assertEqual(latest_phase.name, "Mortality")
