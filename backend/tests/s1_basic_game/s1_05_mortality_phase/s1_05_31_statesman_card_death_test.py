import pytest
from rorapp.helpers.kill_senator import kill_senator
from rorapp.models import Faction, Game, Senator


@pytest.mark.django_db
def test_family_statesman_death_restores_family_senator(basic_game: Game):
    # Arrange
    game = basic_game
    senator = Senator.objects.get(game=game, family_name="Cornelius")
    senator.code = "1a"
    senator.statesman_name = "P. Cornelius Scipio Africanus"
    senator.military = 5
    senator.oratory = 5
    senator.generation = 2
    senator.save()

    # Act
    kill_senator(game.id, senator.id)

    # Assert
    senator.refresh_from_db()
    assert senator.alive is True
    assert senator.code == "1"
    assert senator.statesman_name is None
    assert senator.family_name == "Cornelius"
    assert senator.military == 4
    assert senator.generation == 3


@pytest.mark.django_db
def test_family_statesman_faction_leader_death_restores_and_retains_faction_leader(basic_game: Game):
    # Arrange
    game = basic_game
    senator = Senator.objects.get(game=game, family_name="Cornelius")
    senator.code = "1a"
    senator.statesman_name = "P. Cornelius Scipio Africanus"
    senator.add_title(Senator.Title.FACTION_LEADER)
    senator.save()

    # Act
    kill_senator(game.id, senator.id)

    # Assert
    senator.refresh_from_db()
    assert senator.alive is True
    assert senator.statesman_name is None
    assert senator.has_title(Senator.Title.FACTION_LEADER)


@pytest.mark.django_db
def test_independent_statesman_death_kills_senator(basic_game: Game):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    statesman = Senator.objects.create(
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
    kill_senator(game.id, statesman.id)

    # Assert
    statesman.refresh_from_db()
    assert statesman.alive is False
    assert statesman.faction is None


@pytest.mark.django_db
def test_independent_statesman_faction_leader_death_leaves_no_faction_leader(basic_game: Game):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    statesman = Senator.objects.create(
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
    statesman.add_title(Senator.Title.FACTION_LEADER)
    statesman.save()

    # Act
    kill_senator(game.id, statesman.id)

    # Assert
    statesman.refresh_from_db()
    assert statesman.alive is False
    assert statesman.faction is None
    remaining = Senator.objects.filter(game=game, faction=faction)
    assert not any(s.has_title(Senator.Title.FACTION_LEADER) for s in remaining)
