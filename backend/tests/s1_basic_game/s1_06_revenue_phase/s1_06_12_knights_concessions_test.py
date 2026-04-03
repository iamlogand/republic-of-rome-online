import pytest
from rorapp.classes.concession import Concession
from rorapp.models import Game, Senator
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_senator_earns_cumulative_concession_revenue(revenue_game: Game):
    # Arrange
    game = revenue_game
    senator = Senator.objects.get(game=game, family_name="Cornelius")
    senator.add_concession(Concession.MINING)
    senator.add_concession(Concession.LATIUM_TAX_FARMER)
    senator.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    senator.refresh_from_db()
    assert senator.talents == 6


@pytest.mark.django_db
def test_concession_reveals_corrupt_bar_on_revenue(revenue_game: Game):
    # Arrange
    game = revenue_game
    senator = Senator.objects.get(game=game, family_name="Cornelius")
    senator.add_concession(Concession.MINING)
    senator.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    senator.refresh_from_db()
    assert senator.has_corrupt_concession(Concession.MINING)


@pytest.mark.django_db
def test_armaments_does_not_earn_during_revenue(revenue_game: Game):
    # Arrange
    game = revenue_game
    senator = Senator.objects.get(game=game, family_name="Cornelius")
    senator.add_concession(Concession.ARMAMENTS)
    senator.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    senator.refresh_from_db()
    assert not senator.has_corrupt_concession(Concession.ARMAMENTS)
