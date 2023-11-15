import json
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

class UserTests(TestCase):
    
    def setUp(self):
        
        # Set up data for the tests
        # Use `create_user()` instead of `create()` to automatically hash the password
        self.user1 = User.objects.create_user(username='User 1', password='Password')
        self.user2 = User.objects.create_user(username='User 2', password='Password')
        
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
        
        # Convert the response content to JSON
        response_json = json.loads(response.content.decode('utf-8'))

        # Check that the response JSON matches expectations
        self.assertEqual(response_json[0]['username'], self.user1.username)
        self.assertEqual(response_json[1]['username'], self.user2.username)
