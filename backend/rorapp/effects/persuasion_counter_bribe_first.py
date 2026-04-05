from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.get_next_faction_in_order import get_next_faction_in_order
from rorapp.models import Faction, Game, Senator


class PersuasionCounterBribeFirstEffect(EffectBase):
    """Set up the first counter-bidder at the start of each counter-bribe round."""

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.PERSUASION_COUNTER_BRIBE
            and not any(
                f.has_status_item(FactionStatusItem.CURRENT_COUNTER_BRIBER)
                for f in game_state.factions
            )
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        factions = Faction.objects.filter(game=game_id)

        persuading_senator = next(
            (
                s
                for s in Senator.objects.filter(game=game_id, alive=True)
                if s.has_status_item(Senator.StatusItem.PERSUADER)
            ),
            None,
        )
        if not persuading_senator:
            return False
        persuader = next(
            (f for f in factions if f.id == persuading_senator.faction_id), None
        )
        if not persuader:
            return False

        # Clear per-round markers from previous round
        for faction in factions:
            faction.remove_status_item(FactionStatusItem.SKIPPED)
            faction.remove_status_item(FactionStatusItem.COUNTER_BRIBED)
            faction.save()

        first_counter_bidder = get_next_faction_in_order(factions, persuader.position)
        first_counter_bidder.add_status_item(FactionStatusItem.CURRENT_COUNTER_BRIBER)
        first_counter_bidder.save()

        return True
