import pytest
from rorapp.actions.profiteer_from_famine import ProfiteerFromFamineAction
from rorapp.classes.concession import Concession
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import AvailableAction, Game, Senator


def _collect_revenue(game: Game, droughts: int, popularity: int = 0) -> Senator:
    for _ in range(droughts):
        game.add_effect(GameEffect.DROUGHT)
    game.save()
    senator = Senator.objects.get(game=game, family_name="Cornelius")
    senator.add_concession(Concession.SICILIAN_GRAIN)
    senator.popularity = popularity
    senator.save()
    execute_effects_and_manage_actions(game.id)
    senator.refresh_from_db()
    return senator


def _profiteer(senator: Senator, resolver: FakeRandomResolver) -> bool:
    assert senator.faction_id is not None
    return (
        ProfiteerFromFamineAction()
        .execute(
            senator.game_id,
            senator.faction_id,
            {"Concession": Concession.SICILIAN_GRAIN.value},
            resolver,
        )
        .success
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "droughts, talents, popularity",
    [
        (1, 9, -2),
        (2, 13, -3),
    ],
)
def test_famine_profiteering_multiplies_grain_income_and_costs_popularity(
    revenue_game: Game,
    resolver: FakeRandomResolver,
    droughts: int,
    talents: int,
    popularity: int,
):
    # Arrange
    senator = _collect_revenue(revenue_game, droughts)

    # Act
    success = _profiteer(senator, resolver)

    # Assert
    assert success
    senator.refresh_from_db()
    assert senator.talents == talents
    assert senator.popularity == popularity


@pytest.mark.django_db
def test_famine_profiteering_allowed_at_minus_9_popularity(
    revenue_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    senator = _collect_revenue(revenue_game, 1, popularity=-9)

    # Act
    success = _profiteer(senator, resolver)

    # Assert
    assert success
    senator.refresh_from_db()
    assert senator.talents == 9
    assert senator.popularity == -9


@pytest.mark.django_db
def test_famine_profiteering_only_once_per_concession(
    revenue_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    senator = _collect_revenue(revenue_game, 1)
    _profiteer(senator, resolver)

    # Act
    success = _profiteer(senator, resolver)

    # Assert
    assert not success


@pytest.mark.django_db
@pytest.mark.parametrize("droughts, offered", [(0, False), (1, True)])
def test_famine_profiteering_offered_only_during_famine(
    revenue_game: Game, droughts: int, offered: bool
):
    # Act
    _collect_revenue(revenue_game, droughts)

    # Assert
    assert (
        AvailableAction.objects.filter(
            game=revenue_game, base_name=ProfiteerFromFamineAction.NAME
        ).exists()
        == offered
    )
