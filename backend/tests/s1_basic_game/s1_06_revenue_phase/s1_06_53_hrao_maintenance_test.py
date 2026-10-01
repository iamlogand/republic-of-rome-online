import pytest
from rorapp.actions.maintain_released_forces import MaintainReleasedForcesAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Faction, Fleet, Game, Legion, Log, Senator


def _setup_released_forces_maintenance(
    game: Game, legion_numbers: list, state_treasury: int = 100
) -> tuple:
    """Set game to RELEASED_FORCES_MAINTENANCE with released legions in the reserve.

    No AWAITING_DECISION is set — this is the state before the effect fires.
    """
    hrao_senator = Senator.objects.filter(game=game, alive=True).first()
    assert hrao_senator is not None
    hrao_senator.add_title(Senator.Title.HRAO)
    hrao_senator.save()

    legions = []
    for number in legion_numbers:
        legion = Legion.objects.create(game=game, number=number, released_by_rebel=True)
        legions.append(legion)

    game.phase = Game.Phase.REVENUE
    game.sub_phase = Game.SubPhase.RELEASED_FORCES_MAINTENANCE
    game.state_treasury = state_treasury
    game.save()

    return hrao_senator, legions


def _setup_awaiting_decision(
    game: Game, legion_numbers: list, state_treasury: int = 100
) -> tuple:
    """Set game to RELEASED_FORCES_MAINTENANCE with HRAO already awaiting decision.

    This is the state after the effect fires, ready for the HRAO action.
    """
    hrao_senator, legions = _setup_released_forces_maintenance(
        game, legion_numbers, state_treasury
    )
    hrao_faction = hrao_senator.faction
    assert hrao_faction is not None
    hrao_faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
    hrao_faction.save()
    return hrao_senator, hrao_faction, legions


# --- Effect tests ---


@pytest.mark.django_db
def test_all_forces_eliminated_when_state_cannot_afford_any(revenue_game: Game):
    # Arrange
    _, legions = _setup_released_forces_maintenance(revenue_game, [1, 2, 3], state_treasury=0)
    legion_ids = [l.id for l in legions]

    # Act
    execute_effects_and_manage_actions(revenue_game.id)

    # Assert — all released legions deleted, game advances to redistribution
    assert not Legion.objects.filter(id__in=legion_ids).exists()
    revenue_game.refresh_from_db()
    assert revenue_game.sub_phase == Game.SubPhase.REDISTRIBUTION


@pytest.mark.django_db
def test_auto_elimination_logged_when_state_cannot_afford(revenue_game: Game):
    # Arrange
    _setup_released_forces_maintenance(revenue_game, [1, 2], state_treasury=0)

    # Act
    execute_effects_and_manage_actions(revenue_game.id)

    # Assert
    assert Log.objects.filter(
        game=revenue_game,
        text__contains="were eliminated as the State could not afford their maintenance",
    ).exists()


@pytest.mark.django_db
def test_hrao_faction_awaiting_decision_when_state_can_afford(revenue_game: Game):
    # Arrange
    hrao_senator, _ = _setup_released_forces_maintenance(revenue_game, [1, 2], state_treasury=100)
    hrao_faction = hrao_senator.faction

    # Act
    execute_effects_and_manage_actions(revenue_game.id)

    # Assert — effect sets AWAITING_DECISION and stops
    hrao_faction.refresh_from_db()
    assert hrao_faction.has_status_item(FactionStatusItem.AWAITING_DECISION)
    revenue_game.refresh_from_db()
    assert revenue_game.sub_phase == Game.SubPhase.RELEASED_FORCES_MAINTENANCE


# --- Action tests ---


@pytest.mark.django_db
def test_hrao_maintains_all_released_legions(revenue_game: Game):
    # Arrange
    _, hrao_faction, legions = _setup_awaiting_decision(revenue_game, [1, 2], state_treasury=100)
    legion_ids = [l.id for l in legions]

    # Act
    MaintainReleasedForcesAction().execute(
        revenue_game.id, hrao_faction.id, {"Legions": legion_ids, "Fleets": []}, FakeRandomResolver()
    )

    # Assert — 2 legions × 2T = 4T charged; both legions still exist
    revenue_game.refresh_from_db()
    assert revenue_game.state_treasury == 96
    assert Legion.objects.filter(id__in=legion_ids).count() == 2


@pytest.mark.django_db
def test_hrao_eliminates_all_released_legions(revenue_game: Game):
    # Arrange
    _, hrao_faction, legions = _setup_awaiting_decision(revenue_game, [1, 2], state_treasury=100)
    legion_ids = [l.id for l in legions]

    # Act
    MaintainReleasedForcesAction().execute(
        revenue_game.id, hrao_faction.id, {"Legions": [], "Fleets": []}, FakeRandomResolver()
    )

    # Assert — no cost charged; both legions deleted
    revenue_game.refresh_from_db()
    assert revenue_game.state_treasury == 100
    assert not Legion.objects.filter(id__in=legion_ids).exists()


@pytest.mark.django_db
def test_hrao_maintains_some_and_eliminates_others(revenue_game: Game):
    # Arrange
    _, hrao_faction, legions = _setup_awaiting_decision(revenue_game, [1, 2, 3], state_treasury=100)
    keep_id = legions[0].id
    drop_ids = [l.id for l in legions[1:]]

    # Act
    MaintainReleasedForcesAction().execute(
        revenue_game.id, hrao_faction.id, {"Legions": [keep_id], "Fleets": []}, FakeRandomResolver()
    )

    # Assert — 1 legion kept, 2 deleted; 2T charged
    revenue_game.refresh_from_db()
    assert revenue_game.state_treasury == 98
    assert Legion.objects.filter(id=keep_id).exists()
    assert not Legion.objects.filter(id__in=drop_ids).exists()


@pytest.mark.django_db
def test_game_progresses_to_redistribution_after_hrao_decision(revenue_game: Game):
    # Arrange
    _, hrao_faction, legions = _setup_awaiting_decision(revenue_game, [1])

    # Act
    MaintainReleasedForcesAction().execute(
        revenue_game.id, hrao_faction.id, {"Legions": [], "Fleets": []}, FakeRandomResolver()
    )

    # Assert
    revenue_game.refresh_from_db()
    assert revenue_game.sub_phase == Game.SubPhase.REDISTRIBUTION


@pytest.mark.django_db
def test_hrao_awaiting_decision_cleared_after_action(revenue_game: Game):
    # Arrange
    _, hrao_faction, legions = _setup_awaiting_decision(revenue_game, [1])

    # Act
    MaintainReleasedForcesAction().execute(
        revenue_game.id, hrao_faction.id, {"Legions": [], "Fleets": []}, FakeRandomResolver()
    )

    # Assert
    hrao_faction.refresh_from_db()
    assert not hrao_faction.has_status_item(FactionStatusItem.AWAITING_DECISION)


@pytest.mark.django_db
def test_released_flag_cleared_after_hrao_decision(revenue_game: Game):
    # Arrange
    _, hrao_faction, legions = _setup_awaiting_decision(revenue_game, [1, 2])

    # Act
    MaintainReleasedForcesAction().execute(
        revenue_game.id, hrao_faction.id, {"Legions": [l.id for l in legions], "Fleets": []}, FakeRandomResolver()
    )

    # Assert — maintained legions have their flag cleared
    assert not Legion.objects.filter(game=revenue_game, released_by_rebel=True).exists()


@pytest.mark.django_db
def test_cannot_maintain_more_than_state_can_afford(revenue_game: Game):
    # Arrange — state treasury can only afford 1 legion (2T), but HRAO tries to pick 2
    _, hrao_faction, legions = _setup_awaiting_decision(revenue_game, [1, 2], state_treasury=2)
    legion_ids = [l.id for l in legions]

    # Act
    result = MaintainReleasedForcesAction().execute(
        revenue_game.id, hrao_faction.id, {"Legions": legion_ids, "Fleets": []}, FakeRandomResolver()
    )

    # Assert
    assert not result.success


@pytest.mark.django_db
def test_maintained_forces_log_created(revenue_game: Game):
    # Arrange
    _, hrao_faction, legions = _setup_awaiting_decision(revenue_game, [1])
    legion_ids = [l.id for l in legions]

    # Act
    MaintainReleasedForcesAction().execute(
        revenue_game.id, hrao_faction.id, {"Legions": legion_ids, "Fleets": []}, FakeRandomResolver()
    )

    # Assert
    assert Log.objects.filter(
        game=revenue_game, text__contains="The State paid 2T to maintain"
    ).exists()


@pytest.mark.django_db
def test_eliminated_forces_log_created(revenue_game: Game):
    # Arrange
    _, hrao_faction, legions = _setup_awaiting_decision(revenue_game, [1, 2])

    # Act
    MaintainReleasedForcesAction().execute(
        revenue_game.id, hrao_faction.id, {"Legions": [], "Fleets": []}, FakeRandomResolver()
    )

    # Assert
    assert Log.objects.filter(
        game=revenue_game, text__contains="were eliminated"
    ).exists()
