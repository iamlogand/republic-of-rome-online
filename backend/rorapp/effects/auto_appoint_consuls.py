from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.consul_candidates import get_eligible_consul_pairs
from rorapp.helpers.proposal_available import consular_election_proposal_available
from rorapp.models import Game, Senator
from rorapp.models.log import Log


class AutoAppointConsulsEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.CONSULAR_ELECTION
            and not game_state.game.current_proposal
            and consular_election_proposal_available(game_state)
            and not any(
                s.has_status_item(Senator.StatusItem.UNANIMOUSLY_DEFEATED)
                for s in game_state.senators
            )
            and len(
                get_eligible_consul_pairs(
                    game_state.senators, game_state.game.defeated_proposals
                )
            )
            == 1
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        game = Game.objects.get(id=game_id)
        senators = list(Senator.objects.filter(game=game_id))
        pairs = get_eligible_consul_pairs(senators, game.defeated_proposals)
        if len(pairs) != 1:
            return False

        consuls = pairs[0]
        for consul in consuls:
            consul.add_status_item(Senator.StatusItem.INCOMING_CONSUL)
            consul.save()

        Log.create_object(
            game_id,
            f"{consuls[0].display_name} and {consuls[1].display_name} were the only pair of candidates left, so they were automatically appointed Consuls.",
        )

        game.clear_senate_sub_phase_proposals()
        game.save()
        return True
