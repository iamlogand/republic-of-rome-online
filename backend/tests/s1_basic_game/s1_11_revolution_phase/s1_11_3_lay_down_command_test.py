import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Campaign, Game, Legion, Log, Senator


@pytest.mark.django_db
def test_land_victor_returns_to_rome(
    land_victor: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    game = land_victor.game
    commander = land_victor.commander
    assert commander is not None

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    commander.refresh_from_db()
    assert commander.location == "Rome"


@pytest.mark.django_db
def test_land_victor_campaign_is_deleted(
    land_victor: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    game = land_victor.game

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert not Campaign.objects.filter(game=game).exists()


@pytest.mark.django_db
def test_land_victor_legions_return_to_the_reserve(
    land_victor: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    game = land_victor.game

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Legion.objects.filter(game=game, campaign__isnull=False).count() == 0
    assert Legion.objects.filter(game=game).count() == 5


@pytest.mark.django_db
def test_land_victor_loses_the_proconsul_title(
    land_victor: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    game = land_victor.game
    commander = land_victor.commander
    assert commander is not None
    commander.add_title(Senator.Title.PROCONSUL)
    commander.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    commander.refresh_from_db()
    assert not commander.has_title(Senator.Title.PROCONSUL)


@pytest.mark.django_db
def test_master_of_horse_returns_to_rome(
    land_victor: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    game = land_victor.game
    master_of_horse = Senator.objects.get(game=game, family_name="Fabius")
    master_of_horse.add_title(Senator.Title.MASTER_OF_HORSE)
    master_of_horse.location = "Cisalpine Gaul"
    master_of_horse.save()
    land_victor.master_of_horse = master_of_horse
    land_victor.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    master_of_horse.refresh_from_db()
    assert master_of_horse.location == "Rome"


@pytest.mark.django_db
def test_laying_down_command_is_logged(
    land_victor: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    game = land_victor.game

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Log.objects.filter(
        game=game,
        text="Cornelius laid down command and returned to Rome. "
        "5 legions (I–V) returned to the reserve forces.",
    ).exists()


@pytest.mark.django_db
def test_revolution_ends_after_the_declaration(
    land_victor: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    game = land_victor.game

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.phase != Game.Phase.REVOLUTION
    assert game.turn == 2


@pytest.mark.django_db
def test_revolution_ends_when_there_is_no_land_victor(
    revolution_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = revolution_game
    game.sub_phase = Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
    game.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.phase != Game.Phase.REVOLUTION
    assert game.turn == 2
