import json
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

class UsersViewSetTest(TestCase):
    
    # Set up data for the tests
    def setUp(self):
        
        # Use `create_user()` instead of `create()` to automatically hash the password
        self.user1 = User.objects.create_user(username='testuser1', password='testpass1')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass2')
        
        # Enables requests to API endpoints during testing
        self.client = APIClient()

    def test_get_all_users(self):
        # Get a token for the test user
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Make a request to the API endpoint
        response = self.client.get('/api/users/')

        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Define the expected JSON response
        expected_json = json.dumps([
            {'username': self.user1.username},
            {'username': self.user2.username}
        ])
        
        # Convert the response content to JSON
        response_json = response.content.decode('utf-8')

        # Check that the response JSON matches the expected JSON
        self.assertEqual(json.loads(response_json), json.loads(expected_json))
