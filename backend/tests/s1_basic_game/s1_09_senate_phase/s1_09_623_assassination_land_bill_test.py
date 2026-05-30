import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Game, Senator


def _setup_land_bill_assassination(
    game: Game,
    assassin: Senator,
    target: Senator,
    roll_result: int,
    caught: bool = False,
):
    sponsor = target
    cosponsor = Senator.objects.get(game=game, family_name="Manlius")
    proposal = (
        f"Pass type II land bill"
        f" sponsored by {sponsor.display_name}"
        f" and co-sponsored by {cosponsor.display_name}"
    )
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.ASSASSINATION_RESOLUTION
    game.assassination_roll_result = roll_result
    game.assassination_roll_modifier = 0
    game.bodyguard_rerolls_remaining = 0
    game.interrupted_sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.current_proposal = proposal
    game.save()
    assassin.add_status_item(Senator.StatusItem.ASSASSIN)
    if caught:
        assassin.add_status_item(Senator.StatusItem.CAUGHT)
    assassin.save()
    target.add_status_item(Senator.StatusItem.ASSASSINATION_TARGET)
    target.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    target.save()
    cosponsor.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    cosponsor.save()


@pytest.mark.django_db
def test_caught_during_land_bill_only_kills_assassin(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    _setup_land_bill_assassination(
        game, cornelius, claudius, roll_result=1, caught=True
    )

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    cornelius.refresh_from_db()
    claudius.refresh_from_db()
    assert not cornelius.alive
    assert claudius.alive


@pytest.mark.django_db
def test_land_bill_vote_continues_when_sponsor_killed(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    original_proposal = (
        f"Pass type II land bill"
        f" sponsored by {claudius.display_name}"
        f" and co-sponsored by Manlius"
    )
    _setup_land_bill_assassination(game, cornelius, claudius, roll_result=5)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.current_proposal == original_proposal


@pytest.mark.django_db
def test_land_bill_vote_continues_after_no_effect_roll(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    _setup_land_bill_assassination(game, cornelius, claudius, roll_result=4)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS
    assert game.current_proposal is not None
    assert "land bill" in game.current_proposal.lower()
