from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Game


class SponsorGamesAutoSkipEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        if (
            game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.SPONSOR_GAMES
        ):
            for faction in game_state.factions:
                if faction.has_status_item(FactionStatusItem.CURRENT_INITIATIVE):
                    return not any(
                        s.talents >= 7
                        for s in game_state.senators
                        if s.faction and s.faction.id == faction.id and s.alive
                    )
        return False

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        # Progress game
        game = Game.objects.get(id=game_id)
        game.sub_phase = Game.SubPhase.FACTION_LEADER
        game.save()
        return True
