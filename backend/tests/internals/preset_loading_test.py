import pytest
from django.contrib.auth.models import User
from rorapp.helpers.preset_loader import list_presets, load_preset, resolve_preset
from rorapp.models import Faction, Game


@pytest.mark.django_db
@pytest.mark.parametrize("name", [p["name"] for p in list_presets()])
def test_preset_loads_into_a_playable_game(name: str):
    # Arrange
    host = User.objects.create_user(username=f"host_{name}", password="password")
    game = Game.objects.create(name=f"Game {name}", host=host)
    for position in range(1, 4):
        player = User.objects.create_user(
            username=f"player{position}_{name}", password="password"
        )
        Faction.objects.create(game=game, player=player, position=position)

    # Act
    load_preset(game, resolve_preset(name))

    # Assert
    game.refresh_from_db()
    assert game.started_on is not None
    assert game.finished_on is None
    assert game.actions.exists()
