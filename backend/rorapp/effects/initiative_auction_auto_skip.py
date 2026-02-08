from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game


class InitiativeAuctionAutoSkipEffect(EffectBase):
    """
    In the initiative auction, if the next faction can't afford to raise the bid, automatically skip that faction.
    """

    def validate(self, game_state: GameStateSnapshot) -> bool:
        if (
            game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.INITIATIVE_AUCTION
        ):
            for faction in game_state.factions:
                if faction.has_status_item(
                    FactionStatusItem.CURRENT_BIDDER
                ) and not faction.has_status_item(FactionStatusItem.SKIPPED):
                    faction_senators = [
                        s
                        for s in game_state.senators
                        if s.faction and s.faction.id == faction.id and s.alive
                    ]
                    if all(s.talents == 0 for s in faction_senators):
                        return True
                    for other_faction in game_state.factions:
                        if other_faction.id != faction.id:
                            bid_amount = other_faction.get_bid_amount()
                            if bid_amount and not any(
                                s.talents > bid_amount for s in faction_senators
                            ):
                                return True
        return False

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        factions = Faction.objects.filter(game=game_id)
        for faction in factions:
            if faction.has_status_item(FactionStatusItem.CURRENT_BIDDER):
                faction.add_status_item(FactionStatusItem.SKIPPED)
                return True
        return False
