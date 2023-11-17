import uuid
from django.db import transaction
from django.contrib.auth.models import User
from rorapp.models import Game, Player
from rorapp.functions.user_helper import find_or_create_test_user


@transaction.atomic
def generate_game(player_count: int, host_user_id: int | None = None) -> int:
    """
    This function generates a game with the given number of players.

    Intended for development and testing use only.
    Test users are created if they do not already exist.
    The format for test usernames is "TestUser{number}" and all passwords are set to "password".

    Args:
        player_count (int): The number of players, must be no more than 6.
        host_user_id (int | None): The ID of the user who will host the game. If None, the host will be a test user.

    Returns:
        int: The game ID.
    """
    game_id = create_game(host_user_id)
    populate_game(game_id, player_count)
    return game_id


def create_game(host_user_id: int | None) -> int:
    if host_user_id is None:
        user = find_or_create_test_user(1)
    else:
        user = User.objects.get(id=host_user_id)
    game = Game(name=f"Test Game {str(uuid.uuid4())}", host=user)
    game.save()
    return game.id


def populate_game(game_id: int, player_count: int) -> None:
    validate_player_count(player_count)
    game = Game.objects.get(id=game_id)
    for user_number in range(1, player_count + 1):
        user = find_or_create_test_user(user_number)
        player = Player(user=user, game=game)
        player.save()


def validate_player_count(player_count: int) -> None:
    if player_count > 6:
        raise ValueError("Player count must be no more than 6")
