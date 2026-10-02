import pytest
from rorapp.actions.release_rebel_forces import ReleaseRebelForcesAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Campaign, Faction, Game, Legion, Log, Senator, War


def _setup_rebel_forces_release(
    game: Game, legion_numbers: list, state_treasury: int = 100
) -> tuple:
    """Set game to REBEL_FORCES_RELEASE with AWAITING_DECISION on the rebel faction,
    ready for ReleaseRebelForcesAction.
    """
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

    hrao_candidate = Senator.objects.filter(game=game, alive=True).exclude(id=senator.id).first()
    if hrao_candidate:
        hrao_candidate.add_title(Senator.Title.HRAO)
        hrao_candidate.save()

    faction = senator.faction
    faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
    faction.save()

    game.phase = Game.Phase.REVENUE
    game.sub_phase = Game.SubPhase.REBEL_FORCES_RELEASE
    game.state_treasury = state_treasury
    game.rebel_units_to_release = len(legions)
    game.save()

    return senator, faction, campaign, legions


@pytest.mark.django_db
def test_rebel_chooses_which_legions_to_release(revenue_game: Game):
    # Arrange
    senator, faction, campaign, legions = _setup_rebel_forces_release(revenue_game, [1, 2, 3])
    senator.talents = 0
    senator.save()
    game_rebel_units_to_release = 2
    revenue_game.rebel_units_to_release = game_rebel_units_to_release
    revenue_game.save()
    keep_id = legions[0].id
    release_ids = [l.id for l in legions[1:]]

    # Act
    ReleaseRebelForcesAction().execute(
        revenue_game.id, faction.id, {"Legions": release_ids}, FakeRandomResolver()
    )

    # Assert — rebel chose which legions to release
    assert Legion.objects.get(id=keep_id).campaign == campaign
    assert not Legion.objects.filter(id__in=release_ids, campaign__isnull=False).exists()


@pytest.mark.django_db
def test_rebel_awaiting_decision_cleared_after_release(revenue_game: Game):
    # Arrange
    senator, faction, campaign, legions = _setup_rebel_forces_release(revenue_game, [1])
    release_ids = [l.id for l in legions]

    # Act
    ReleaseRebelForcesAction().execute(
        revenue_game.id, faction.id, {"Legions": release_ids}, FakeRandomResolver()
    )

    # Assert
    faction.refresh_from_db()
    assert not faction.has_status_item(FactionStatusItem.AWAITING_DECISION)


@pytest.mark.django_db
def test_maintenance_log_created_for_kept_legions(revenue_game: Game):
    # Arrange
    senator, faction, campaign, legions = _setup_rebel_forces_release(revenue_game, [1, 2, 3])
    revenue_game.rebel_units_to_release = 1
    revenue_game.save()
    release_ids = [legions[2].id]

    # Act
    ReleaseRebelForcesAction().execute(
        revenue_game.id, faction.id, {"Legions": release_ids}, FakeRandomResolver()
    )

    # Assert
    rebel_name = senator.display_name
    assert Log.objects.filter(
        game=revenue_game,
        text__contains=f"{rebel_name} spent 4T maintaining",
    ).exists()


@pytest.mark.django_db
def test_cannot_release_wrong_number_of_units(revenue_game: Game):
    # Arrange
    _, faction, _, legions = _setup_rebel_forces_release(revenue_game, [1, 2, 3])
    revenue_game.rebel_units_to_release = 2
    revenue_game.save()

    # Act — only 1 selected but 2 required
    result = ReleaseRebelForcesAction().execute(
        revenue_game.id, faction.id, {"Legions": [legions[0].id]}, FakeRandomResolver()
    )

    # Assert
    assert not result.success


@pytest.mark.django_db
def test_cannot_release_units_outside_rebel_campaign(revenue_game: Game):
    # Arrange
    _, faction, _, legions = _setup_rebel_forces_release(revenue_game, [1, 2])
    reserve_legion = Legion.objects.create(game=revenue_game, number=5)

    # Act — tries to release a reserve legion not in the rebel campaign
    result = ReleaseRebelForcesAction().execute(
        revenue_game.id, faction.id, {"Legions": [reserve_legion.id, legions[0].id]}, FakeRandomResolver()
    )

    # Assert
    assert not result.success
