import os
import json
import random
from django.conf import settings
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rorapp.functions import rank_senators_and_factions
from rorapp.models import Game, Player, Faction, Senator, Title, Turn, Phase, Step, PotentialAction, ActionLog, SenatorActionLog
from rorapp.serializers import GameDetailSerializer, TurnSerializer, PhaseSerializer, StepSerializer


def start_game(game_id, user, seed=None):
    '''
    Start and setup an early republic scenario game.
    
    :param game: the game id
    :param faction: the user starting the game
    :param seed: seed for controlling "random" operations when testing
    
    :return: a response with a message and a status code
    :rtype: rest_framework.response.Response
    '''
    
    try:
        game, players = validate_game_start(game_id, user)
        game, turn, phase, step = setup_game(game, players, seed)
        return send_websocket_messages(game, turn, phase, step)
    except (NotFound, PermissionDenied) as e:
        return Response({"message": str(e)}, status=e.status_code)


def validate_game_start(game_id, user):
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        raise NotFound("Game not found")
    
    if game.host.id != user.id:
        raise PermissionDenied("Only the host can start the game")
    
    if Step.objects.filter(phase__turn__game__id=game.id).count() > 0:
        raise PermissionDenied("Game has already started")
    
    players = Player.objects.filter(game__id=game.id)
    if players.count() < 3:
        raise PermissionDenied("Game must have at least 3 players to start")
    
    return game, players


def setup_game(game, players, seed):
    factions = create_factions(game, players, seed)
    senators = create_senators(game, players, seed)
    assign_senators_to_factions(senators, factions)
    set_game_as_started(game)
    
    turn, phase, step = create_turn_phase_step(game)
    temp_rome_consul_title = assign_temp_rome_consul(senators, step, seed)

    create_action_logs(temp_rome_consul_title, step)
    rank_senators_and_factions(game.id)
    create_potential_actions(factions, step)

    return game, turn, phase, step


def create_factions(game, players, seed):
    factions = []
    position = 1
    random.seed() if seed is None else random.seed(seed)
    list_of_players = list(players)
    random.shuffle(list_of_players)

    for player in list_of_players:
        faction = Faction(game=game, position=position, player=player)
        faction.save()  # Save factions to DB
        factions.append(faction)
        position += 1
    return factions


def create_senators(game, factions, seed):
    candidate_senators = load_candidate_senators(game)
    
    required_senator_count = len(factions) * 3
    
    random.seed() if seed is None else random.seed(seed)
    random.shuffle(candidate_senators)
    
    # Discard some candidates, leaving only the required number of senators
    return candidate_senators[:required_senator_count]


def load_candidate_senators(game):
    senator_json_path = os.path.join(settings.BASE_DIR, 'rorapp', 'presets', 'senator.json')
    senators = []
    with open(senator_json_path, 'r') as file:
        senators_dict = json.load(file)
        
    for senator_name, senator_data in senators_dict.items():
        if senator_data['scenario'] == 1:
            senator = Senator(
                name=senator_name,
                game=game,
                code=senator_data['code'],
                military=senator_data['military'],
                oratory=senator_data['oratory'],
                loyalty=senator_data['loyalty'],
                influence=senator_data['influence']
            )
            senators.append(senator)
    return senators


def assign_senators_to_factions(senators, factions):
    senator_iterator = iter(senators)
    for faction in factions:
        for _ in range(3):
            senator = next(senator_iterator)
            senator.faction = faction
            senator.save()  # Save senators to DB


def set_game_as_started(game):
    game.start_date = timezone.now()
    game.save()  # Update game to DB


def create_turn_phase_step(game):
    turn = Turn(index=1, game=game)
    turn.save()
    phase = Phase(name="Faction", index=0, turn=turn)
    phase.save()
    step = Step(index=0, phase=phase)
    step.save()
    return turn, phase, step


def assign_temp_rome_consul(senators, step, seed):
    random.seed() if seed is None else random.seed(seed)
    random.shuffle(senators)
    
    temp_rome_consul_title = Title(
        name="Temporary Rome Consul",
        senator=senators[0],
        start_step=step,
        major_office=True
    )
    temp_rome_consul_title.save()
    return temp_rome_consul_title


def create_action_logs(temp_rome_consul_title, step):
    action_log = ActionLog(
        index=0,
        step=step,
        type="temporary_rome_consul",
        faction=temp_rome_consul_title.senator.faction,
        data={"senator": temp_rome_consul_title.senator.id}
    )
    action_log.save()
    
    senator_action_log = SenatorActionLog(
        senator=temp_rome_consul_title.senator,
        action_log=action_log
    )
    senator_action_log.save()


def create_potential_actions(factions, step):
    for faction in factions:
        action = PotentialAction(
            step=step,
            faction=faction,
            type="select_faction_leader",
            required=True,
            parameters=None
        )
        action.save()


def send_websocket_messages(game, turn, phase, step):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"game_{game.id}",
        {
            "type": "game_update",
            "messages": [
                {
                    "operation": "update",
                    "instance": {
                        "class": "game",
                        "data": GameDetailSerializer(game).data
                    }
                },
                {
                    "operation": "create",
                    "instance": {
                        "class": "turn",
                        "data": TurnSerializer(turn).data
                    }
                },
                {
                    "operation": "create",
                    "instance": {
                        "class": "phase",
                        "data": PhaseSerializer(phase).data
                    }
                },
                {
                    "operation": "create",
                    "instance": {
                        "class": "step",
                        "data": StepSerializer(step).data
                    }
                }
            ]
        }
    )
    
    return Response({"message": "Game started"}, status=200)
