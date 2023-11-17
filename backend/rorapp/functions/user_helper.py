from django.contrib.auth.models import User


def find_or_create_test_user(user_number: int) -> User:
    try:
        user = User.objects.get(username=f"TestUser{user_number}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=f"TestUser{user_number}", password="password"
        )
    return user
