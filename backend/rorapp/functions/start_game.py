import os
import json
import random
from typing import Tuple
from django.conf import settings
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from rorapp.functions.rank_senators_and_factions import rank_senators_and_factions
from rorapp.functions.send_websocket_messages import send_websocket_messages
from rorapp.functions.ws_message_create import ws_message_create
from rorapp.functions.ws_message_update import ws_message_update
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


def user_start_game(game_id, user, seed=None) -> Response:
    """
    Start and setup an early republic scenario game as a user.

    :param game: the game id
    :param faction: the user starting the game
    :param seed: seed for controlling "random" operations when testing

    :return: a response with a message and a status code
    :rtype: rest_framework.response.Response
    """
    try:
        validate_user(game_id, user)
    except (NotFound, PermissionDenied) as e:
        return Response({"message": str(e)}, status=e.status_code)

    return start_game(game_id, seed)


def start_game(game_id, seed=None) -> Response:
    """
    Start and setup an early republic scenario game anonymously.

    :param game: the game id
    :param seed: seed for controlling "random" operations when testing

    :return: a response with a message and a status code
    :rtype: rest_framework.response.Response
    """

    try:
        game, players = validate_game_start(game_id)
        game, turn, phase, step = setup_game(game, players, seed)
        return send_start_game_websocket_messages(game, turn, phase, step)
    except (NotFound, PermissionDenied) as e:
        return Response({"message": str(e)}, status=e.status_code)


def validate_user(game_id, user) -> None:
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        raise NotFound("Game not found")

    if game.host.id != user.id:
        raise PermissionDenied("Only the host can start the game")


def validate_game_start(game_id) -> Tuple[Game, list[Player]]:
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


def setup_game(game, players, seed) -> Tuple[Game, Turn, Phase, Step]:
    factions = create_factions(game, players, seed)
    senators = create_senators(game, players, seed)
    assign_senators_to_factions(senators, factions)
    set_game_as_started(game)

    turn, phase, step = create_turn_phase_step(game)
    temp_rome_consul_title = assign_temp_rome_consul(senators, step, seed)

    create_action_logs(temp_rome_consul_title, step)
    rank_senators_and_factions(game.id)
    create_actions(factions, step)

    return game, turn, phase, step


def create_factions(game, players, seed) -> list[Faction]:
    factions = []
    position = 1
    random.seed() if seed is None else random.seed(seed)
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


def create_senators(game, factions, seed) -> list[Senator]:
    candidate_senators = load_candidate_senators(game)

    required_senator_count = len(factions) * 3

    random.seed() if seed is None else random.seed(seed)
    random.shuffle(candidate_senators)

    # Discard some candidates, leaving only the required number of senators
    return candidate_senators[:required_senator_count]


def load_candidate_senators(game):
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


def assign_senators_to_factions(senators, factions) -> None:
    senator_iterator = iter(senators)
    for faction in factions:
        for _ in range(3):
            senator = next(senator_iterator)
            senator.faction = faction
            senator.save()  # Save senators to DB


def set_game_as_started(game) -> None:
    game.start_date = timezone.now()
    game.save()  # Update game to DB


def create_turn_phase_step(game) -> Tuple[Turn, Phase, Step]:
    turn = Turn(index=1, game=game)
    turn.save()
    phase = Phase(name="Faction", index=0, turn=turn)
    phase.save()
    step = Step(index=0, phase=phase)
    step.save()
    return turn, phase, step


def assign_temp_rome_consul(senators, step, seed) -> Title:
    random.seed() if seed is None else random.seed(seed)
    random.shuffle(senators)

    temp_rome_consul_title = Title(
        name="Temporary Rome Consul",
        senator=senators[0],
        start_step=step,
        major_office=True,
    )
    temp_rome_consul_title.save()
    return temp_rome_consul_title


def create_action_logs(temp_rome_consul_title, step) -> None:
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


def create_actions(factions, step) -> None:
    for faction in factions:
        action = Action(
            step=step,
            faction=faction,
            type="select_faction_leader",
            required=True,
            parameters=None,
        )
        action.save()


def send_start_game_websocket_messages(game, turn, phase, step):
    messages_to_send = [
        ws_message_update("game", GameDetailSerializer(game).data),
        ws_message_create("turn", TurnSerializer(turn).data),
        ws_message_create("phase", PhaseSerializer(phase).data),
        ws_message_create("step", StepSerializer(step).data),
    ]
    send_websocket_messages(game.id, messages_to_send)
    return Response({"message": "Game started"}, status=200)
