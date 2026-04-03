import pytest
from rorapp.actions.initiative_auction_bid import InitiativeAuctionBidAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Senator


@pytest.mark.django_db
def test_min_bid_is_higher_than_previous_highest_bid(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.INITIATIVE_AUCTION
    game.save()

    faction1: Faction = game.factions.get(position=1)
    faction2: Faction = game.factions.get(position=2)
    faction3: Faction = game.factions.get(position=3)

    faction3.set_bid_amount(1)
    faction3.save()

    faction1.set_bid_amount(2)
    faction1.save()

    faction2.add_status_item(FactionStatusItem.CURRENT_BIDDER)
    faction2.save()

    senator = Senator.objects.filter(game=game, faction=faction2).first()
    assert senator
    senator.talents = 5
    senator.save()

    snapshot = GameStateSnapshot(game.id)

    # Act
    result = InitiativeAuctionBidAction().get_schema(snapshot, faction2.id)

    # Assert
    assert len(result) == 1
    schema = result[0].schema
    assert schema[0]["min"] == [3]
