import json
import os
import pytest
from django.conf import settings
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rorapp.models import Faction, Game, Senator


@pytest.mark.django_db
def test_initial_rome_consul_gains_influence():

    # Arrange
    host = User.objects.create_user(username="host", password="password")
    game = Game.objects.create(name="Test Game", host=host)

    for i in range(1, 4):
        player = User.objects.create_user(username=f"player{i}", password="password")
        Faction.objects.create(game=game, player=player, position=i)

    client = APIClient()
    client.force_authenticate(user=host)

    # Act
    response = client.post(f"/api/games/{game.id}/start-game/")

    # Assert
    assert response.status_code == 200
    rome_consul = Senator.objects.get(
        game=game, titles__contains=Senator.Title.ROME_CONSUL.value
    )

    senator_json_path = os.path.join(
        settings.BASE_DIR, "rorapp", "data", "senator.json"
    )
    with open(senator_json_path, "r") as file:
        senators_dict = json.load(file)

    initial_influence = senators_dict[rome_consul.name]["influence"]
    assert rome_consul.influence == initial_influence + 5
