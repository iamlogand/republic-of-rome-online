from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.clear_proposal_state import clear_proposal_state
from rorapp.helpers.governor_election import (
    assign_governor,
    is_governor_proposal,
    next_senate_sub_phase_after_governor_election,
    parse_governor_proposals,
)
from rorapp.helpers.unanimous_defeat import handle_unanimous_defeat
from rorapp.models import Game, Log, Province, Senator


class ElectGovernorEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        if game_state.game.phase != Game.Phase.SENATE:
            return False
        if game_state.game.sub_phase != Game.SubPhase.GOVERNOR_ELECTION:
            return False
        proposal = game_state.game.current_proposal
        if proposal is None or proposal == "":
            return False
        if not all(
            f.has_status_item(FactionStatusItem.DONE) for f in game_state.factions
        ):
            return False
        return is_governor_proposal(proposal)

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        if not game.current_proposal:
            return False

        pairings = parse_governor_proposals(game.current_proposal)
        if not pairings:
            return False

        if game.votes_yea > game.votes_nay:
            Log.create_object(game.id, f"Motion passed: {game.current_proposal}.")

            senators = list(Senator.objects.filter(game=game_id, alive=True))
            for province_name, senator_name in pairings:
                senator = next(
                    (s for s in senators if s.display_name == senator_name), None
                )
                province = Province.objects.filter(
                    game_id=game_id, name=province_name, governor__isnull=True
                ).first()

                if senator and province:
                    assign_governor(province, senator)
                    Log.create_object(
                        game.id,
                        f"{senator.display_name} was elected governor of {province.name} and left Rome.",
                    )
                else:
                    Log.create_object(
                        game.id,
                        f"{senator_name} could not take up the governorship of {province_name}.",
                    )

            next_sub_phase = next_senate_sub_phase_after_governor_election(game_id)
            if next_sub_phase != Game.SubPhase.GOVERNOR_ELECTION:
                game.clear_senate_sub_phase_proposals()
            game.sub_phase = next_sub_phase
            game.save()
        else:
            game.add_defeated_proposal(game.current_proposal)
            Log.create_object(
                game_id,
                f"Motion defeated: {game.current_proposal}.",
            )
            game.save()
            handle_unanimous_defeat(game_id)

        clear_proposal_state(game_id)
        return True