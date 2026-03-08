import pytest
from rorapp.models import Game
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_state_earns_base_revenue(revenue_game: Game):
    # Act
    execute_effects_and_manage_actions(revenue_game.id)

    # Assert
    revenue_game.refresh_from_db()
    assert revenue_game.state_treasury == 300
