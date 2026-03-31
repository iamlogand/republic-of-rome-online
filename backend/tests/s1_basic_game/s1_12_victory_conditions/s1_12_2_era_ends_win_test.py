import pytest
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Faction, Game, Log, Senator


def _setup_era_ends_resolution(game: Game) -> None:
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.ERA_ENDS
    game.era_ends = True
    game.save()


@pytest.mark.django_db
def test_era_ends_sets_finished_on(basic_game: Game):
    # Arrange
    _setup_era_ends_resolution(basic_game)

    # Act
    execute_effects_and_manage_actions(basic_game.id)

    # Assert
    basic_game.refresh_from_db()
    assert basic_game.finished_on is not None


@pytest.mark.django_db
def test_era_ends_faction_with_most_influence_wins(basic_game: Game):
    # Arrange
    faction1: Faction = basic_game.factions.get(position=1)
    faction2: Faction = basic_game.factions.get(position=2)
    Senator.objects.filter(game=basic_game, faction=faction1).update(influence=10)
    Senator.objects.filter(game=basic_game, faction=faction2).update(influence=1)
    _setup_era_ends_resolution(basic_game)

    # Act
    execute_effects_and_manage_actions(basic_game.id)

    # Assert
    logs = Log.objects.filter(game=basic_game)
    assert any(faction1.display_name in log.text for log in logs)


@pytest.mark.django_db
def test_era_ends_tie_broken_by_individual_senator_influence(basic_game: Game):
    # Arrange
    faction1: Faction = basic_game.factions.get(position=1)
    faction2: Faction = basic_game.factions.get(position=2)
    Senator.objects.filter(game=basic_game, faction=faction1).update(influence=5)
    Senator.objects.filter(game=basic_game, faction=faction2).update(influence=5)
    senator = Senator.objects.filter(game=basic_game, faction=faction1).first()
    assert senator is not None
    senator.delete()
    Senator.objects.create(
        game=basic_game,
        faction=faction1,
        family_name="Tiebreaker",
        code="99",
        military=1,
        oratory=1,
        loyalty=1,
        influence=20,
    )
    _setup_era_ends_resolution(basic_game)

    # Act
    execute_effects_and_manage_actions(basic_game.id)

    # Assert
    logs = Log.objects.filter(game=basic_game)
    assert any(faction1.display_name in log.text for log in logs)


@pytest.mark.django_db
def test_era_ends_tie_broken_by_votes(basic_game: Game):
    # Arrange
    faction1: Faction = basic_game.factions.get(position=1)
    faction2: Faction = basic_game.factions.get(position=2)
    Senator.objects.filter(game=basic_game, faction=faction1).update(influence=5)
    Senator.objects.filter(game=basic_game, faction=faction2).update(influence=5)
    Senator.objects.filter(game=basic_game, faction=faction1).update(knights=3)
    Senator.objects.filter(game=basic_game, faction=faction2).update(knights=0)
    _setup_era_ends_resolution(basic_game)

    # Act
    execute_effects_and_manage_actions(basic_game.id)

    # Assert
    logs = Log.objects.filter(game=basic_game)
    assert any(faction1.display_name in log.text for log in logs)



@pytest.mark.django_db
def test_era_ends_win_triggered_after_putting_rome_in_order(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.PUTTING_ROME_IN_ORDER
    game.era_ends = True
    game.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.finished_on is not None
