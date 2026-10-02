import pytest
from rorapp.actions.release_rebel_legions import ReleaseRebelLegionsAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Campaign, Faction, Game, Legion, Log, Senator, War


def _setup_rebel(game: Game, legion_numbers: list) -> tuple[Senator, Campaign]:
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

    return senator, campaign


def _execute_rebel_release(game: Game, senator: Senator, legion_ids: list) -> None:
    faction = senator.faction
    assert faction is not None
    ReleaseRebelLegionsAction().execute(
        game.id, faction.id, {"Legions": legion_ids}, FakeRandomResolver()
    )


@pytest.mark.django_db
def test_rebel_senator_earns_no_personal_revenue(revenue_game: Game):
    # Arrange
    senator, _ = _setup_rebel(revenue_game, [1, 2, 3])
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
    senator, _ = _setup_rebel(revenue_game, [1, 2, 3])
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
    senator, _ = _setup_rebel(revenue_game, [1, 2, 3])
    senator.talents = 2
    senator.save()
    faction = senator.faction
    assert faction is not None
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
    senator, campaign = _setup_rebel(revenue_game, [1, 2])
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
    senator, _ = _setup_rebel(revenue_game, [1, 2, 3])
    senator.talents = 2  # can only afford 1 legion
    senator.save()
    faction = senator.faction
    assert faction is not None
    faction.treasury = 0
    faction.save()

    # Act
    execute_effects_and_manage_actions(revenue_game.id)

    # Assert
    faction.refresh_from_db()
    assert faction.has_status_item(FactionStatusItem.AWAITING_DECISION)
    revenue_game.refresh_from_db()
    assert revenue_game.sub_phase == Game.SubPhase.REBEL_LEGIONS_RELEASE
    assert revenue_game.rebel_legions_to_release == 2


@pytest.mark.django_db
def test_rebel_releases_legions_it_cannot_afford(revenue_game: Game):
    # Arrange
    senator, campaign = _setup_rebel(revenue_game, [1, 2, 3])
    senator.talents = 2  # can only afford 1 legion
    senator.save()
    faction = senator.faction
    assert faction is not None
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
    senator, _ = _setup_rebel(revenue_game, [1, 2])
    senator.talents = 2  # can only afford 1 of 2 legions
    senator.save()
    faction = senator.faction
    assert faction is not None
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
    senator, _ = _setup_rebel(revenue_game, [1])
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
    senator, _ = _setup_rebel(revenue_game, [1, 2])
    senator.talents = 2  # can only afford 1 of 2 legions
    senator.save()
    faction = senator.faction
    assert faction is not None
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
def test_odd_talent_leftover_stays_with_primary_rebel(revenue_game: Game):
    # Arrange
    senator, _ = _setup_rebel(revenue_game, [1, 2, 3, 4, 5, 6, 7])
    senator.talents = 11
    senator.save()
    faction = senator.faction
    assert faction is not None
    faction.treasury = 0
    faction.save()

    # Act
    execute_effects_and_manage_actions(revenue_game.id)

    # Assert
    senator.refresh_from_db()
    assert senator.talents == 1


@pytest.mark.django_db
def test_odd_talent_leftover_stays_with_secondary_rebel(revenue_game: Game):
    # Arrange
    senator, _ = _setup_rebel(revenue_game, [1, 2, 3, 4, 5, 6, 7])
    senator.talents = 9
    senator.save()
    faction = senator.faction
    assert faction is not None
    faction.treasury = 0
    faction.save()
    secondary = Senator.objects.filter(
        game=revenue_game, alive=True, rebel=False
    ).first()
    assert secondary is not None
    secondary.rebel = True
    secondary.talents = 2
    secondary.save()

    # Act
    execute_effects_and_manage_actions(revenue_game.id)

    # Assert
    secondary.refresh_from_db()
    assert secondary.talents == 1


@pytest.mark.django_db
def test_odd_talent_leftover_stays_with_faction_treasury(revenue_game: Game):
    # Arrange
    senator, _ = _setup_rebel(revenue_game, [1, 2, 3, 4, 5, 6, 7])
    senator.talents = 0
    senator.save()
    faction = senator.faction
    assert faction is not None
    faction.treasury = 11
    faction.save()

    # Act
    execute_effects_and_manage_actions(revenue_game.id)

    # Assert
    faction.refresh_from_db()
    assert faction.treasury == 1


@pytest.mark.django_db
def test_secondary_rebel_charged_when_primary_runs_dry(revenue_game: Game):
    # Arrange
    senator, _ = _setup_rebel(revenue_game, [1, 2, 3])
    senator.talents = 0
    senator.save()
    faction = senator.faction
    assert faction is not None
    faction.treasury = 0
    faction.save()
    secondary = Senator.objects.filter(
        game=revenue_game, alive=True, rebel=False
    ).first()
    assert secondary is not None
    secondary.rebel = True
    secondary.talents = 10
    secondary.save()

    # Act
    execute_effects_and_manage_actions(revenue_game.id)

    # Assert
    secondary.refresh_from_db()
    assert secondary.talents == 4


def _setup_rebel_legions_release(
    game: Game, legion_numbers: list, state_treasury: int = 100
) -> tuple:
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
    legions = [
        Legion.objects.create(game=game, number=n, campaign=campaign)
        for n in legion_numbers
    ]

    hrao_candidate = (
        Senator.objects.filter(game=game, alive=True).exclude(id=senator.id).first()
    )
    if hrao_candidate:
        hrao_candidate.add_title(Senator.Title.HRAO)
        hrao_candidate.save()

    faction = senator.faction
    assert faction is not None
    faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
    faction.save()

    game.phase = Game.Phase.REVENUE
    game.sub_phase = Game.SubPhase.REBEL_LEGIONS_RELEASE
    game.state_treasury = state_treasury
    game.rebel_legions_to_release = len(legions)
    game.save()

    return senator, faction, campaign, legions


@pytest.mark.django_db
def test_rebel_chooses_which_legions_to_release(revenue_game: Game):
    # Arrange
    senator, faction, campaign, legions = _setup_rebel_legions_release(
        revenue_game, [1, 2, 3]
    )
    senator.talents = 0
    senator.save()
    game_rebel_legions_to_release = 2
    revenue_game.rebel_legions_to_release = game_rebel_legions_to_release
    revenue_game.save()
    keep_id = legions[0].id
    release_ids = [l.id for l in legions[1:]]

    # Act
    ReleaseRebelLegionsAction().execute(
        revenue_game.id, faction.id, {"Legions": release_ids}, FakeRandomResolver()
    )

    # Assert
    assert Legion.objects.get(id=keep_id).campaign == campaign
    assert not Legion.objects.filter(
        id__in=release_ids, campaign__isnull=False
    ).exists()


@pytest.mark.django_db
def test_released_legions_marked_with_flag(revenue_game: Game):
    # Arrange
    _, faction, _, legions = _setup_rebel_legions_release(revenue_game, [1, 2])
    release_ids = [l.id for l in legions]

    # Act
    ReleaseRebelLegionsAction().execute(
        revenue_game.id, faction.id, {"Legions": release_ids}, FakeRandomResolver()
    )

    # Assert
    assert Legion.objects.filter(id__in=release_ids, released_by_rebel=True).count() == 2


@pytest.mark.django_db
def test_game_progresses_to_released_legions_disbandment_after_release(revenue_game: Game):
    # Arrange
    _, faction, _, legions = _setup_rebel_legions_release(revenue_game, [1])
    release_ids = [l.id for l in legions]

    # Act
    ReleaseRebelLegionsAction().execute(
        revenue_game.id, faction.id, {"Legions": release_ids}, FakeRandomResolver()
    )

    # Assert
    revenue_game.refresh_from_db()
    assert revenue_game.sub_phase == Game.SubPhase.RELEASED_LEGIONS_DISBANDMENT


@pytest.mark.django_db
def test_rebel_awaiting_decision_cleared_after_release(revenue_game: Game):
    # Arrange
    _, faction, _, legions = _setup_rebel_legions_release(revenue_game, [1])
    release_ids = [l.id for l in legions]

    # Act
    ReleaseRebelLegionsAction().execute(
        revenue_game.id, faction.id, {"Legions": release_ids}, FakeRandomResolver()
    )

    # Assert
    faction.refresh_from_db()
    assert not faction.has_status_item(FactionStatusItem.AWAITING_DECISION)


@pytest.mark.django_db
def test_release_logged_with_rebel_name(revenue_game: Game):
    # Arrange
    senator, faction, campaign, legions = _setup_rebel_legions_release(
        revenue_game, [1, 2, 3]
    )
    revenue_game.rebel_legions_to_release = 1
    revenue_game.save()
    release_ids = [legions[2].id]

    # Act
    ReleaseRebelLegionsAction().execute(
        revenue_game.id, faction.id, {"Legions": release_ids}, FakeRandomResolver()
    )

    # Assert
    rebel_name = senator.display_name
    assert Log.objects.filter(
        game=revenue_game,
        text__contains=f"{rebel_name} released",
    ).exists()


@pytest.mark.django_db
def test_cannot_release_wrong_number_of_units(revenue_game: Game):
    # Arrange
    _, faction, _, legions = _setup_rebel_legions_release(revenue_game, [1, 2, 3])
    revenue_game.rebel_legions_to_release = 2
    revenue_game.save()

    # Act
    result = ReleaseRebelLegionsAction().execute(
        revenue_game.id, faction.id, {"Legions": [legions[0].id]}, FakeRandomResolver()
    )

    # Assert
    assert not result.success


@pytest.mark.django_db
def test_cannot_release_units_outside_rebel_campaign(revenue_game: Game):
    # Arrange
    _, faction, _, legions = _setup_rebel_legions_release(revenue_game, [1, 2])
    reserve_legion = Legion.objects.create(game=revenue_game, number=5)

    # Act
    result = ReleaseRebelLegionsAction().execute(
        revenue_game.id,
        faction.id,
        {"Legions": [reserve_legion.id, legions[0].id]},
        FakeRandomResolver(),
    )

    # Assert
    assert not result.success
