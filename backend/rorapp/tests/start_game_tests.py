from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rorapp.models import Game, Player, Faction, Senator, Title
from rorapp.functions.start_game import start_game, user_start_game


class StartGameTests(TestCase):
    def setUp(self):
        # Set up data for the tests - 6 users
        self.user1 = User.objects.create_user(username="User 1", password="Password")
        self.user2 = User.objects.create_user(username="User 2", password="Password")
        self.user3 = User.objects.create_user(username="User 3", password="Password")
        self.user4 = User.objects.create_user(username="User 4", password="Password")
        self.user5 = User.objects.create_user(username="User 5", password="Password")
        self.user6 = User.objects.create_user(username="User 6", password="Password")

        # Enables requests to API endpoints during testing
        self.client = APIClient()

    def test_start_game_api(self):
        self.client.force_authenticate(user=self.user1)

        # Create 4 games and add players
        sixPlayerGame = Game.objects.create(name="Game 1", host=self.user1)
        fivePlayerGame = Game.objects.create(name="Game 2", host=self.user1)
        fourPlayerGame = Game.objects.create(name="Game 3", host=self.user1)
        threePlayerGame = Game.objects.create(name="Game 4", host=self.user1)

        Player.objects.create(user=self.user1, game=sixPlayerGame)
        Player.objects.create(user=self.user2, game=sixPlayerGame)
        Player.objects.create(user=self.user3, game=sixPlayerGame)
        Player.objects.create(user=self.user4, game=sixPlayerGame)
        Player.objects.create(user=self.user5, game=sixPlayerGame)
        Player.objects.create(user=self.user6, game=sixPlayerGame)

        Player.objects.create(user=self.user1, game=fivePlayerGame)
        Player.objects.create(user=self.user2, game=fivePlayerGame)
        Player.objects.create(user=self.user3, game=fivePlayerGame)
        Player.objects.create(user=self.user4, game=fivePlayerGame)
        Player.objects.create(user=self.user5, game=fivePlayerGame)

        Player.objects.create(user=self.user1, game=fourPlayerGame)
        Player.objects.create(user=self.user2, game=fourPlayerGame)
        Player.objects.create(user=self.user3, game=fourPlayerGame)
        Player.objects.create(user=self.user4, game=fourPlayerGame)

        Player.objects.create(user=self.user1, game=threePlayerGame)
        Player.objects.create(user=self.user2, game=threePlayerGame)
        Player.objects.create(user=self.user3, game=threePlayerGame)

        # Define expectations for faction positions
        allExpectedPositions = [
            [1, 2, 3, 4, 5, 6],
            [1, 2, 3, 5, 6],
            [1, 2, 3, 5],
            [1, 3, 5],
        ]

        for game in [sixPlayerGame, fivePlayerGame, fourPlayerGame, threePlayerGame]:
            # Try to start game
            response = self.client.post(f"/api/games/{game.id}/start-game/")

            # Check that the response is 200 OK
            self.assertEqual(response.status_code, 200)

            # Check that the game has the correct number of factions and senators
            self.assertEqual(game.factions.count(), game.players.count())
            self.assertEqual(game.senators.count(), game.factions.count() * 3)

            # Check that the factions have the correct positions
            factions = Faction.objects.filter(game=game).order_by("position")
            expectedPositions = [
                positions
                for positions in allExpectedPositions
                if len(positions) == game.players.count()
            ][0]
            for i in range(len(factions)):
                self.assertEqual(
                    factions[i].position,
                    expectedPositions[i],
                    f"Game {game.id} has incorrect faction positions: item {i} is {factions[i].position} but should be {expectedPositions[i]}",
                )

            # Check that a Temporary Rome Consul has been assigned
            temp_rome_consuls = Title.objects.filter(
                senator__game=game, name="Temporary Rome Consul"
            )
            self.assertEqual(temp_rome_consuls.count(), 1)

    def test_start_game_ranks(self):
        # Create a game with 6 players
        game = Game.objects.create(name="Game 1", host=self.user1)
        Player.objects.create(user=self.user1, game=game)
        Player.objects.create(user=self.user2, game=game)
        Player.objects.create(user=self.user3, game=game)
        Player.objects.create(user=self.user4, game=game)
        Player.objects.create(user=self.user5, game=game)
        Player.objects.create(user=self.user6, game=game)

        # Allow user 1 to make authenticated requests
        self.client.force_authenticate(user=self.user1)

        # Start game A with a seed
        start_game(game.id, seed=1)

        # Check that the senators have been ranked correctly
        senators = Senator.objects.filter(game=game).order_by("rank")
        self.assertEqual(senators[0].name, "Papirius")
        self.assertEqual(senators[0].rank, 0)
        self.assertEqual(senators[1].name, "Cornelius")
        self.assertEqual(senators[1].rank, 1)
        self.assertEqual(senators[2].name, "Fabius")
        self.assertEqual(senators[2].rank, 2)

        # Check that the Temporary Rome Consul is the highest ranked senator
        temp_rome_consul = Title.objects.get(senator__game=game)
        self.assertEqual(temp_rome_consul.senator.name, "Papirius")

        # Check that the factions have been ranked correctly
        factions = Faction.objects.filter(game=game).order_by("rank")
        self.assertEqual(factions[0].player.user.username, "User 1")
        self.assertEqual(factions[0].rank, 0)
        self.assertEqual(factions[1].player.user.username, "User 5")
        self.assertEqual(factions[1].rank, 1)
        self.assertEqual(factions[2].player.user.username, "User 2")
        self.assertEqual(factions[2].rank, 2)

        # Check that the Temporary Rome Consul is in the highest ranked faction
        self.assertEqual(temp_rome_consul.senator.faction, factions[0])

    def test_start_game_api_errors(self):
        self.client.force_authenticate(user=self.user1)

        # Try to start a non-existent game
        response = self.client.post("/api/games/9999/start-game/")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["message"], "Game not found")

        # Try to start a game as a non-host
        otherUsersGame = Game.objects.create(name="Other Users Game", host=self.user2)
        response = self.client.post(f"/api/games/{otherUsersGame.id}/start-game/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["message"], "Only the host can start the game")

        # Try to start the game with less players than required
        thisUsersGame = Game.objects.create(name="This Users Game", host=self.user1)
        Player.objects.create(user=self.user1, game=thisUsersGame)
        response = self.client.post(f"/api/games/{thisUsersGame.id}/start-game/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["message"], "Game must have at least 3 players to start"
        )

        # Try to start a game that has already started
        Player.objects.create(user=self.user2, game=thisUsersGame)
        Player.objects.create(user=self.user3, game=thisUsersGame)
        user_start_game(thisUsersGame.id, self.user1, seed=1)
        response = self.client.post(f"/api/games/{thisUsersGame.id}/start-game/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["message"], "Game has already started")
