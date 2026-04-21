import pytest
from rorapp.classes.concession import Concession
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Game, Senator


@pytest.mark.django_db
def test_land_commissioner_returned_to_forum_when_no_land_bill(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.END
    game.save()
    senator = Senator.objects.filter(game=game, alive=True).first()
    assert senator is not None
    senator.add_concession(Concession.LAND_COMMISSIONER)
    senator.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    senator.refresh_from_db()
    assert not senator.has_concession(Concession.LAND_COMMISSIONER)
    game.refresh_from_db()
    assert Concession.LAND_COMMISSIONER.value in game.concessions


@pytest.mark.django_db
def test_land_commissioner_kept_when_land_bill_in_effect(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.END
    game.add_effect(GameEffect.LAND_BILL_2)
    game.save()
    senator = Senator.objects.filter(game=game, alive=True).first()
    assert senator is not None
    senator.add_concession(Concession.LAND_COMMISSIONER)
    senator.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    senator.refresh_from_db()
    assert senator.has_concession(Concession.LAND_COMMISSIONER)
    game.refresh_from_db()
    assert Concession.LAND_COMMISSIONER.value not in game.concessions
