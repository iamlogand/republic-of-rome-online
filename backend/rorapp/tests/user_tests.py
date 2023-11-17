import json
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from rorapp.functions import find_or_create_test_user

class UserTests(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = find_or_create_test_user(1)
        self.user2 = find_or_create_test_user(2)

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
