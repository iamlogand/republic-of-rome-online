import pytest
from rorapp.actions.disband_released_legions import DisbandReleasedLegionsAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Game, Legion, Senator


def _setup_released_legions_disbanding(
    game: Game, legion_numbers: list, state_treasury: int = 100
) -> tuple:
    """Set game to RELEASED_LEGIONS_DISBANDMENT with released legions in the reserve."""
    hrao_senator = Senator.objects.filter(game=game, alive=True).first()
    assert hrao_senator is not None
    hrao_senator.add_title(Senator.Title.HRAO)
    hrao_senator.save()

    legions = []
    for number in legion_numbers:
        legion = Legion.objects.create(game=game, number=number, released_by_rebel=True)
        legions.append(legion)

    game.phase = Game.Phase.REVENUE
    game.sub_phase = Game.SubPhase.RELEASED_LEGIONS_DISBANDMENT
    game.state_treasury = state_treasury
    game.save()

    return hrao_senator, legions


def _setup_awaiting_decision(
    game: Game, legion_numbers: list, state_treasury: int = 100
) -> tuple:
    """Set game to RELEASED_LEGIONS_DISBANDMENT with HRAO already awaiting decision.

    This is the state after the effect fires, ready for the HRAO action.
    """
    hrao_senator, legions = _setup_released_legions_disbanding(
        game, legion_numbers, state_treasury
    )
    hrao_faction = hrao_senator.faction
    assert hrao_faction is not None
    hrao_faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
    hrao_faction.save()
    return hrao_senator, hrao_faction, legions


@pytest.mark.django_db
def test_hrao_disbands_no_legions_maintains_all(revenue_game: Game):
    # Arrange
    _, hrao_faction, legions = _setup_awaiting_decision(
        revenue_game, [1, 2], state_treasury=100
    )
    legion_ids = [l.id for l in legions]

    # Act
    DisbandReleasedLegionsAction().execute(
        revenue_game.id, hrao_faction.id, {"Legions": []}, FakeRandomResolver()
    )

    # Assert
    revenue_game.refresh_from_db()
    assert revenue_game.state_treasury == 96
    assert Legion.objects.filter(id__in=legion_ids).count() == 2


@pytest.mark.django_db
def test_hrao_disbands_all_legions(revenue_game: Game):
    # Arrange
    _, hrao_faction, legions = _setup_awaiting_decision(
        revenue_game, [1, 2], state_treasury=100
    )
    legion_ids = [l.id for l in legions]

    # Act
    DisbandReleasedLegionsAction().execute(
        revenue_game.id, hrao_faction.id, {"Legions": legion_ids}, FakeRandomResolver()
    )

    # Assert
    revenue_game.refresh_from_db()
    assert revenue_game.state_treasury == 100
    assert not Legion.objects.filter(id__in=legion_ids).exists()


@pytest.mark.django_db
def test_hrao_maintains_some_and_eliminates_others(revenue_game: Game):
    # Arrange
    _, hrao_faction, legions = _setup_awaiting_decision(
        revenue_game, [1, 2, 3], state_treasury=100
    )
    keep_id = legions[0].id
    drop_ids = [l.id for l in legions[1:]]

    # Act
    DisbandReleasedLegionsAction().execute(
        revenue_game.id, hrao_faction.id, {"Legions": drop_ids}, FakeRandomResolver()
    )

    # Assert
    revenue_game.refresh_from_db()
    assert revenue_game.state_treasury == 98
    assert Legion.objects.filter(id=keep_id).exists()
    assert not Legion.objects.filter(id__in=drop_ids).exists()


@pytest.mark.django_db
def test_game_progresses_to_redistribution_after_hrao_decision(revenue_game: Game):
    # Arrange
    _, hrao_faction, legions = _setup_awaiting_decision(revenue_game, [1])
    legion_ids = [l.id for l in legions]

    # Act
    DisbandReleasedLegionsAction().execute(
        revenue_game.id, hrao_faction.id, {"Legions": legion_ids}, FakeRandomResolver()
    )

    # Assert
    revenue_game.refresh_from_db()
    assert revenue_game.sub_phase == Game.SubPhase.REDISTRIBUTION


@pytest.mark.django_db
def test_hrao_awaiting_decision_cleared_after_action(revenue_game: Game):
    # Arrange
    _, hrao_faction, legions = _setup_awaiting_decision(revenue_game, [1])
    legion_ids = [l.id for l in legions]

    # Act
    DisbandReleasedLegionsAction().execute(
        revenue_game.id, hrao_faction.id, {"Legions": legion_ids}, FakeRandomResolver()
    )

    # Assert
    hrao_faction.refresh_from_db()
    assert not hrao_faction.has_status_item(FactionStatusItem.AWAITING_DECISION)


@pytest.mark.django_db
def test_released_flag_cleared_after_hrao_decision(revenue_game: Game):
    # Arrange
    _, hrao_faction, legions = _setup_awaiting_decision(revenue_game, [1, 2])

    # Act
    DisbandReleasedLegionsAction().execute(
        revenue_game.id,
        hrao_faction.id,
        {"Legions": []},
        FakeRandomResolver(),
    )

    # Assert
    assert not Legion.objects.filter(game=revenue_game, released_by_rebel=True).exists()
