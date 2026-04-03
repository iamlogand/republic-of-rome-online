from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.clear_proposal_and_votes import clear_proposal_and_votes
from rorapp.helpers.unanimous_defeat import handle_unanimous_defeat
from rorapp.models import Game, Senator
from rorapp.models.log import Log


class ElectCensorEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.CENSOR_ELECTION
            and not (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
            and all(
                f.has_status_item(FactionStatusItem.DONE) for f in game_state.factions
            )
            and game_state.game.current_proposal.startswith("Elect Censor ")
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        game = Game.objects.get(id=game_id)
        if not game.current_proposal:
            return False

        senator_name = game.current_proposal[len("Elect Censor ") :]
        senators = Senator.objects.filter(game=game_id, alive=True)
        censor = next((s for s in senators if s.display_name == senator_name), None)

        if game.votes_yea > game.votes_nay:

            # Proposal passed - elect the censor
            Log.create_object(game.id, f"Motion passed: {game.current_proposal}.")

            if censor:
                # Remove PM and Censor title from whoever currently holds them
                for senator in senators:
                    changed = False
                    if senator.has_title(Senator.Title.PRESIDING_MAGISTRATE):
                        senator.remove_title(Senator.Title.PRESIDING_MAGISTRATE)
                        changed = True
                    if senator.has_title(Senator.Title.CENSOR):
                        senator.remove_title(Senator.Title.CENSOR)
                        changed = True
                    if changed:
                        senator.save()

                censor.add_title(Senator.Title.CENSOR)
                censor.add_title(Senator.Title.PRESIDING_MAGISTRATE)
                censor.influence += 5
                censor.save()

                Log.create_object(
                    game_id=game.id,
                    text=f"{censor.display_name} was elected Censor. He gained 5 influence.",
                )

            game.clear_defeated_proposals()
            clear_proposal_and_votes(game_id)
            game = Game.objects.get(id=game_id)
            game.sub_phase = Game.SubPhase.PROSECUTION
            game.prosecutions_remaining = 2
            game.save()

        else:

            # Proposal failed
            if game.current_proposal:
                game.add_defeated_proposal(game.current_proposal)
            Log.create_object(
                game_id,
                f"Motion defeated: {game.current_proposal}.",
            )
            game.save()
            handle_unanimous_defeat(game_id)
            clear_proposal_and_votes(game_id)

        return True
