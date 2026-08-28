from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.governor_election import has_governor_election_work_remaining
from rorapp.models import Game, Log


class AutoCloseGovernorElectionsEffect(EffectBase):

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
        return not has_governor_election_work_remaining(
            game_state.game.id,
            game_state.senators,
            list(game_state.game.defeated_proposals),
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        game.clear_senate_sub_phase_proposals()
        game.sub_phase = Game.SubPhase.OTHER_BUSINESS
        game.save()
        Log.create_object(
            game_id,
            "With no further governorship elections possible, the Senate moved to other business.",
        )
        return True
