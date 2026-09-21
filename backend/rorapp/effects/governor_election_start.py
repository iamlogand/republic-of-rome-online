from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.governor_election import governor_candidates, open_governorships
from rorapp.models import Game


class GovernorElectionStartEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        # Elections for all open governorships are conducted immediately after
        # prosecutions and before conducting other business (1.09.5)
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.OTHER_BUSINESS
            and not game_state.game.current_proposal
            and not any(
                f.has_status_item(FactionStatusItem.CALLED_TO_VOTE)
                for f in game_state.factions
            )
            and bool(
                open_governorships(
                    game_state.provinces,
                    governor_candidates(game_state.senators),
                    game_state.game.defeated_proposals,
                )
            )
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        game.sub_phase = Game.SubPhase.GOVERNOR_ELECTION
        game.save()
        return True
