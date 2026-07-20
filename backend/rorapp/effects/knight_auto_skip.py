from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Game


class KnightAutoSkipEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        if not (
            game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.ATTRACT_KNIGHT
        ):
            return False

        evil_omens_level = game_state.game.count_effect(GameEffect.EVIL_OMENS)
        if evil_omens_level == 0:
            return False

        current_faction = next(
            (
                f
                for f in game_state.factions
                if f.has_status_item(FactionStatusItem.CURRENT_INITIATIVE)
            ),
            None,
        )
        if not current_faction:
            return False

        faction_senators = [
            s
            for s in game_state.senators
            if s.faction and s.faction.id == current_faction.id and s.alive
        ]
        if any(s.talents >= evil_omens_level for s in faction_senators):
            return False
        return not any(s.knights > 0 for s in faction_senators)

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        game.sub_phase = Game.SubPhase.SPONSOR_GAMES
        game.save()
        return True
