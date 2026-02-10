import pytest
from rorapp.actions.play_concession import PlayConcessionAction
from rorapp.classes.concession import Concession
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Senator


@pytest.mark.django_db
def test_play_concession(basic_game: Game):

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

    action = PlayConcessionAction()
    selection = {"Senator": str(senator.id), "Concession": f"concession:{Concession.MINING.value}"}

    # Act
    result = action.execute(
        game.id,
        faction.id,
        selection,
        FakeRandomResolver(),
    )

    # Assert
    assert result.success
    faction.refresh_from_db()
    assert f"concession:mining" not in faction.cards
    senator.refresh_from_db()
    assert Concession.MINING.value in senator.concessions
    expected_message = f"{senator.display_name} of {faction.display_name} received the mining concession."
    assert game.logs.filter(text=expected_message).count() == 1


@pytest.mark.django_db
def test_play_concession_not_available_without_concession_cards(basic_game: Game):

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
    action = PlayConcessionAction()

    # Act
    result = action.get_schema(snapshot, faction.id)

    # Assert
    assert result == []
