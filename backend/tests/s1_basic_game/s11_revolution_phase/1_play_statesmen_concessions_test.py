import pytest
from rorapp.actions.play_concession import PlayConcessionAction
from rorapp.classes.concession import Concession
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Senator
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_hrao_faction_gets_awaiting_decision_at_revolution_start(revolution_game: Game):
    # Arrange
    game = revolution_game
    hrao_faction: Faction = game.factions.get(position=2)
    hrao_senator = Senator.objects.filter(game=game, faction=hrao_faction).first()
    assert hrao_senator is not None
    hrao_senator.add_title(Senator.Title.HRAO)
    hrao_senator.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    hrao_faction.refresh_from_db()
    assert hrao_faction.has_status_item(FactionStatusItem.AWAITING_DECISION)
    for faction in game.factions.exclude(id=hrao_faction.id):
        assert not faction.has_status_item(FactionStatusItem.AWAITING_DECISION)


@pytest.mark.django_db
def test_concession_played_to_senator_during_revolution(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.REVOLUTION
    game.sub_phase = Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
    game.save()

    faction: Faction = game.factions.get(position=1)
    faction.cards = [f"concession:{Concession.MINING.value}"]
    faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
    faction.save()

    senator = Senator.objects.filter(game=game, faction=faction).first()
    assert senator is not None

    # Act
    result = PlayConcessionAction().execute(
        game.id,
        faction.id,
        {"Senator": str(senator.id), "Concession": f"concession:{Concession.MINING.value}"},
        FakeRandomResolver(),
    )

    # Assert
    assert result.success
    senator.refresh_from_db()
    assert Concession.MINING.value in senator.concessions
    faction.refresh_from_db()
    assert f"concession:{Concession.MINING.value}" not in faction.cards


@pytest.mark.django_db
def test_concession_not_playable_without_concession_cards(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.REVOLUTION
    game.sub_phase = Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
    game.save()

    faction: Faction = game.factions.get(position=1)
    faction.cards = []
    faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
    faction.save()

    snapshot = GameStateSnapshot(game.id)

    # Act
    result = PlayConcessionAction().get_schema(snapshot, faction.id)

    # Assert
    assert result == []
