import pytest
from rorapp.actions.vote_nay import VoteNayAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
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
