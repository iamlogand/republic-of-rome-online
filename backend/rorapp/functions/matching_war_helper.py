from typing import List
from rorapp.models import Game, War
from rorapp.serializers import WarSerializer


def update_matching_wars(game_id) -> List[dict]:
    """
    Update the matching wars field for all wars in a game.

    Returns a list of WebSocket messages with updated war data.
    """

    messages_to_send = []

    game = Game.objects.get(id=game_id)
    wars = War.objects.filter(game=game, status__in=["active", "unprosecuted"])
    for war in wars:
        matching_wars = war.matching_wars.all()
        updated_matching_wars = War.objects.filter(
            game=game, status__in=["active", "unprosecuted"], name=war.name
        ).exclude(id=war.id)
        if matching_wars != updated_matching_wars:
            war.matching_wars.set(updated_matching_wars)
        war.save()
        messages_to_send.append(WarSerializer(war).data)

    return messages_to_send
