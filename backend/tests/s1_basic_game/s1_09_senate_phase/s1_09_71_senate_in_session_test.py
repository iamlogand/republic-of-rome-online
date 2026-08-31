import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Faction, Game


@pytest.mark.django_db
def test_assassination_tracking_cleared_when_senate_adjourns(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.END
    game.save()
    faction_a = Faction.objects.filter(game=game, position=1).first()
    faction_b = Faction.objects.filter(game=game, position=2).first()
    assert faction_a is not None
    assert faction_b is not None
    faction_a.add_status_item(FactionStatusItem.ATTEMPTED_ASSASSINATION)
    faction_a.save()
    faction_b.add_status_item(FactionStatusItem.ASSASSINATION_TARGETED)
    faction_b.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    faction_a.refresh_from_db()
    faction_b.refresh_from_db()
    assert not faction_a.has_status_item(FactionStatusItem.ATTEMPTED_ASSASSINATION)
    assert not faction_b.has_status_item(FactionStatusItem.ASSASSINATION_TARGETED)
