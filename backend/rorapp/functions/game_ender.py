from django.utils import timezone
from rorapp.functions.progress_helper import get_latest_step
from rorapp.models import Game
from rorapp.functions.websocket_message_helper import create_websocket_message
from rorapp.models.action_log import ActionLog
from rorapp.models.faction import Faction
from rorapp.models.senator import Senator
from rorapp.serializers import GameDetailSerializer
from rorapp.serializers.action_log import ActionLogSerializer


def end_game_with_influence_victory(game_id: int) -> list[dict]:
    messages_to_send = []

    winning_faction = find_influence_winner(game_id)

    latest_step = get_latest_step(game_id)
    new_action_log_index = (
        ActionLog.objects.filter(step__phase__turn__game=game_id)
        .order_by("-index")[0]
        .index
        + 1
    )
    faction_wins_action_log = ActionLog(
        index=new_action_log_index,
        step=latest_step,
        type="faction_wins",
        faction=winning_faction,
        data={"type": "influence"},
    )
    faction_wins_action_log.save()
    messages_to_send.append(
        create_websocket_message(
            "action_log", ActionLogSerializer(faction_wins_action_log).data
        )
    )
    messages_to_send.append(end_game(game_id))

    return messages_to_send


def end_game(game_id: int) -> dict:
    game = Game.objects.get(id=game_id)
    game.end_date = timezone.now()
    game.save()
    return create_websocket_message("game", GameDetailSerializer(game).data)


def find_influence_winner(game_id: int) -> Faction:
    factions = Faction.objects.filter(game=game_id)
    winning_faction = None
    current_highest_influence = 0
    current_highest_senator_influence = 0
    current_highest_votes = 0
    for faction in factions:
        senators = Senator.objects.filter(alive=True, faction=faction).order_by(
            "-influence"
        )
        highest_senator = senators.first()
        assert isinstance(highest_senator, Senator)
        highest_senator_influence = highest_senator.influence
        influence = 0
        votes = 0
        for senator in senators:
            influence += senator.influence
            votes += senator.votes

        # Highest influence wins
        if influence > current_highest_influence:
            winning_faction = faction
            current_highest_influence = influence
            current_highest_senator_influence = highest_senator_influence
            current_highest_votes = votes

        # Tiebreaker: highest influence on an individual senator
        elif (
            influence == current_highest_influence
            and highest_senator_influence > current_highest_senator_influence
        ):
            winning_faction = faction
            current_highest_influence = influence
            current_highest_senator_influence = highest_senator_influence
            current_highest_votes = votes

        # Second tiebreaker: highest votes
        elif (
            influence == current_highest_influence
            and highest_senator_influence == current_highest_senator_influence
            and votes > current_highest_votes
        ):
            winning_faction = faction
            current_highest_influence = influence
            current_highest_senator_influence = highest_senator_influence
            current_highest_votes = votes

    assert isinstance(winning_faction, Faction), "No winning faction found"
    return winning_faction
