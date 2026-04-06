from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.resolve_persuasion import resolve_persuasion
from rorapp.models import Faction, Game, Senator


class PersuasionDecisionAutoResolveEffect(EffectBase):
    """Auto-resolve persuasion when the persuader has no meaningful decision to make.

    This is the case when nobody counter-bribed (so raising the bribe is not
    allowed) or when the persuader has no talents left to raise with.
    """

    def validate(self, game_state: GameStateSnapshot) -> bool:
        if not (
            game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.PERSUASION_DECISION
        ):
            return False

        persuading_senator = next(
            (
                s
                for s in game_state.senators
                if s.has_status_item(Senator.StatusItem.PERSUADER)
            ),
            None,
        )
        if not persuading_senator:
            return False

        no_counter_bribe = not any(
            f.has_status_item(FactionStatusItem.COUNTER_BRIBED)
            for f in game_state.factions
        )
        no_talents = persuading_senator.talents == 0
        return no_counter_bribe or no_talents

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        persuading_senator = next(
            (
                s
                for s in Senator.objects.filter(game=game_id, alive=True)
                if s.has_status_item(Senator.StatusItem.PERSUADER)
            ),
            None,
        )
        target = next(
            (
                s
                for s in Senator.objects.filter(game=game_id, alive=True)
                if s.has_status_item(Senator.StatusItem.PERSUASION_TARGET)
            ),
            None,
        )
        if not persuading_senator or not target:
            return False

        resolve_persuasion(game_id, persuading_senator, target, False, random_resolver)
        return True
