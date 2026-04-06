from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.get_next_faction_in_order import get_next_faction_in_order
from rorapp.models import Faction, Game, Log


class PlayCardsAutoSkipEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        if game_state.game.sub_phase != Game.SubPhase.PLAY_STATESMEN_CONCESSIONS or game_state.game.phase not in (
            Game.Phase.INITIAL,
            Game.Phase.REVOLUTION,
        ):
            return False

        current_faction = next(
            (f for f in game_state.factions if f.has_status_item(FactionStatusItem.AWAITING_DECISION)),
            None,
        )
        return current_faction is not None and len(current_faction.cards) == 0

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        factions = Faction.objects.filter(game=game_id)
        current_faction = factions.get(status_items__contains=[FactionStatusItem.AWAITING_DECISION.value])

        current_faction.add_status_item(FactionStatusItem.DONE)
        current_faction.remove_status_item(FactionStatusItem.AWAITING_DECISION)
        current_faction.save()

        next_faction = get_next_faction_in_order(factions, current_faction.position)
        if not next_faction.has_status_item(FactionStatusItem.DONE):
            next_faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
            next_faction.save()

        return True
