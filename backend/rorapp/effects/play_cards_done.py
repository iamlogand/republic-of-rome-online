from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Game


class PlayCardsDoneEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.REVOLUTION
            and game_state.game.sub_phase == Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
            and all(
                f.has_status_item(FactionStatusItem.DONE) for f in game_state.factions
            )
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        game.sub_phase = Game.SubPhase.CIVIL_WAR_DECLARATION
        game.save()
        return True
