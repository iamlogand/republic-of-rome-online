import os
import json
import random
from typing import List, Tuple
from django.db.models.query import QuerySet
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from rorapp.functions.rank_helper import rank_senators_and_factions
from rorapp.functions.websocket_message_helper import (
    send_websocket_messages,
    create_websocket_message,
    update_websocket_message,
)
from rorapp.models import (
    Game,
    Player,
    Faction,
    Senator,
    Title,
    Turn,
    Phase,
    Step,
    Action,
    ActionLog,
    SenatorActionLog,
)
from rorapp.serializers import (
    GameDetailSerializer,
    TurnSerializer,
    PhaseSerializer,
    StepSerializer,
)


def user_start_game(game_id: int, user: User) -> Response:
    """
    Start an early republic scenario game as a user.

    Args:
        game_id (int): The game ID.
        user (User): The user starting the game.

    Returns:
        Response: The response with a message and a status code.

    """
    try:
        validate_user(game_id, user.id)
    except (NotFound, PermissionDenied) as e:
        return Response({"message": str(e)}, status=e.status_code)

    return start_game(game_id)


def start_game(
    game_id: int,
) -> Response:
    """
    Start an early republic scenario game anonymously.

    Args:
        game_id (int): The game ID.

    Returns:
        Response: The response with a message and a status code.
    """

    try:
        game, players = validate_game_start(game_id)
        game, turn, phase, step = setup_game(game, players)
        return send_start_game_websocket_messages(game, turn, phase, step)
    except (NotFound, PermissionDenied) as e:
        return Response({"message": str(e)}, status=e.status_code)


def validate_user(game_id: int, user_id: int) -> None:
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        raise NotFound("Game not found")
    if game.host.id != user_id:
        raise PermissionDenied("Only the host can start the game")


def validate_game_start(game_id: int) -> Tuple[Game, list[Player]]:
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        raise NotFound("Game not found")
    if Step.objects.filter(phase__turn__game__id=game.id).count() > 0:
        raise PermissionDenied("Game has already started")
    players = Player.objects.filter(game__id=game.id)
    if players.count() < 3:
        raise PermissionDenied("Game must have at least 3 players to start")

    return game, players


def setup_game(game: Game, players: QuerySet[Player]) -> Tuple[Game, Turn, Phase, Step]:
    factions = create_factions(game, players)
    senators = create_senators(game, players)
    assign_senators_to_factions(senators, factions)
    set_game_as_started(game)
    turn, phase, step = create_turn_phase_step(game)
    temp_rome_consul_title = assign_temp_rome_consul(senators, step)
    create_action_logs(temp_rome_consul_title, step)
    rank_senators_and_factions(game.id)
    create_actions(factions, step)
    return game, turn, phase, step


def create_factions(game: Game, players: QuerySet[Player]) -> list[Faction]:
    factions = []
    position = 1
    list_of_players = list(players)
    random.shuffle(list_of_players)
    position_exclusions = [4, 6, 2]
    positions_to_exclude = position_exclusions[: (6 - len(list_of_players))]
    for player in list_of_players:
        while position in positions_to_exclude:
            position += 1
        faction = Faction(game=game, position=position, player=player)
        faction.save()
        factions.append(faction)
        position += 1
    return factions


def create_senators(game: Game, factions: QuerySet[Faction]) -> list[Senator]:
    candidate_senators = load_candidate_senators(game)
    required_senator_count = len(factions) * 3
    random.shuffle(candidate_senators)

    # Discard some candidates, leaving only the required number of senators
    return candidate_senators[:required_senator_count]


def load_candidate_senators(game: Game) -> list[Senator]:
    senator_json_path = os.path.join(
        settings.BASE_DIR, "rorapp", "presets", "senator.json"
    )
    senators = []
    with open(senator_json_path, "r") as file:
        senators_dict = json.load(file)
    for senator_name, senator_data in senators_dict.items():
        if senator_data["scenario"] == 1:
            senator = Senator(
                name=senator_name,
                game=game,
                code=senator_data["code"],
                military=senator_data["military"],
                oratory=senator_data["oratory"],
                loyalty=senator_data["loyalty"],
                influence=senator_data["influence"],
            )
            senators.append(senator)
    return senators


def assign_senators_to_factions(
    senators: list[Senator], factions: list[Faction]
) -> None:
    senator_iterator = iter(senators)
    for faction in factions:
        for _ in range(3):
            senator = next(senator_iterator)
            senator.faction = faction
            senator.save()  # Save senators to DB


def set_game_as_started(game: Game) -> None:
    game.start_date = timezone.now()
    game.save()  # Update game to DB


def create_turn_phase_step(game: Game) -> Tuple[Turn, Phase, Step]:
    turn = Turn(index=1, game=game)
    turn.save()
    phase = Phase(name="Faction", index=0, turn=turn)
    phase.save()
    step = Step(index=0, phase=phase)
    step.save()
    return turn, phase, step


def assign_temp_rome_consul(senators: list[Senator], step: Step) -> Title:
    random.shuffle(senators)
    rome_consul = senators[0]
    temp_rome_consul_title = Title(
        name="Temporary Rome Consul",
        senator=rome_consul,
        start_step=step,
        major_office=True,
    )
    temp_rome_consul_title.save()
    rome_consul.influence += 5
    rome_consul.save()
    return temp_rome_consul_title


def create_action_logs(temp_rome_consul_title: Title, step: Step) -> None:
    action_log = ActionLog(
        index=0,
        step=step,
        type="temporary_rome_consul",
        faction=temp_rome_consul_title.senator.faction,
        data={"senator": temp_rome_consul_title.senator.id},
    )
    action_log.save()
    senator_action_log = SenatorActionLog(
        senator=temp_rome_consul_title.senator, action_log=action_log
    )
    senator_action_log.save()


def create_actions(factions: List[Faction], step: Step) -> None:
    for faction in factions:
        action = Action(
            step=step,
            faction=faction,
            type="select_faction_leader",
            required=True,
            parameters=None,
        )
        action.save()


def send_start_game_websocket_messages(
    game: Game, turn: Turn, phase: Phase, step: Step
):
    messages_to_send = [
        update_websocket_message("game", GameDetailSerializer(game).data),
        create_websocket_message("turn", TurnSerializer(turn).data),
        create_websocket_message("phase", PhaseSerializer(phase).data),
        create_websocket_message("step", StepSerializer(step).data),
    ]
    send_websocket_messages(game.id, messages_to_send)
    return Response({"message": "Game started"}, status=200)
