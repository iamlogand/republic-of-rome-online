from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Senator


class ProposalFailEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and not (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
            and all(
                f.has_status_item(Faction.StatusItem.DONE) for f in game_state.factions
            )
            and game_state.game.votes_nay >= game_state.game.votes_yea
        )

    def execute(self, game_id: int) -> bool:

        game = Game.objects.get(id=game_id)
        game.defeated_proposals.append(game.current_proposal)

        # Clear current proposal and votes
        game.current_proposal = None
        game.votes_nay = 0
        game.votes_yea = 0
        game.save()

        factions = Faction.objects.filter(game=game_id)
        for faction in factions:
            faction.remove_status_item(Faction.StatusItem.DONE)

        senators = Senator.objects.filter(game=game_id)
        for senator in senators:
            senator.remove_status_item(Senator.StatusItem.VOTED_NAY)
            senator.remove_status_item(Senator.StatusItem.VOTED_YEA)
            senator.remove_status_item(Senator.StatusItem.ABSTAINED)

        return True
