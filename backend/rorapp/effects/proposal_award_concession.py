from rorapp.classes.concession import Concession
from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.clear_proposal_and_votes import clear_proposal_and_votes
from rorapp.models import Game, Log, Senator


class ProposalAwardConcessionEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.OTHER_BUSINESS
            and not (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
            and all(f.has_status_item(FactionStatusItem.DONE) for f in game_state.factions)
            and game_state.game.current_proposal.startswith("Award the ")
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        game = Game.objects.get(id=game_id)
        if not game.current_proposal:
            return False

        if game.votes_yea > game.votes_nay:

            # Proposal passed
            Log.create_object(game.id, f"Motion passed: {game.current_proposal}.")

            # Parse proposal: "Award the {concession} concession to {senator_name}"
            after_award = game.current_proposal[len("Award the "):]
            concession_idx = after_award.index(" concession to ")
            concession_value = after_award[:concession_idx]
            senator_name = after_award[concession_idx + len(" concession to "):]

            concession = Concession(concession_value)

            senators = Senator.objects.filter(game=game, alive=True)
            senator = next(
                (s for s in senators if s.display_name == senator_name),
                None,
            )
            if not senator:
                raise ValueError(f"Senator not found: {senator_name}")

            # Move concession from game to senator
            game.remove_concession(concession)
            senator.add_concession(concession)
            senator.save()

            Log.create_object(
                game_id,
                f"{senator.display_name} received the {concession.value} concession.",
            )

        else:

            # Proposal failed
            game.defeated_proposals.append(game.current_proposal)
            Log.create_object(
                game_id,
                f"Motion defeated: {game.current_proposal}.",
            )

        game.save()
        clear_proposal_and_votes(game_id)
        return True
