from typing import Callable

import pytest
from rorapp.actions.attack_war import AttackWarAction
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Campaign, Fleet, Game, Legion, Senator, War


def _attack(game: Game, war: War, resolver: FakeRandomResolver):
    rebel = Senator.objects.get(game=game, family_name="Cornelius")
    result = AttackWarAction().execute(
        game.id, rebel.faction_id, {"War": war.id}, resolver
    )
    execute_effects_and_manage_actions(game.id, resolver)
    return result


@pytest.mark.django_db
def test_the_rebel_wins_outright_below_four_wars(
    rebel_army: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    game = rebel_army(other_wars=2).game

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.finished_on is not None
    assert game.sub_phase != Game.SubPhase.REBEL_END_GAME


@pytest.mark.django_db
def test_four_wars_send_the_rebel_to_the_end_game(
    rebel_army: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = rebel_army(other_wars=4)
    game = campaign.game
    Legion.objects.create(game=game, number=20)
    Fleet.objects.create(game=game, number=1)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.finished_on is None
    assert game.sub_phase == Game.SubPhase.REBEL_END_GAME
    assert Legion.objects.filter(game=game, campaign=campaign).count() == 4
    assert Fleet.objects.filter(game=game, campaign=campaign).count() == 1


@pytest.mark.django_db
def test_the_rebel_wins_by_beating_a_war_back_below_four(
    rebel_army: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = rebel_army(legion_numbers=list(range(1, 16)), other_wars=4)
    game = campaign.game
    execute_effects_and_manage_actions(game.id, resolver)
    war = War.objects.filter(game=game, primary_rebel__isnull=True).first()
    assert war is not None
    resolver.dice_rolls = [18]

    # Act
    _attack(game, war, resolver)

    # Assert
    game.refresh_from_db()
    assert game.finished_on is not None
    assert War.objects.filter(game=game, primary_rebel__isnull=True).count() == 3


@pytest.mark.django_db
def test_everyone_loses_when_the_rebel_fails_to_win_a_battle(
    rebel_army: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = rebel_army(legion_numbers=[1, 2], other_wars=4)
    game = campaign.game
    execute_effects_and_manage_actions(game.id, resolver)
    war = War.objects.filter(game=game, primary_rebel__isnull=True).first()
    assert war is not None
    resolver.dice_rolls = [12]

    # Act
    _attack(game, war, resolver)

    # Assert
    game.refresh_from_db()
    assert game.finished_on is not None
    assert War.objects.filter(game=game, primary_rebel__isnull=True).count() == 4


@pytest.mark.django_db
def test_a_consul_for_life_wins_when_the_rebel_dies_in_the_last_battle(
    rebel_army: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = rebel_army(legion_numbers=list(range(1, 16)), other_wars=4)
    game = campaign.game
    consul_for_life = Senator.objects.get(game=game, family_name="Manlius")
    consul_for_life.add_title(Senator.Title.CONSUL_FOR_LIFE)
    consul_for_life.save()
    execute_effects_and_manage_actions(game.id, resolver)
    rebel = Senator.objects.get(game=game, family_name="Cornelius")
    war = War.objects.filter(game=game, primary_rebel__isnull=True).first()
    assert war is not None
    resolver.dice_rolls = [16]
    resolver.mortality_chits = [[rebel.code]]

    # Act
    _attack(game, war, resolver)

    # Assert
    game.refresh_from_db()
    rebel.refresh_from_db()
    assert rebel.alive == False
    assert game.finished_on is not None


@pytest.mark.django_db
def test_the_revolt_fails_when_the_rebel_dies_with_no_consul_for_life(
    rebel_army: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = rebel_army(legion_numbers=list(range(1, 16)), other_wars=4)
    game = campaign.game
    execute_effects_and_manage_actions(game.id, resolver)
    rebel = Senator.objects.get(game=game, family_name="Cornelius")
    war = War.objects.filter(game=game, primary_rebel__isnull=True).first()
    assert war is not None
    resolver.dice_rolls = [16]
    resolver.mortality_chits = [[rebel.code]]

    # Act
    _attack(game, war, resolver)

    # Assert
    game.refresh_from_db()
    rebel.refresh_from_db()
    assert rebel.alive == False
    assert game.finished_on is None
    assert War.objects.filter(game=game, primary_rebel__isnull=False).exists() == False
