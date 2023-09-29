from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rorapp.models import Game, Player, Title


class StartGameTests(TestCase):
    
    def setUp(self):
        
        # Set up data for the tests - 4 games with a variety of player counts for each
        self.user1 = User.objects.create_user(username='User 1', password='Password')
        self.user2 = User.objects.create_user(username='User 2', password='Password')
        self.user3 = User.objects.create_user(username='User 3', password='Password')
        self.user4 = User.objects.create_user(username='User 4', password='Password')
        self.user5 = User.objects.create_user(username='User 5', password='Password')
        self.user6 = User.objects.create_user(username='User 6', password='Password')

        self.gameA = Game.objects.create(name='Game 1', host=self.user1)
        self.gameB = Game.objects.create(name='Game 2', host=self.user1)
        self.gameC = Game.objects.create(name='Game 3', host=self.user1)
        self.gameD = Game.objects.create(name='Game 4', host=self.user1)
        
        self.player1A = Player.objects.create(user=self.user1, game=self.gameA)
        self.player2A = Player.objects.create(user=self.user2, game=self.gameA)
        self.player3A = Player.objects.create(user=self.user3, game=self.gameA)
        self.player4A = Player.objects.create(user=self.user4, game=self.gameA)
        self.player5A = Player.objects.create(user=self.user5, game=self.gameA)
        self.player6A = Player.objects.create(user=self.user6, game=self.gameA)
        
        self.player1B = Player.objects.create(user=self.user1, game=self.gameB)
        self.player2B = Player.objects.create(user=self.user2, game=self.gameB)
        self.player3B = Player.objects.create(user=self.user3, game=self.gameB)
        self.player4B = Player.objects.create(user=self.user4, game=self.gameB)
        self.player5B = Player.objects.create(user=self.user5, game=self.gameB)
        
        self.player1C = Player.objects.create(user=self.user1, game=self.gameC)
        self.player2C = Player.objects.create(user=self.user2, game=self.gameC)
        self.player3C = Player.objects.create(user=self.user3, game=self.gameC)
        self.player4C = Player.objects.create(user=self.user4, game=self.gameC)
        
        self.player1D = Player.objects.create(user=self.user1, game=self.gameD)
        self.player2D = Player.objects.create(user=self.user2, game=self.gameD)
        self.player3D = Player.objects.create(user=self.user3, game=self.gameD)

        # Enables requests to API endpoints during testing
        self.client = APIClient()

    def test_start_game(self):
        
        # Allow user 1 to make authenticated requests
        self.client.force_authenticate(user=self.user1)
        
        for game in [self.gameA, self.gameB, self.gameC, self.gameD]:
            
            # Try to start game
            response = self.client.post(f'/api/games/{game.id}/start-game/')
            
            # Check that the response is 200 OK
            self.assertEqual(response.status_code, 200)
            
            # Check that the game has the correct number of factions and senators
            self.assertEqual(game.factions.count(), game.players.count())
            self.assertEqual(game.senators.count(), game.factions.count() * 3)
            
            # Check that a Temporary Rome Consul has been assigned
            temp_rome_consuls = Title.objects.filter(senator__game=game, name='Temporary Rome Consul')
            self.assertEqual(temp_rome_consuls.count(), 1)
