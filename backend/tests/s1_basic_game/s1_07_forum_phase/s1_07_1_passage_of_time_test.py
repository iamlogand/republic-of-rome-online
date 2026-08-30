import pytest
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Game, Senator


@pytest.mark.django_db
def test_temporary_effects_expire_at_start_of_forum_phase(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.START
    game.add_effect(GameEffect.MANPOWER_SHORTAGE)
    game.save()

    senator = Senator.objects.filter(game=game, alive=True).first()
    assert senator is not None
    senator.add_title(Senator.Title.HRAO)
    senator.save()

    resolver.dice_rolls = [6]  # Non-7 initiative roll to avoid triggering an event

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.effects == []


@pytest.mark.django_db
def test_permanent_land_bills_remain_at_start_of_forum_phase(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.START
    game.add_effect(GameEffect.LAND_BILL_2)
    game.add_effect(GameEffect.LAND_BILL_2)
    game.add_effect(GameEffect.LAND_BILL_3)
    game.add_effect(GameEffect.MANPOWER_SHORTAGE)
    game.save()

    senator = Senator.objects.filter(game=game, alive=True).first()
    assert senator is not None
    senator.add_title(Senator.Title.HRAO)
    senator.save()

    resolver.dice_rolls = [6]  # Non-7 initiative roll to avoid triggering an event

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.LAND_BILL_2) == 2
    assert game.count_effect(GameEffect.LAND_BILL_3) == 1
    assert not game.has_effect(GameEffect.MANPOWER_SHORTAGE)
