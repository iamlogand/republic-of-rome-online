import pytest
from rorapp.actions.propose_passing_land_bill import ProposePassingLandBillAction
from rorapp.actions.vote_nay import VoteNayAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Game, Senator


def _setup_land_bill_vote(game: Game, bill_type: str, yea: int, nay: int) -> tuple:
    senators = list(Senator.objects.filter(game=game, alive=True))
    sponsor = senators[0]
    cosponsor = senators[1]
    game.current_proposal = (
        f"Pass type {bill_type} land bill"
        f" sponsored by {sponsor.display_name}"
        f" and co-sponsored by {cosponsor.display_name}"
    )
    game.votes_yea = yea
    game.votes_nay = nay
    game.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()
    return sponsor, cosponsor


@pytest.mark.django_db
def test_land_bill_type_i_pass_reduces_unrest(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.unrest = 3
    game.save()
    _setup_land_bill_vote(game, "I", 15, 0)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.unrest == 2


@pytest.mark.django_db
def test_land_bill_type_ii_pass_reduces_unrest_by_2(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.unrest = 5
    game.save()
    _setup_land_bill_vote(game, "II", 15, 0)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.unrest == 3


@pytest.mark.django_db
def test_land_bill_type_iii_pass_reduces_unrest_by_3(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.unrest = 5
    game.save()
    _setup_land_bill_vote(game, "III", 15, 0)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.unrest == 2


@pytest.mark.django_db
def test_land_bill_pass_places_effect_marker(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    _setup_land_bill_vote(game, "II", 15, 0)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.LAND_BILL_2) == 1


@pytest.mark.django_db
def test_land_bill_pass_increases_sponsor_popularity(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    sponsor, _ = _setup_land_bill_vote(game, "II", 15, 0)
    initial_pop = sponsor.popularity

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    sponsor.refresh_from_db()
    assert sponsor.popularity == initial_pop + 2


@pytest.mark.django_db
def test_land_bill_pass_increases_cosponsor_popularity(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    _, cosponsor = _setup_land_bill_vote(game, "II", 15, 0)
    initial_pop = cosponsor.popularity

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    cosponsor.refresh_from_db()
    assert cosponsor.popularity == initial_pop + 1


@pytest.mark.django_db
def test_land_bill_pass_type_iii_sponsor_popularity(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    sponsor, _ = _setup_land_bill_vote(game, "III", 15, 0)
    initial_pop = sponsor.popularity

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    sponsor.refresh_from_db()
    assert sponsor.popularity == initial_pop + 4


@pytest.mark.django_db
def test_land_bill_pass_voted_nay_reduces_popularity(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    senators = list(Senator.objects.filter(game=game, alive=True))
    sponsor = senators[0]
    cosponsor = senators[1]
    game.current_proposal = (
        f"Pass type II land bill"
        f" sponsored by {sponsor.display_name}"
        f" and co-sponsored by {cosponsor.display_name}"
    )
    game.save()
    faction = game.factions.first()
    assert faction is not None
    faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    faction.save()
    voter = faction.senators.first()
    assert voter is not None
    initial_pop = voter.popularity

    # Act
    VoteNayAction().execute(game.id, faction.id, {}, resolver)

    # Assert
    voter.refresh_from_db()
    assert voter.popularity == initial_pop - 1


@pytest.mark.django_db
def test_land_bill_pass_blocks_same_type_reproposal(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    _setup_land_bill_vote(game, "II", 15, 0)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.has_unavailable_proposal("pass type II land bill")


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("marker_count", "expected_available"),
    ((1, True), (2, True), (3, False)),
)
def test_type_iii_land_bill_schema_respects_available_markers(
    senate_game: Game,
    marker_count: int,
    expected_available: bool,
):
    # Arrange
    game = senate_game
    for _ in range(marker_count):
        game.add_effect(GameEffect.LAND_BILL_3)
    game.save()
    presiding_magistrate = Senator.objects.get(
        game=game,
        titles__contains=Senator.Title.PRESIDING_MAGISTRATE.value,
    )
    assert presiding_magistrate.faction_id is not None
    snapshot = GameStateSnapshot(game.id)

    # Act
    schemas = ProposePassingLandBillAction().get_schema(
        snapshot,
        presiding_magistrate.faction_id,
    )

    # Assert
    assert len(schemas) == 1
    bill_type_field = next(
        field for field in schemas[0].field_descriptors if field["name"] == "Bill type"
    )
    available_types = {option["value"] for option in bill_type_field["options"]}
    assert ("III" in available_types) is expected_available


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("marker_count", "expected_success"),
    ((1, True), (2, True), (3, False)),
)
def test_type_iii_land_bill_proposal_respects_available_markers(
    senate_game: Game,
    resolver: FakeRandomResolver,
    marker_count: int,
    expected_success: bool,
):
    # Arrange
    game = senate_game
    for _ in range(marker_count):
        game.add_effect(GameEffect.LAND_BILL_3)
    game.save()
    faction = game.factions.first()
    assert faction is not None
    senators = list(Senator.objects.filter(game=game, alive=True)[:2])

    # Act
    result = ProposePassingLandBillAction().execute(
        game.id,
        faction.id,
        {
            "Bill type": "III",
            "Sponsor": senators[0].id,
            "Co-sponsor": senators[1].id,
        },
        resolver,
    )

    # Assert
    assert result.success is expected_success
    if not expected_success:
        assert result.message == (
            "The maximum number of type III land bills is already in effect."
        )


@pytest.mark.django_db
def test_land_bill_fail_blocks_same_type_reproposal(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    _setup_land_bill_vote(game, "I", 0, 15)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.has_unavailable_proposal("pass type I land bill")


@pytest.mark.django_db
def test_land_bill_fail_does_not_place_effect_marker(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    _setup_land_bill_vote(game, "II", 0, 15)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.LAND_BILL_2) == 0


@pytest.mark.django_db
def test_land_bill_type_i_unrest_capped_at_zero(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.unrest = 0
    game.save()
    _setup_land_bill_vote(game, "I", 15, 0)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.unrest == 0
