from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.clear_proposal_and_votes import clear_proposal_and_votes
from rorapp.models import Faction, Game, Senator
from rorapp.models.log import Log


class ElectConsulsEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.CONSULAR_ELECTION
            and not (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
            and all(
                f.has_status_item(Faction.StatusItem.DONE) for f in game_state.factions
            )
            and game_state.game.current_proposal.startswith("Elect consuls ")
        )

    def execute(self, game_id: int) -> bool:

        game = Game.objects.get(id=game_id)
        if not game.current_proposal:
            return False

        if game.votes_yea > game.votes_nay:
            # Proposal passed
            Log.create_object(game.id, f"Motion passed: {game.current_proposal}")
            consul_names = game.current_proposal[len("Elect consuls ") :].split(" and ")
            senators = Senator.objects.filter(game=game, alive=True)
            consuls = [s for s in senators if s.display_name in consul_names]
            for consul in consuls:
                consul.add_status_item(Senator.StatusItem.INCOMING_CONSUL)
                consul.save()
            game.defeated_proposals = []
            game.save()
        else:
            # Proposal failed
            game.defeated_proposals.append(game.current_proposal)
            game.save()

        clear_proposal_and_votes(game_id)

        return True
