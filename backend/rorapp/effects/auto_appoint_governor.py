from django.conf import settings

from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.elect_governor import assign_governor
from rorapp.helpers.governor_election import (
    governor_candidates,
    is_sole_candidate,
    remaining_candidates,
    vacant_provinces,
)
from rorapp.models import Game, Log, Province, Senator


class AutoAppointGovernorEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        if not settings.FEATURE_FLAGS.get("governors"):
            return False
        if not (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.GOVERNOR_ELECTION
            and not game_state.game.current_proposal
            and not any(
                f.has_status_item(FactionStatusItem.CALLED_TO_VOTE)
                for f in game_state.factions
            )
        ):
            return False
        vacant = vacant_provinces(game_state.provinces)
        candidates = governor_candidates(game_state.senators)
        return any(
            is_sole_candidate(
                province, vacant, candidates, game_state.game.defeated_proposals
            )
            for province in vacant
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        vacant = vacant_provinces(list(Province.objects.filter(game_id=game_id)))
        candidates = governor_candidates(
            list(Senator.objects.filter(game_id=game_id, alive=True))
        )

        province = next(
            province
            for province in vacant
            if is_sole_candidate(province, vacant, candidates, game.defeated_proposals)
        )
        senator = remaining_candidates(province, candidates, game.defeated_proposals)[0]
        assign_governor(province, senator)
        Log.create_object(
            game_id,
            f"{senator.display_name} was the only remaining candidate, "
            f"so he was appointed governor of {province.name} and left Rome.",
        )
        return True
