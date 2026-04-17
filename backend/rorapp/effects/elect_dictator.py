from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.dictator_appointment import appoint_dictator
from rorapp.helpers.clear_proposal_and_votes import clear_proposal_and_votes
from rorapp.helpers.unanimous_defeat import handle_unanimous_defeat
from rorapp.models import Game, Senator
from rorapp.models.log import Log


class ElectDictatorEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.DICTATOR_ELECTION
            and not (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
            and all(
                f.has_status_item(FactionStatusItem.DONE) for f in game_state.factions
            )
            and game_state.game.current_proposal.startswith("Elect Dictator ")
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        if not game.current_proposal:
            return False
        senator_name = game.current_proposal[len("Elect Dictator "):]
        senators = Senator.objects.filter(game=game_id, alive=True)
        dictator_candidate = next(
            (s for s in senators if s.display_name == senator_name), None
        )

        if game.votes_yea > game.votes_nay:
            Log.create_object(game.id, f"Motion passed: {game.current_proposal}.")
            clear_proposal_and_votes(game_id)
            if dictator_candidate:
                appoint_dictator(game_id, dictator_candidate.id)
        else:
            game.add_defeated_proposal(game.current_proposal)
            Log.create_object(
                game_id,
                f"Motion defeated: {game.current_proposal}.",
            )
            game.save()
            handle_unanimous_defeat(game_id)
            clear_proposal_and_votes(game_id)

        return True
