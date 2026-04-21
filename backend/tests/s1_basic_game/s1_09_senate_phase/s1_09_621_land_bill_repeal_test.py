import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Game, Senator


def _setup_repeal_vote(game: Game, bill_type: str, yea: int, nay: int) -> Senator:
    senator = Senator.objects.filter(game=game, alive=True).first()
    assert senator is not None
    game.current_proposal = (
        f"Repeal type {bill_type} land bill sponsored by {senator.display_name}"
    )
    game.votes_yea = yea
    game.votes_nay = nay
    game.save()
    senator.add_status_item(Senator.StatusItem.VOTED_YEA)
    senator.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()
    return senator


@pytest.mark.django_db
def test_land_bill_repeal_pass_removes_effect_marker(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.add_effect(GameEffect.LAND_BILL_2)
    game.save()
    _setup_repeal_vote(game, "II", 15, 0)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.LAND_BILL_2) == 0


@pytest.mark.django_db
def test_land_bill_repeal_pass_increases_unrest(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.unrest = 1
    game.add_effect(GameEffect.LAND_BILL_2)
    game.save()
    _setup_repeal_vote(game, "II", 15, 0)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.unrest == 3


@pytest.mark.django_db
def test_land_bill_repeal_pass_reduces_sponsor_popularity(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.add_effect(GameEffect.LAND_BILL_2)
    game.save()
    sponsor = _setup_repeal_vote(game, "II", 15, 0)
    sponsor.popularity = 5
    sponsor.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    sponsor.refresh_from_db()
    assert sponsor.popularity == 2


@pytest.mark.django_db
def test_land_bill_repeal_pass_type_iii_sponsor_popularity(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.add_effect(GameEffect.LAND_BILL_3)
    game.save()
    sponsor = _setup_repeal_vote(game, "III", 15, 0)
    sponsor.popularity = 8
    sponsor.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    sponsor.refresh_from_db()
    assert sponsor.popularity == 2


@pytest.mark.django_db
def test_land_bill_repeal_pass_voted_yea_non_sponsor_loses_popularity(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.add_effect(GameEffect.LAND_BILL_2)
    game.save()
    senators = list(Senator.objects.filter(game=game, alive=True))
    sponsor = senators[0]
    other = senators[1]
    game.current_proposal = (
        f"Repeal type II land bill sponsored by {sponsor.display_name}"
    )
    game.votes_yea = 15
    game.votes_nay = 0
    game.save()
    other.add_status_item(Senator.StatusItem.VOTED_YEA)
    other.save()
    initial_pop = other.popularity
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    other.refresh_from_db()
    assert other.popularity == initial_pop - 1


@pytest.mark.django_db
def test_land_bill_repeal_pass_only_removes_one_marker(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.add_effect(GameEffect.LAND_BILL_2)
    game.add_effect(GameEffect.LAND_BILL_2)
    game.save()
    _setup_repeal_vote(game, "II", 15, 0)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.LAND_BILL_2) == 1


@pytest.mark.django_db
def test_land_bill_repeal_pass_blocks_second_repeal(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.add_effect(GameEffect.LAND_BILL_2)
    game.save()
    _setup_repeal_vote(game, "II", 15, 0)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.has_unavailable_proposal("repeal type II land bill")


@pytest.mark.django_db
def test_land_bill_repeal_fail_blocks_second_repeal(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.add_effect(GameEffect.LAND_BILL_2)
    game.save()
    _setup_repeal_vote(game, "II", 0, 15)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.has_unavailable_proposal("repeal type II land bill")


@pytest.mark.django_db
def test_land_bill_repeal_fail_keeps_effect_marker(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.add_effect(GameEffect.LAND_BILL_2)
    game.save()
    _setup_repeal_vote(game, "II", 0, 15)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.LAND_BILL_2) == 1
