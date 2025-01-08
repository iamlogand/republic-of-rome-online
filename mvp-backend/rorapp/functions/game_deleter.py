from rorapp.serializers.game import Game


def delete_all_games() -> int:
    """
    Deletes all games from the database.

    Returns:
        int: The number of games that were deleted.
    """

    games = Game.objects.all()
    count = games.count()
    games.delete()
    return count
