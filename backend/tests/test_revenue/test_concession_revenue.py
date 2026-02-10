import pytest
from rorapp.classes.concession import Concession
from rorapp.models import Game, Senator
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_senator_with_multiple_concessions_earns_cumulative_revenue(basic_game: Game):

    # Arrange
    game = basic_game
    game.phase = Game.Phase.REVENUE
    game.sub_phase = Game.SubPhase.START
    game.state_treasury = 200
    game.save()

    senator = Senator.objects.get(game=game, name="Cornelius")
    senator.add_concession(Concession.MINING)
    senator.add_concession(Concession.LATIUM_TAX_FARMER)
    senator.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    senator.refresh_from_db()
    # 1T base + 3T Mining + 2T Latium Tax Farmer = 6T
    assert senator.talents == 6
    expected_message = "Senators in Faction 1 earned 9T of revenue."
    assert game.logs.filter(text=expected_message).count() == 1
