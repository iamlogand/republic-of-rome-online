from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.governor_election import (
    assign_governor,
    governor_election_inputs,
    is_exclusive_last_remaining_candidate,
    next_senate_sub_phase_after_governor_election,
    remaining_candidates_for_province,
)
from rorapp.models import Game, Log


class AutoAppointGovernorEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        if not (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.GOVERNOR_ELECTION
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

        vacant, candidates, defeated = governor_election_inputs(
            game_state.game.id,
            game_state.senators,
            list(game_state.game.defeated_proposals),
        )
        return any(
            is_exclusive_last_remaining_candidate(
                province, vacant, candidates, defeated
            )
            for province in vacant
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        vacant, candidates, defeated = governor_election_inputs(game_id)
        appointed = False
        used_ids: set[int] = set()

        for province in vacant:
            if not is_exclusive_last_remaining_candidate(
                province, vacant, candidates, defeated
            ):
                continue
            remaining = [
                senator
                for senator in remaining_candidates_for_province(
                    province, candidates, defeated
                )
                if senator.id not in used_ids
            ]
            if len(remaining) != 1:
                continue
            senator = remaining[0]
            assign_governor(province, senator)
            used_ids.add(senator.id)
            appointed = True
            Log.create_object(
                game_id,
                f"{senator.display_name}, the only remaining eligible candidate, "
                f"was automatically appointed governor of {province.name} and left Rome.",
            )

        if not appointed:
            return False

        next_sub_phase = next_senate_sub_phase_after_governor_election(game_id)
        if next_sub_phase != Game.SubPhase.GOVERNOR_ELECTION:
            game.clear_senate_sub_phase_proposals()
        game.sub_phase = next_sub_phase
        game.save()
        return True
