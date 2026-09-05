from typing import Callable

import pytest
from rorapp.actions.give_speech import GiveSpeechAction
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.helpers.hrao import set_hrao
from rorapp.models import Campaign, Game, Log, Senator


@pytest.mark.django_db
def test_bankruptcy_hands_the_game_to_a_rebel(
    rebel_army: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    game = rebel_army().game
    game.state_treasury = -1
    game.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.rebel_winning_condition == 2
    assert game.finished_on is not None


@pytest.mark.django_db
def test_bankruptcy_still_ends_the_game_without_a_rebel(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.START
    game.state_treasury = -1
    game.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.rebel_winning_condition == 0
    assert game.finished_on is not None


@pytest.mark.django_db
def test_a_people_revolt_hands_the_game_to_a_rebel(
    rebel_army: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    game = rebel_army().game
    game.phase = Game.Phase.POPULATION
    game.sub_phase = Game.SubPhase.STATE_OF_REPUBLIC_SPEECH
    game.unrest = 9
    game.save()
    set_hrao(game.id)
    hrao = Senator.objects.get(game=game, titles__contains=["HRAO"])
    resolver.dice_rolls = [3]

    # Act
    assert hrao.faction_id is not None
    GiveSpeechAction().execute(game.id, hrao.faction_id, {}, resolver)
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.rebel_winning_condition == 2
    assert game.finished_on is not None


@pytest.mark.django_db
def test_a_rebel_does_not_count_towards_the_era_ends_win(
    rebel_army: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    game = rebel_army().game
    rebel = Senator.objects.get(game=game, family_name="Cornelius")
    rebel.influence = 40
    rebel.save()
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.ERA_ENDS
    game.rebel_winning_condition = 0
    game.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Log.objects.filter(
        game=game, text="The era has ended! Faction 1 wins with 14 influence."
    ).exists()
