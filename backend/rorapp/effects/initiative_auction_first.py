from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Log, Senator


class InitiativeAuctionFirstEffect(EffectBase):
    """Find the faction with the HRAO and gives them an opportunity to place the first bid in the initiative auction."""

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.INITIATIVE_AUCTION
            and not any(
                f.has_status_item(FactionStatusItem.CURRENT_BIDDER)
                or f.has_status_item(FactionStatusItem.AUCTION_WINNER)
                or f.has_status_item(FactionStatusItem.CURRENT_INITIATIVE)
                for f in game_state.factions
            )
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        factions = Faction.objects.filter(game=game_id)
        for initiative_index in Faction.INITIATIVE_INDICES:
            if not any(
                f.has_status_item(FactionStatusItem.initiative(initiative_index))
                for f in factions
            ):
                for faction in factions:
                    if any(
                        s.has_title(Senator.Title.HRAO)
                        for s in Senator.objects.filter(
                            game=game_id, faction=faction.id, alive=True
                        )
                    ):
                        faction.add_status_item(FactionStatusItem.CURRENT_BIDDER)
                        faction.save()
                        Log.create_object(
                            game_id=game_id,
                            text=f"Initiative {initiative_index} will be sold to the highest bidder via auction.",
                        )
                        return True
        return False
