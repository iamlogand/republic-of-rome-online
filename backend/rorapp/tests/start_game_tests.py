from django.test import TestCase
from rest_framework.test import APIClient
from rorapp.functions import generate_game
from rorapp.models import Game, Player, Faction, Senator, Title
from rorapp.functions import delete_all_games, find_or_create_test_user, start_game, user_start_game


class StartGameTests(TestCase):
    """
    These tests check that the start game API endpoint works as expected.
    """

    def setUp(self):
        delete_all_games()
        self.user_1 = find_or_create_test_user(1)
        self.user_2 = find_or_create_test_user(2)
        self.user_3 = find_or_create_test_user(3)

        # Enables requests to API endpoints during testing
        self.client = APIClient()

    def test_start_game_api(self):
        six_player_game_id = generate_game(6)
        five_player_game_id = generate_game(5)
        four_player_game_id = generate_game(4)
        three_player_game_id = generate_game(3)

        self.client.force_authenticate(user=self.user_1)

        # Define expectations for faction positions
        allExpectedPositions = [
            [1, 2, 3, 4, 5, 6],
            [1, 2, 3, 5, 6],
            [1, 2, 3, 5],
            [1, 3, 5],
        ]

        for game_id in [
            six_player_game_id,
            five_player_game_id,
            four_player_game_id,
            three_player_game_id,
        ]:
            game = Game.objects.get(id=game_id)

            # Try to start game
            response = self.client.post(f"/api/games/{game_id}/start-game/")

            # Check that the response is 200 OK
            self.assertEqual(response.status_code, 200)

            # Check that the game has the correct number of factions and senators
            self.assertEqual(game.factions.count(), game.players.count())
            self.assertEqual(game.senators.count(), game.factions.count() * 3)

            # Check that the factions have the correct positions
            factions = Faction.objects.filter(game=game_id).order_by("position")
            expectedPositions = [
                positions
                for positions in allExpectedPositions
                if len(positions) == game.players.count()
            ][0]
            for i in range(len(factions)):
                self.assertEqual(
                    factions[i].position,
                    expectedPositions[i],
                    f"Game {game_id} has incorrect faction positions: item {i} is {factions[i].position} but should be {expectedPositions[i]}",
                )

            # Check that a Temporary Rome Consul has been assigned
            temp_rome_consuls = Title.objects.filter(
                senator__game=game_id, name="Temporary Rome Consul"
            )
            self.assertEqual(temp_rome_consuls.count(), 1)

    def test_start_game_ranks(self):
        # Create a game with 6 players
        game_id = generate_game(6)

        # Allow user 1 to make authenticated requests
        self.client.force_authenticate(user=self.user_1)

        # Start game A with a seed
        start_game(game_id, seed=1)

        # Check that the senators have been ranked correctly
        senators = Senator.objects.filter(game=game_id).order_by("rank")
        self.assertEqual(senators[0].name, "Papirius")
        self.assertEqual(senators[0].rank, 0)
        self.assertEqual(senators[1].name, "Cornelius")
        self.assertEqual(senators[1].rank, 1)
        self.assertEqual(senators[2].name, "Fabius")
        self.assertEqual(senators[2].rank, 2)

        # Check that the Temporary Rome Consul is the highest ranked senator
        temp_rome_consul = Title.objects.get(senator__game=game_id)
        self.assertEqual(temp_rome_consul.senator.name, "Papirius")
        self.assertEqual(temp_rome_consul.senator.influence, 8)  # 3 base + 5 consulship

        # Check that the factions have been ranked correctly
        factions = Faction.objects.filter(game=game_id).order_by("rank")
        self.assertEqual(factions[0].player.user.username, "TestUser1")
        self.assertEqual(factions[0].rank, 0)
        self.assertEqual(factions[1].player.user.username, "TestUser5")
        self.assertEqual(factions[1].rank, 1)
        self.assertEqual(factions[2].player.user.username, "TestUser2")
        self.assertEqual(factions[2].rank, 2)

        # Check that the Temporary Rome Consul is in the highest ranked faction
        self.assertEqual(temp_rome_consul.senator.faction, factions[0])

    def test_start_game_api_errors(self):
        self.client.force_authenticate(user=self.user_1)

        # Try to start a non-existent game
        response = self.client.post("/api/games/9999/start-game/")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["message"], "Game not found")

        # Try to start a game as a non-host
        other_users_game_id = generate_game(3, self.user_2.id)
        response = self.client.post(f"/api/games/{other_users_game_id}/start-game/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["message"], "Only the host can start the game")

        # Try to start the game with less players than required
        this_users_game_id = generate_game(1)
        this_users_game = Game.objects.get(id=this_users_game_id)
        response = self.client.post(f"/api/games/{this_users_game_id}/start-game/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["message"], "Game must have at least 3 players to start"
        )

        # Try to start a game that has already started
        Player.objects.create(user=self.user_2, game=this_users_game)
        Player.objects.create(user=self.user_3, game=this_users_game)
        user_start_game(this_users_game_id, self.user_1, seed=1)
        response = self.client.post(f"/api/games/{this_users_game_id}/start-game/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["message"], "Game has already started")
