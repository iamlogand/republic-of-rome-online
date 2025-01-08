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
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Make a request to the API endpoint
        response = self.client.get("/api/users/")

        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 200)

        # Convert the response content to JSON
        response_json = json.loads(response.content.decode("utf-8"))

        # Check that the response JSON matches expectations
        self.assertEqual(len(response_json), 2)
        usernames = [user["username"] for user in response_json]
        self.assertTrue(self.user1.username in usernames)
        self.assertTrue(self.user2.username in usernames)
