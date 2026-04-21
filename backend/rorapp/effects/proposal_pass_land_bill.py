from collections import defaultdict

from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.clear_proposal_and_votes import clear_proposal_and_votes
from rorapp.helpers.game_data import load_land_bills
from rorapp.helpers.proposal_available import LAND_BILL_EFFECT
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
            Log.create_object(game.id, f"Motion passed: {game.current_proposal}.")

            # Parse sponsor and co-sponsor names
            senators = list(Senator.objects.filter(game=game, alive=True))
            sponsored_by = " sponsored by "
            cosponsor_marker = " and co-sponsored by "
            sponsor_start = game.current_proposal.index(sponsored_by) + len(
                sponsored_by
            )
            sponsor_name_and_more = game.current_proposal[sponsor_start:]
            sponsor = next(
                (
                    s
                    for s in senators
                    if sponsor_name_and_more.startswith(s.display_name)
                ),
                None,
            )
            cosponsor_start = game.current_proposal.index(cosponsor_marker) + len(
                cosponsor_marker
            )
            cosponsor_name = game.current_proposal[cosponsor_start:]
            cosponsor = next(
                (s for s in senators if cosponsor_name.startswith(s.display_name)),
                None,
            )

            if not sponsor or not cosponsor:
                raise ValueError(
                    "Could not parse sponsor or co-sponsor from land bill proposal."
                )

            bill = _LAND_BILLS[bill_type]

            # Apply unrest change
            unrest_change = game.change_unrest(bill["pass_unrest_change"])
            Log.create_object(
                game_id, f"The land bill lowered unrest by {abs(unrest_change)}."
            )

            # Apply sponsor and co-sponsor popularity
            sponsor_pop_change = sponsor.change_popularity(
                bill["pass_sponsor_popularity"]
            )
            sponsor.save()
            cosponsor_pop_change = cosponsor.change_popularity(
                bill["pass_cosponsor_popularity"]
            )
            cosponsor.save()
            Log.create_object(
                game_id,
                f"{sponsor.display_name} gained {sponsor_pop_change} popularity"
                f" and {cosponsor.display_name} gained {cosponsor_pop_change} popularity"
                f" for sponsoring the land bill.",
            )

            # Apply voted-against popularity penalty — one log per faction
            nay_senators = [
                s
                for s in Senator.objects.filter(game=game, alive=True).select_related(
                    "faction"
                )
                if s.has_status_item(Senator.StatusItem.VOTED_NAY)
            ]
            by_faction = defaultdict(list)
            against_pop = bill["pass_against_popularity"]
            for senator in nay_senators:
                senator.change_popularity(against_pop)
                senator.save()
                by_faction[senator.faction].append(senator)
            for faction, senators in by_faction.items():
                names = ", ".join(s.display_name for s in senators[:-1])
                if names:
                    names += f" and {senators[-1].display_name}"
                else:
                    names = senators[-1].display_name
                faction_name = faction.display_name if faction else "no faction"
                Log.create_object(
                    game_id,
                    f"{names} of {faction_name} each lost {abs(against_pop)} popularity for voting against the land bill.",
                )

            # Place land bill marker
            game.add_effect(LAND_BILL_EFFECT[bill_type])

        else:
            game.add_defeated_proposal(game.current_proposal)
            Log.create_object(game_id, f"Motion defeated: {game.current_proposal}.")
            handle_unanimous_defeat(game_id)

        # Record so the same type cannot be proposed again this turn (pass or fail)
        game.add_unavailable_proposal(f"pass type {bill_type} land bill")

        game.save()
        clear_proposal_and_votes(game_id)
        return True
