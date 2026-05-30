# TODO: §1.09.74 Special Major Prosecution is not yet implemented.
# When added, a guilty verdict should trigger: FL loses 5 influence,
# mortality chit draws equal to target popularity, and FL death.
# Currently only the assassin's execution is applied.

import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Game, Senator


def _setup_caught_assassin(
    game: Game,
    assassin: Senator,
    target: Senator,
    roll_result: int = 1,
):
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.ASSASSINATION_RESOLUTION
    game.assassination_roll_result = roll_result
    game.assassination_roll_modifier = 0
    game.bodyguard_rerolls_remaining = 0
    game.interrupted_sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    assassin.add_status_item(Senator.StatusItem.ASSASSIN)
    assassin.add_status_item(Senator.StatusItem.CAUGHT)
    assassin.save()
    target.add_status_item(Senator.StatusItem.ASSASSINATION_TARGET)
    target.save()


@pytest.mark.django_db
def test_caught_assassin_is_killed(senate_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    _setup_caught_assassin(game, cornelius, claudius)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    cornelius.refresh_from_db()
    assert not cornelius.alive


@pytest.mark.django_db
def test_caught_assassin_who_is_faction_leader_is_killed(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    cornelius.add_title(Senator.Title.FACTION_LEADER)
    cornelius.save()
    _setup_caught_assassin(game, cornelius, claudius)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert — FL death manifests as generation increment (heir inherits the family)
    cornelius.refresh_from_db()
    assert cornelius.generation > 1
