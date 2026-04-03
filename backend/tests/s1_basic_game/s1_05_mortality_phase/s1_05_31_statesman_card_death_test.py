import pytest
from rorapp.helpers.kill_senator import kill_senator
from rorapp.models import Faction, Game, Senator


@pytest.mark.django_db
def test_family_statesman_death_reverts_family_senator(basic_game: Game):
    # Arrange
    game = basic_game
    senator = Senator.objects.get(game=game, family_name="Cornelius")
    senator.code = "1a"
    senator.statesman_name = "P. Cornelius Scipio Africanus"
    senator.military = 5
    senator.generation = 2
    senator.save()

    # Act
    kill_senator(senator)

    # Assert
    senator.refresh_from_db()
    assert senator.alive is False
    assert senator.code == "1"
    assert senator.statesman_name is None
    assert senator.family_name == "Cornelius"
    assert senator.military != 5
    assert senator.generation == 2


@pytest.mark.django_db
def test_family_statesman_faction_leader_death_retains_family_senator_in_faction(basic_game: Game):
    # Arrange
    game = basic_game
    senator = Senator.objects.get(game=game, family_name="Cornelius")
    senator.code = "1a"
    senator.statesman_name = "P. Cornelius Scipio Africanus"
    senator.military = 5
    senator.oratory = 5
    senator.generation = 2
    senator.add_title(Senator.Title.FACTION_LEADER)
    senator.save()

    # Act
    kill_senator(senator)

    # Assert
    senator.refresh_from_db()
    assert senator.alive is True
    assert senator.code == "1"
    assert senator.statesman_name is None
    assert senator.generation == 3
    assert senator.has_title(Senator.Title.FACTION_LEADER)


@pytest.mark.django_db
def test_independent_statesman_death_removes_senator(basic_game: Game):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    senator = Senator.objects.create(
        game=game,
        faction=faction,
        family_name="Flamininus",
        family=False,
        code="18a",
        statesman_name="T. Quinctius Flamininus",
        military=5,
        oratory=4,
        loyalty=7,
        influence=4,
    )

    # Act
    kill_senator(senator)

    # Assert
    assert game.senators.filter(family_name="Flaminius").count() == 0


@pytest.mark.django_db
def test_independent_statesman_faction_leader_death_removes_senator(basic_game: Game):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    senator = Senator.objects.create(
        game=game,
        faction=faction,
        family_name="Flamininus",
        family=False,
        code="18a",
        statesman_name="T. Quinctius Flamininus",
        military=5,
        oratory=4,
        loyalty=7,
        influence=4,
    )
    senator.add_title(Senator.Title.FACTION_LEADER)
    senator.save()

    # Act
    kill_senator(senator)

    # Assert
    assert game.senators.filter(family_name="Flaminius").count() == 0
