from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.end_prosecutions import end_prosecutions
from rorapp.helpers.prosecution_eligible import has_minor_prosecution_target, has_major_prosecution_target
from rorapp.models import Game, Log, Senator


class AutoCloseProsecutionsEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        if not (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.PROSECUTION
            and (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
            and not any(
                f.has_status_item(FactionStatusItem.CALLED_TO_VOTE)
                for f in game_state.factions
            )
        ):
            return False

        censor = next(
            (s for s in game_state.senators if s.has_title(Senator.Title.CENSOR)),
            None,
        )
        if not censor or not censor.has_title(Senator.Title.PRESIDING_MAGISTRATE):
            return False

        defeated = game_state.game.defeated_proposals
        senators = game_state.senators

        minor_possible = (
            game_state.game.prosecutions_remaining >= 1
            and has_minor_prosecution_target(senators, defeated, censor.id)
        )
        major_possible = (
            game_state.game.prosecutions_remaining == 2
            and has_major_prosecution_target(senators, defeated, censor.id)
        )

        return not minor_possible and not major_possible

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        senators = list(Senator.objects.filter(game=game_id, alive=True))
        censor = next((s for s in senators if s.has_title(Senator.Title.CENSOR)), None)

        game = Game.objects.get(id=game_id)
        if game.prosecutions_remaining == 2:
            log_text = (
                f"{censor.display_name} found no senators eligible for prosecution."
                if censor else "No senators were eligible for prosecution."
            )
        else:
            log_text = (
                f"{censor.display_name} found no further senators eligible for prosecution."
                if censor else "No further senators were eligible for prosecution."
            )

        Log.create_object(game_id=game_id, text=log_text)
        end_prosecutions(game_id)
        return True
