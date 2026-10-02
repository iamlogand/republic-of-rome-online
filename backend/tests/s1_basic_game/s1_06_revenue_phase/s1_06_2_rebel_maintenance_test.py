import pytest
from rorapp.actions.release_rebel_legions import ReleaseRebelLegionsAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Campaign, Game, Legion, Log, Senator, War


def _setup_rebel(game: Game, legion_numbers: list) -> tuple:
    senator = Senator.objects.filter(game=game, alive=True).first()
    assert senator is not None
    senator.rebel = True
    senator.save()

    revolt = War.objects.create(
        game=game,
        name="Revolt",
        index=0,
        land_strength=10,
        fleet_support=0,
        naval_strength=0,
        spoils=0,
        location="Italia",
        status=War.Status.ACTIVE,
        primary_rebel=senator,
    )

    campaign = Campaign.objects.create(game=game, war=revolt, commander=senator)

    for number in legion_numbers:
        Legion.objects.create(game=game, number=number, campaign=campaign)

    # Assign HRAO to a non-rebel senator for tests that proceed to the release action
    hrao_candidate = Senator.objects.filter(game=game, alive=True).exclude(id=senator.id).first()
    if hrao_candidate:
        hrao_candidate.add_title(Senator.Title.HRAO)
        hrao_candidate.save()

    return senator, campaign, revolt


def _execute_rebel_release(game: Game, senator: Senator, legion_ids: list) -> None:
    """Drive the rebel release action after execute_effects_and_manage_actions has
    left the game at REBEL_FORCES_RELEASE with AWAITING_DECISION on the rebel faction."""
    faction = senator.faction
    assert faction is not None
    ReleaseRebelLegionsAction().execute(
        game.id, faction.id, {"Legions": legion_ids}, FakeRandomResolver()
    )


@pytest.mark.django_db
def test_rebel_senator_earns_no_personal_revenue(revenue_game: Game):
    # Arrange
    senator, _, _ = _setup_rebel(revenue_game, [1, 2, 3])
    initial_talents = senator.talents

    # Act
    execute_effects_and_manage_actions(revenue_game.id)

    # Assert
    senator.refresh_from_db()
    assert senator.talents == initial_talents


@pytest.mark.django_db
def test_rebel_legions_not_charged_to_state(revenue_game: Game):
    # Arrange
    _setup_rebel(revenue_game, [1, 2, 3, 4, 5])

    # Act
    execute_effects_and_manage_actions(revenue_game.id)

    # Assert
    revenue_game.refresh_from_db()
    assert revenue_game.state_treasury == 280


@pytest.mark.django_db
def test_rebel_maintenance_deducted_from_personal_treasury(revenue_game: Game):
    # Arrange
    senator, _, _ = _setup_rebel(revenue_game, [1, 2, 3])
    senator.talents = 20
    senator.save()

    # Act
    execute_effects_and_manage_actions(revenue_game.id)

    # Assert
    senator.refresh_from_db()
    assert senator.talents == 14


@pytest.mark.django_db
def test_rebel_maintenance_deducted_from_faction_treasury_when_personal_empty(
    revenue_game: Game,
):
    # Arrange
    senator, _, _ = _setup_rebel(revenue_game, [1, 2, 3])
    senator.talents = 2
    senator.save()
    faction = senator.faction
    faction.treasury = 20
    faction.save()

    # Act
    execute_effects_and_manage_actions(revenue_game.id)

    # Assert
    senator.refresh_from_db()
    faction.refresh_from_db()
    assert senator.talents == 0
    assert faction.treasury == 16


@pytest.mark.django_db
def test_veteran_legions_with_rebel_allegiance_are_free(revenue_game: Game):
    # Arrange
    senator, campaign, _ = _setup_rebel(revenue_game, [1, 2])
    senator.talents = 0
    senator.save()
    # Make both legions veteran with rebel allegiance — no maintenance required
    for legion in Legion.objects.filter(campaign=campaign):
        legion.veteran = True
        legion.allegiance = senator
        legion.save()

    # Act
    execute_effects_and_manage_actions(revenue_game.id)

    # Assert
    senator.refresh_from_db()
    assert senator.talents == 0
    assert Legion.objects.filter(campaign=campaign).count() == 2


@pytest.mark.django_db
def test_rebel_awaiting_decision_when_cannot_afford(revenue_game: Game):
    # Arrange
    senator, _, _ = _setup_rebel(revenue_game, [1, 2, 3])
    senator.talents = 2  # can only afford 1 legion
    senator.save()
    faction = senator.faction
    faction.treasury = 0
    faction.save()

    # Act
    execute_effects_and_manage_actions(revenue_game.id)

    # Assert
    faction.refresh_from_db()
    assert faction.has_status_item(FactionStatusItem.AWAITING_DECISION)
    revenue_game.refresh_from_db()
    assert revenue_game.sub_phase == Game.SubPhase.REBEL_FORCES_RELEASE
    assert revenue_game.rebel_units_to_release == 2


@pytest.mark.django_db
def test_rebel_releases_legions_it_cannot_afford(revenue_game: Game):
    # Arrange
    senator, campaign, _ = _setup_rebel(revenue_game, [1, 2, 3])
    senator.talents = 2  # can only afford 1 legion
    senator.save()
    faction = senator.faction
    faction.treasury = 0
    faction.save()
    execute_effects_and_manage_actions(revenue_game.id)
    keep_id = Legion.objects.get(game=revenue_game, number=1).id
    release_ids = [
        Legion.objects.get(game=revenue_game, number=2).id,
        Legion.objects.get(game=revenue_game, number=3).id,
    ]

    # Act
    _execute_rebel_release(revenue_game, senator, release_ids)

    # Assert
    assert Legion.objects.get(id=keep_id).campaign == campaign
    assert Legion.objects.filter(id__in=release_ids, campaign__isnull=True).count() == 2


@pytest.mark.django_db
def test_released_legions_logged(revenue_game: Game):
    # Arrange
    senator, campaign, _ = _setup_rebel(revenue_game, [1, 2])
    senator.talents = 2  # can only afford 1 of 2 legions
    senator.save()
    faction = senator.faction
    faction.treasury = 0
    faction.save()
    execute_effects_and_manage_actions(revenue_game.id)
    release_id = Legion.objects.get(game=revenue_game, number=2).id

    # Act
    _execute_rebel_release(revenue_game, senator, [release_id])

    # Assert
    assert Log.objects.filter(
        game=revenue_game,
        text__contains="returned to the reserve forces",
    ).exists()


@pytest.mark.django_db
def test_rebel_maintenance_logged_when_paid(revenue_game: Game):
    # Arrange
    senator, _, _ = _setup_rebel(revenue_game, [1])
    senator.talents = 10
    senator.save()

    # Act
    execute_effects_and_manage_actions(revenue_game.id)

    # Assert
    assert Log.objects.filter(
        game=revenue_game,
        text__contains="The rebels spent 2T maintaining 1 legion.",
    ).exists()


@pytest.mark.django_db
def test_partial_payment_logged(revenue_game: Game):
    # Arrange
    senator, _, _ = _setup_rebel(revenue_game, [1, 2])
    senator.talents = 2  # can only afford 1 of 2 legions
    senator.save()
    faction = senator.faction
    faction.treasury = 0
    faction.save()

    # Act
    execute_effects_and_manage_actions(revenue_game.id)

    # Assert
    assert Log.objects.filter(
        game=revenue_game,
        text__contains="but couldn't afford to maintain the rest",
    ).exists()


@pytest.mark.django_db
def test_secondary_rebel_charged_when_primary_runs_dry(revenue_game: Game):
    # Arrange
    senator, _, _ = _setup_rebel(revenue_game, [1, 2, 3])
    senator.talents = 0
    senator.save()
    faction = senator.faction
    faction.treasury = 0
    faction.save()
    secondary = Senator.objects.filter(game=revenue_game, alive=True, rebel=False).first()
    assert secondary is not None
    secondary.rebel = True
    secondary.talents = 10
    secondary.save()

    # Act
    execute_effects_and_manage_actions(revenue_game.id)

    # Assert
    secondary.refresh_from_db()
    assert secondary.talents == 4
