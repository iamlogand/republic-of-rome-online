import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.models import Faction, Game, Senator
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_revolution_start_gives_awaiting_decision_to_hrao_faction(basic_game: Game):

    # Arrange
    game = basic_game
    game.phase = Game.Phase.REVOLUTION
    game.sub_phase = Game.SubPhase.START
    game.save()

    hrao_faction: Faction = game.factions.get(position=2)
    hrao_senator = Senator.objects.filter(game=game, faction=hrao_faction).first()
    assert hrao_senator is not None
    hrao_senator.add_title(Senator.Title.HRAO)
    hrao_senator.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
    hrao_faction.refresh_from_db()
    assert hrao_faction.has_status_item(FactionStatusItem.AWAITING_DECISION)

    for faction in game.factions.exclude(id=hrao_faction.id):
        assert not faction.has_status_item(FactionStatusItem.AWAITING_DECISION)
