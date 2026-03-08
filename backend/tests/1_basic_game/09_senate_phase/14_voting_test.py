import pytest
from rorapp.actions.vote_yea import VoteYeaAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Faction, Game


@pytest.mark.django_db
def test_faction_votes_added_on_yea_vote(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.current_proposal = "Test proposal"
    game.save()
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    faction.save()
    initial_votes_yea = game.votes_yea
    faction_votes = sum(s.votes for s in faction.senators.all())

    # Act
    result = VoteYeaAction().execute(game.id, faction.id, {}, resolver)

    # Assert
    assert result.success
    game.refresh_from_db()
    assert game.votes_yea == initial_votes_yea + faction_votes
