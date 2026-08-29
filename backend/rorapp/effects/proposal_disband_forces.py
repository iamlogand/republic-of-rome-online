from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.clear_proposal_state import clear_proposal_state
from rorapp.helpers.motion_result import log_motion_result
from rorapp.helpers.unanimous_defeat import handle_unanimous_defeat
from rorapp.helpers.unit_lists import string_to_unit_lists, unit_list_to_string
from rorapp.models import Fleet, Game, Legion, Log


class ProposalDisbandForcesEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.OTHER_BUSINESS
            and not (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
            and all(
                f.has_status_item(FactionStatusItem.DONE) for f in game_state.factions
            )
            and game_state.game.current_proposal.startswith("Disband ")
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        game = Game.objects.get(id=game_id)
        if not game.current_proposal:
            return False

        if game.votes_yea > game.votes_nay:

            # Proposal passed
            log_motion_result(game, passed=True)

            legions, fleets = string_to_unit_lists(game.current_proposal, game_id)

            # Disbanded units stay out of the force pool for the rest of the
            # senate phase, so they can't be rebuilt this turn (1.09.63)
            for legion in legions:
                game.add_disbanded_legion_number(legion.number)
            for fleet in fleets:
                game.add_disbanded_fleet_number(fleet.number)

            units_text = unit_list_to_string(legions, fleets)
            Legion.objects.filter(id__in=[l.id for l in legions]).delete()
            Fleet.objects.filter(id__in=[f.id for f in fleets]).delete()

            Log.create_object(
                game_id=game.id,
                text=f"The State disbanded {units_text}.",
            )

        else:

            # Proposal failed
            game.add_defeated_proposal(game.current_proposal)
            log_motion_result(game, passed=False)
            handle_unanimous_defeat(game_id)

        game.save()
        clear_proposal_state(game_id)
        return True
