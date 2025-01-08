from django.contrib.auth.models import User


def find_or_create_test_user(user_number: int) -> User:
    """
    Find or create a test user.

    Args:
        user_number (int): The test user number (e.g. 1 for TestUser1)

    Returns:
        User: The test user.
    """
    try:
        user = User.objects.get(username=f"TestUser{user_number}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=f"TestUser{user_number}", password="password"
        )
    return user
