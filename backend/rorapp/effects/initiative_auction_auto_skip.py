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
                if faction.has_status_item(Faction.StatusItem.CURRENT_BIDDER) and not faction.has_status_item(Faction.StatusItem.SKIPPED):
                    for f in game_state.factions:
                        bid_amount = f.get_bid_amount()
                        if bid_amount and not any(
                            s.talents > bid_amount
                            for s in game_state.senators
                            if s.faction and s.faction.id == faction.id and s.alive
                        ):
                            return True
        return False

    def execute(self, game_id: int) -> bool:
        factions = Faction.objects.filter(game=game_id)
        for faction in factions:
            if faction.has_status_item(Faction.StatusItem.CURRENT_BIDDER):
                faction.add_status_item(Faction.StatusItem.SKIPPED)
                return True
        return False
