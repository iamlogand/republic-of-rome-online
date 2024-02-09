import os
import json
import random
from collections import deque
from typing import List, Tuple
from django.db.models.query import QuerySet
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from rorapp.functions.forum_phase_helper import generate_select_faction_leader_action
from rorapp.functions.rank_helper import rank_senators_and_factions
from rorapp.functions.websocket_message_helper import (
    send_websocket_messages,
    create_websocket_message,
)
from rorapp.models import (
    ActionLog,
    Faction,
    Game,
    Phase,
    Player,
    Secret,
    Senator,
    SenatorActionLog,
    Situation,
    Step,
    Title,
    Turn,
    War,
)
from rorapp.serializers import (
    GameDetailSerializer,
    PhaseSerializer,
    StepSerializer,
    TurnSerializer,
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


def validate_game_start(game_id: int) -> Tuple[Game, List[Player]]:
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
    senators, unassigned_senator_names = create_senators(game, factions)
    assign_senators_to_factions(senators, factions)
    set_game_as_started(game)
    turn, phase, step = create_turn_phase_step(game)
    temp_rome_consul_title = assign_temp_rome_consul(senators, step)
    assign_prior_consul(temp_rome_consul_title, step)
    create_action_logs(temp_rome_consul_title, step)
    rank_senators_and_factions(game.id)
    create_actions(factions, step)
    wars_dict = create_situations_and_secrets(game, factions, unassigned_senator_names)
    create_first_punic_war(game, wars_dict)
    return game, turn, phase, step


def create_factions(game: Game, players: QuerySet[Player]) -> List[Faction]:
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


def create_senators(game: Game, factions: QuerySet[Faction]) -> List[str]:
    candidate_senators = load_candidate_senators(game)
    required_senator_count = len(factions) * 3
    random.shuffle(candidate_senators)

    # Discard some candidates, leaving only the required number of senators
    unassigned_senators = [
        senator.name for senator in candidate_senators[required_senator_count:]
    ]
    return candidate_senators[:required_senator_count], unassigned_senators


def load_candidate_senators(game: Game) -> List[Senator]:
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
    senators: List[Senator], factions: List[Faction]
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


def assign_temp_rome_consul(senators: List[Senator], step: Step) -> Title:
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


def assign_prior_consul(temp_rome_consul: Title, step: Step) -> None:
    prior_consul_title = Title(
        name="Prior Consul",
        senator=temp_rome_consul.senator,
        start_step=step,
        major_office=False,
    )
    prior_consul_title.save()


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
        generate_select_faction_leader_action(faction, step)


def create_situations_and_secrets(
    game: Game, factions: QuerySet[Faction], unassigned_senator_names: List[str]
) -> dict:
    situation_json_path = os.path.join(
        settings.BASE_DIR, "rorapp", "presets", "situation.json"
    )
    with open(situation_json_path, "r") as file:
        situations_dict = json.load(file)
    secret_situations = []
    for name, data in situations_dict.items():
        if data["type"] in ["concession", "intrigue"]:
            if "quantity" in data:
                for _ in range(data["quantity"]):
                    secret_situations.append(
                        Situation(
                            name=name,
                            type=data["type"],
                            secret=True,
                            game=game,
                            index=0,
                        )
                    )
            else:
                secret_situations.append(
                    Situation(
                        name=name, type=data["type"], secret=True, game=game, index=0
                    )
                )
    statesman_json_path = os.path.join(
        settings.BASE_DIR, "rorapp", "presets", "statesman.json"
    )
    with open(statesman_json_path, "r") as file:
        statesman_dict = json.load(file)
    secret_situations += [
        Situation(name=name, type="statesman", secret=True, game=game, index=0)
        for name, data in statesman_dict.items()
        if data["scenario"] == 1
    ]
    random.shuffle(secret_situations)
    secret_situations = deque(secret_situations)
    secrets = []
    for faction in factions:
        for _ in range(3):
            secret_situation = secret_situations.pop()
            secret = Secret(
                name=secret_situation.name,
                type=secret_situation.type,
                faction=faction,
            )
            secret.save()
            secrets.append(secret)
    situations = list(secret_situations)
    situations += [
        Situation(name=name, type=data["type"], secret=False, game=game, index=0)
        for name, data in situations_dict.items()
        if data["type"] == "leader"
    ]
    wars_json_path = os.path.join(settings.BASE_DIR, "rorapp", "presets", "war.json")
    with open(wars_json_path, "r") as file:
        wars_dict = json.load(file)
    situations += [
        Situation(name=title, type="war", secret=False, game=game, index=0)
        for title in wars_dict.keys()
        if title != "1st Punic War"
    ]
    situations += [
        Situation(name=name, type="senator", secret=False, game=game, index=0)
        for name in unassigned_senator_names
    ]
    random.shuffle(situations)
    for i, situation in enumerate(situations):
        situation.index = i
        situation.save()

    return wars_dict


def create_first_punic_war(game: Game, wars_dict: dict) -> None:
    data = wars_dict["1st Punic War"]
    first_punic_war = War(
        name=data["name"],
        index=data["index"],
        game=game,
        land_strength=data["land_strength"],
        fleet_support=data["fleet_support"],
        naval_strength=data["naval_strength"],
        disaster_numbers=data["disaster_numbers"],
        standoff_numbers=data["standoff_numbers"],
        spoils=data["spoils"],
        status="active" if data["immediately_active"] else "inactive",
        famine=data["famine"],
        naval_defeated=False if data["naval_strength"] > 0 else True,
    )
    first_punic_war.save()


def send_start_game_websocket_messages(
    game: Game, turn: Turn, phase: Phase, step: Step
):
    messages_to_send = [
        create_websocket_message("game", GameDetailSerializer(game).data),
        create_websocket_message("turn", TurnSerializer(turn).data),
        create_websocket_message("phase", PhaseSerializer(phase).data),
        create_websocket_message("step", StepSerializer(step).data),
    ]
    send_websocket_messages(game.id, messages_to_send)
    return Response({"message": "Game started"}, status=200)
