from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Log, Senator


class InitiativeAuctionNextEffect(EffectBase):
    """In the initiative auction, pass the next opportunity to bid to the next faction."""

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.INITIATIVE_AUCTION
            and any(
                f.has_status_item(Faction.StatusItem.CURRENT_BIDDER)
                and (
                    f.get_bid_amount() is not None
                    or f.has_status_item(Faction.StatusItem.SKIPPED)
                )
                for f in game_state.factions
            )
        )

    def execute(self, game_id: int) -> bool:
        factions = Faction.objects.filter(game=game_id)
        positions = [f.position for f in factions.order_by("position")]

        for f in factions:
            if f.has_status_item(Faction.StatusItem.CURRENT_BIDDER):
                f.remove_status_item(Faction.StatusItem.CURRENT_BIDDER)
                previous_faction = f
                break

        # Figure out which faction is next
        next_position_index = positions.index(previous_faction.position) + 1
        next_position = (
            positions[next_position_index]
            if next_position_index < len(positions)
            else positions[0]
        )
        next_faction = factions.get(position=next_position)

        if next_faction.get_bid_amount() is None and not next_faction.has_status_item(
            Faction.StatusItem.SKIPPED
        ):
            # Pass to next faction
            next_faction.add_status_item(Faction.StatusItem.CURRENT_BIDDER)
            next_faction.save()
            return True

        # Bid has been all the way around
        winning_faction = None
        winning_bid_amount = 0
        for faction in Faction.objects.filter(game=game_id):
            bid_amount = faction.get_bid_amount()
            if bid_amount and bid_amount > winning_bid_amount:
                winning_faction = faction
        if not winning_faction:
            # Nobody placed a bid, so make the HRAO the winner by default
            for faction in Faction.objects.filter(game=game_id):
                if any(
                    s.has_title(Senator.Title.HRAO)
                    for s in Senator.objects.filter(
                        game=game_id, faction=faction.id, alive=True
                    )
                ):
                    winning_faction = faction
                    break
            if not winning_faction:
                return False
        winning_faction.add_status_item(Faction.StatusItem.AUCTION_WINNER)
        winning_faction.save()

        for initiative_index in Faction.INITIATIVE_INDICES:
            if not any(
                f.has_status_item(Faction.StatusItem.initiative(initiative_index))
                for f in factions
            ):
                if winning_bid_amount > 0:
                    Log.create_object(
                        game_id,
                        f"Sold to the highest bidder! {winning_faction.display_name} won the auction for initiative {initiative_index}.",
                    )
                else:
                    Log.create_object(
                        game_id,
                        f"{winning_faction.display_name} gets initiative {initiative_index} for free because nobody bid in the auction.",
                    )
                break

        # Initiate the end of the auction
        for faction in Faction.objects.filter(game=game_id):
            if faction.has_status_item(Faction.StatusItem.CURRENT_BIDDER):
                faction.remove_status_item(Faction.StatusItem.CURRENT_BIDDER)

        return True
