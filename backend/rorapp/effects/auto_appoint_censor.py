from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.censor_candidates import get_eligible_censor_candidates
from rorapp.models import Game, Senator
from rorapp.models.log import Log


class AutoAppointCensorEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        if not (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.CENSOR_ELECTION
            and (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
        ):
            return False

        candidates, is_fallback = get_eligible_censor_candidates(game_state.senators)
        defeated_names = {
            p[len("Elect Censor "):] for p in game_state.game.defeated_proposals
            if p.startswith("Elect Censor ")
        }
        candidates = [c for c in candidates if c.display_name not in defeated_names]
        # Auto-appoint only when exactly one prior consul candidate (not fallback)
        return not is_fallback and len(candidates) == 1

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        game = Game.objects.get(id=game_id)
        senators = list(Senator.objects.filter(game=game_id, alive=True))
        candidates, is_fallback = get_eligible_censor_candidates(senators)
        defeated_names = {
            p[len("Elect Censor "):] for p in game.defeated_proposals
            if p.startswith("Elect Censor ")
        }
        candidates = [c for c in candidates if c.display_name not in defeated_names]

        if is_fallback or len(candidates) != 1:
            return False

        censor = candidates[0]

        # Remove PM and Censor title from whoever currently holds them
        for senator in senators:
            changed = False
            if senator.has_title(Senator.Title.PRESIDING_MAGISTRATE):
                senator.remove_title(Senator.Title.PRESIDING_MAGISTRATE)
                changed = True
            if senator.has_title(Senator.Title.CENSOR):
                senator.remove_title(Senator.Title.CENSOR)
                changed = True
            if changed:
                senator.save()

        censor.add_title(Senator.Title.CENSOR)
        censor.add_title(Senator.Title.PRESIDING_MAGISTRATE)
        censor.influence += 5
        censor.save()

        Log.create_object(
            game_id=game_id,
            text=f"{censor.display_name} was automatically appointed Censor.",
        )

        game.defeated_proposals = []
        game.sub_phase = Game.SubPhase.PROSECUTION
        game.prosecutions_remaining = 2
        game.save()
        return True
