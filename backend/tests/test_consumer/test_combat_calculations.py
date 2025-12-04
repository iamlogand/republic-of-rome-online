import pytest
import pytest_asyncio
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from rorapp.consumers.game import GameConsumer
from rorapp.models import Game, Faction, CombatCalculation


@pytest_asyncio.fixture
async def game_with_players():
    host = await database_sync_to_async(User.objects.create_user)(
        username="host_fixture", password="password"
    )
    game = await database_sync_to_async(Game.objects.create)(
        name="Test Game Fixture", host=host
    )
    player1 = await database_sync_to_async(User.objects.create_user)(
        username="player1_fixture", password="password"
    )
    await database_sync_to_async(Faction.objects.create)(
        game=game, player=player1, position=1
    )
    player2 = await database_sync_to_async(User.objects.create_user)(
        username="player2_fixture", password="password"
    )
    await database_sync_to_async(Faction.objects.create)(
        game=game, player=player2, position=2
    )
    return {"game": game, "player1": player1, "player2": player2}


@pytest_asyncio.fixture
async def spectator():
    return await database_sync_to_async(User.objects.create_user)(
        username="spectator_fixture", password="password"
    )


def create_communicator(game_id, user):
    communicator = WebsocketCommunicator(GameConsumer.as_asgi(), f"/ws/game/{game_id}/")
    communicator.scope["user"] = user
    communicator.scope["url_route"] = {"kwargs": {"game_id": game_id}}
    return communicator


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_combat_calculations_player_read(game_with_players):

    # Arrange
    game = game_with_players["game"]
    player1 = game_with_players["player1"]
    player2 = game_with_players["player2"]

    await database_sync_to_async(CombatCalculation.objects.create)(
        game=game, name="Initial Calculation", land_battle=True, regular_legions=2
    )

    sender = create_communicator(game.id, player1)
    receiver = create_communicator(game.id, player2)

    await sender.connect()
    await receiver.connect()
    await sender.receive_json_from()

    initial_load = await receiver.receive_json_from()
    assert "combat_calculations" in initial_load
    assert len(initial_load["combat_calculations"]) == 1
    assert initial_load["combat_calculations"][0]["name"] == "Initial Calculation"

    # Act
    await sender.send_json_to(
        {
            "combat_calculations": [
                {"name": "Updated Calculation", "land_battle": False, "fleets": 3}
            ]
        }
    )

    # Assert
    broadcast = await receiver.receive_json_from()
    assert "combat_calculations" in broadcast
    assert len(broadcast["combat_calculations"]) == 1
    assert broadcast["combat_calculations"][0]["name"] == "Fleets"

    await sender.disconnect()
    await receiver.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_combat_calculations_spectator_read(game_with_players, spectator):

    # Arrange
    game = game_with_players["game"]
    player = game_with_players["player1"]

    await database_sync_to_async(CombatCalculation.objects.create)(
        game=game, name="Initial Calculation", land_battle=True, regular_legions=2
    )

    sender = create_communicator(game.id, player)
    receiver = create_communicator(game.id, spectator)

    await sender.connect()
    await receiver.connect()
    await sender.receive_json_from()

    initial_load = await receiver.receive_json_from()
    assert "combat_calculations" in initial_load
    assert len(initial_load["combat_calculations"]) == 1
    assert initial_load["combat_calculations"][0]["name"] == "Initial Calculation"

    # Act
    await sender.send_json_to(
        {
            "combat_calculations": [
                {"name": "Updated Calculation", "land_battle": False, "fleets": 3}
            ]
        }
    )

    # Assert
    broadcast = await receiver.receive_json_from()
    assert "combat_calculations" in broadcast
    assert len(broadcast["combat_calculations"]) == 1
    assert broadcast["combat_calculations"][0]["name"] == "Fleets"

    await sender.disconnect()
    await receiver.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_combat_calculations_player_write(game_with_players):

    # Arrange
    game = game_with_players["game"]
    player = game_with_players["player1"]
    communicator = create_communicator(game.id, player)
    connected, _ = await communicator.connect()
    assert connected

    # Act
    await communicator.send_json_to(
        {
            "combat_calculations": [
                {
                    "name": "Test Calculation",
                    "land_battle": True,
                    "regular_legions": 5,
                }
            ]
        }
    )

    # Assert
    await communicator.disconnect()

    calc_count = await database_sync_to_async(
        CombatCalculation.objects.filter(game=game).count
    )()
    assert calc_count == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_combat_calculations_spectator_write(game_with_players, spectator):

    # Arrange
    game = game_with_players["game"]
    communicator = create_communicator(game.id, spectator)
    connected, _ = await communicator.connect()
    assert connected

    # Act
    await communicator.send_json_to(
        {
            "combat_calculations": [
                {
                    "name": "Test Calculation",
                    "land_battle": True,
                    "regular_legions": 5,
                }
            ]
        }
    )

    # Assert
    await communicator.disconnect()
    calc_count = await database_sync_to_async(
        CombatCalculation.objects.filter(game=game).count
    )()
    assert calc_count == 0
