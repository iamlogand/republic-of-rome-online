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


class ProposalLandBillRepealEffect(EffectBase):

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
            and game_state.game.current_proposal.startswith("Repeal type ")
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        if not game.current_proposal:
            return False

        # Parse bill type: "Repeal type {II|III} land bill sponsored by ..."
        after_type = game.current_proposal[len("Repeal type ") :]
        bill_type = after_type.split(" ")[0]  # "II" or "III"

        if game.votes_yea > game.votes_nay:
            Log.create_object(game.id, f"Motion passed: {game.current_proposal}.")

            # Parse sponsor name
            sponsored_by = " sponsored by "
            sponsor_start = game.current_proposal.index(sponsored_by) + len(
                sponsored_by
            )
            sponsor_name = game.current_proposal[sponsor_start:]
            senators = list(Senator.objects.filter(game=game, alive=True))
            sponsor = next(
                (s for s in senators if sponsor_name.startswith(s.display_name)),
                None,
            )
            if not sponsor:
                raise ValueError(
                    "Could not parse sponsor from land bill repeal proposal."
                )

            bill = _LAND_BILLS[bill_type]

            # Apply unrest change
            unrest_change = game.change_unrest(bill["repeal_unrest_change"])
            Log.create_object(game_id, f"Repeal of the land bill increased unrest by {unrest_change}.")

            # Apply sponsor popularity loss
            sponsor_pop_loss = bill["repeal_sponsor_popularity_loss"]
            sponsor_pop_change = sponsor.change_popularity(-sponsor_pop_loss)
            sponsor.save()
            if sponsor_pop_change != 0:
                Log.create_object(
                    game_id,
                    f"{sponsor.display_name} lost {abs(sponsor_pop_change)} popularity for sponsoring the land bill repeal.",
                )

            # Apply voted-for popularity penalty to all senators who voted yea
            yea_senators = [
                s
                for s in Senator.objects.filter(game=game, alive=True).select_related(
                    "faction"
                )
                if s.has_status_item(Senator.StatusItem.VOTED_YEA)
            ]
            by_faction = defaultdict(list)

            yea_pop_loss = bill["repeal_voting_for_popularity_loss"]
            for senator in yea_senators:
                senator.change_popularity(yea_pop_loss)
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
                    f"{names} of {faction_name} each lost {abs(yea_pop_loss)} popularity for voting to repeal the land bill.",
                )

            game.decrement_effect(LAND_BILL_EFFECT[bill_type])

        else:
            game.add_defeated_proposal(game.current_proposal)
            Log.create_object(game_id, f"Motion defeated: {game.current_proposal}.")
            handle_unanimous_defeat(game_id)

        # Record so a second repeal cannot be attempted this turn
        game.add_unavailable_proposal(f"repeal type {bill_type} land bill")

        game.save()
        clear_proposal_and_votes(game_id)
        return True
