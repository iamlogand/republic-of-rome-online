import pytest
from django.db import IntegrityError

from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.game_state.get_game_state import get_public_game_state
from rorapp.helpers.provinces import province_static_fields
from rorapp.models import Game, Province
from rorapp.serializers import ProvinceSerializer


@pytest.mark.django_db
def test_public_game_state_includes_empty_provinces_list(basic_game: Game):
    # Act
    public_game_state, _ = get_public_game_state(basic_game.id)

    # Assert
    assert "provinces" in public_game_state
    assert public_game_state["provinces"] == []


@pytest.mark.django_db
def test_public_game_state_serializes_provinces(basic_game: Game):
    # Arrange
    province = Province.objects.create(
        game=basic_game,
        name="Macedonia",
        developed=True,
        **province_static_fields("Macedonia"),
    )

    # Act
    public_game_state, _ = get_public_game_state(basic_game.id)

    # Assert
    assert public_game_state["provinces"] == [ProvinceSerializer(province).data]
    serialized = public_game_state["provinces"][0]
    assert serialized["frontier"] is True
    assert serialized["in_forum"] is True


@pytest.mark.django_db
def test_game_state_snapshot_get_province(basic_game: Game):
    # Arrange
    province = Province.objects.create(
        game=basic_game, name="Asia", developed=True
    )

    # Act
    snapshot = GameStateSnapshot(basic_game.id)

    # Assert
    assert snapshot.get_province(province.id) == province
    assert snapshot.get_province(province.id + 9999) is None


@pytest.mark.django_db
def test_province_name_is_unique_per_game(basic_game: Game):
    # Arrange
    Province.objects.create(game=basic_game, name="Sicilia", developed=False)

    # Act
    # Assert
    with pytest.raises(IntegrityError):
        Province.objects.create(game=basic_game, name="Sicilia", developed=True)