from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.clear_proposal_state import clear_proposal_state
from rorapp.helpers.game_data import load_land_bills
from rorapp.helpers.motion_result import log_motion_result
from rorapp.helpers.proposal_available import LAND_BILL_EFFECT
from rorapp.helpers.proposal_parsing import extract_land_bill_sponsors
from rorapp.helpers.unanimous_defeat import handle_unanimous_defeat
from rorapp.models import Game, Log, Senator

_LAND_BILLS = load_land_bills()


class ProposalLandBillEffect(EffectBase):

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
            and game_state.game.current_proposal.startswith("Pass type ")
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        if not game.current_proposal:
            return False

        # Parse bill type: "Pass type {I|II|III} land bill sponsored by ..."
        after_type = game.current_proposal[len("Pass type ") :]
        bill_type = after_type.split(" ")[0]  # "I", "II", or "III"

        if game.votes_yea > game.votes_nay:
            log_motion_result(game, passed=True)

            senators = list(Senator.objects.filter(game=game, alive=True))
            sponsor, cosponsor = extract_land_bill_sponsors(
                game.current_proposal, senators
            )

            bill = _LAND_BILLS[bill_type]

            # Apply unrest change
            unrest_change = game.change_unrest(bill["pass_unrest_change"])
            if unrest_change != 0:
                Log.create_object(
                    game_id,
                    f"Passage of the land bill lowered unrest by {abs(unrest_change)}.",
                )

            # Apply sponsor and co-sponsor popularity
            popularity_changes = []
            for senator, popularity in (
                (sponsor, bill["pass_sponsor_popularity"]),
                (cosponsor, bill["pass_cosponsor_popularity"]),
            ):
                if senator is not None:
                    pop_change = senator.change_popularity(popularity)
                    senator.save()
                    popularity_changes.append(
                        f"{senator.display_name} gained {pop_change} popularity"
                    )
            if popularity_changes:
                Log.create_object(
                    game_id,
                    " and ".join(popularity_changes) + " for sponsoring the land bill.",
                )

            # Place land bill marker
            game.add_effect(LAND_BILL_EFFECT[bill_type])

        else:
            game.add_defeated_proposal(game.current_proposal)
            log_motion_result(game, passed=False)
            handle_unanimous_defeat(game_id)

        # Record so the same type cannot be proposed again this turn (pass or fail)
        game.add_unavailable_proposal(f"pass type {bill_type} land bill")

        game.save()
        clear_proposal_state(game_id)
        return True
