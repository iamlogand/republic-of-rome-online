import pytest
from rorapp.actions.cancel_tribune import CancelTribuneAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game


@pytest.mark.django_db
def test_faction_with_played_tribune_and_no_proposal_can_cancel(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    faction = Faction.objects.filter(game=game).first()
    assert faction is not None
    faction.add_status_item(FactionStatusItem.PLAYED_TRIBUNE)
    faction.save()

    # Act
    result = CancelTribuneAction().execute(game.id, faction.id, {}, resolver)

    # Assert
    assert result.success
    faction.refresh_from_db()
    assert not faction.has_status_item(FactionStatusItem.PLAYED_TRIBUNE)


@pytest.mark.django_db
def test_faction_cannot_cancel_tribune_when_proposal_is_on_floor(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.current_proposal = "Elect consuls Julius and Cornelius"
    game.save()
    faction = Faction.objects.filter(game=game).first()
    assert faction is not None
    faction.add_status_item(FactionStatusItem.PLAYED_TRIBUNE)
    faction.save()

    snapshot = GameStateSnapshot(game.id)

    # Act
    allowed = CancelTribuneAction().is_allowed(snapshot, faction.id)

    # Assert
    assert allowed is None
