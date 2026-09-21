from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.clear_proposal_state import clear_proposal_state
from rorapp.helpers.motion_result import log_motion_result
from rorapp.helpers.proposal_available import REJECT_RHODIAN_ALLIANCE_PROPOSAL
from rorapp.helpers.rhodian_alliance import end_rhodian_alliance
from rorapp.helpers.unanimous_defeat import handle_unanimous_defeat
from rorapp.models import Game


class ProposalRejectRhodianAllianceEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.OTHER_BUSINESS
            and game_state.game.current_proposal == REJECT_RHODIAN_ALLIANCE_PROPOSAL
            and all(
                f.has_status_item(FactionStatusItem.DONE) for f in game_state.factions
            )
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)

        if game.votes_yea > game.votes_nay:
            log_motion_result(game, passed=True)
            end_rhodian_alliance(game)
        else:
            game.add_defeated_proposal(REJECT_RHODIAN_ALLIANCE_PROPOSAL)
            log_motion_result(game, passed=False)
            handle_unanimous_defeat(game_id)

        game.save()
        clear_proposal_state(game_id)
        return True
