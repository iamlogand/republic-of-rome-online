from typing import List
from rorapp.classes.concession import Concession
from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.clear_proposal_and_votes import clear_proposal_and_votes
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import Fleet, Game, Legion, Log, Senator


class ProposalRaiseForcesEffect(EffectBase):

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
            and game_state.game.current_proposal.startswith("Raise ")
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        game = Game.objects.get(id=game_id)
        if not game.current_proposal:
            return False

        if game.votes_yea > game.votes_nay:

            # Proposal passed
            Log.create_object(game.id, f"Motion passed: {game.current_proposal}.")
            unit_amounts = game.current_proposal[len("Raise ") :].split(" and ")
            legions_to_raise = 0
            fleets_to_raise = 0
            for amount in unit_amounts:
                (unit_count, unit_type) = amount.split(" ")
                if unit_type.startswith("legion"):
                    legions_to_raise = int(unit_count)
                if unit_type.startswith("fleet"):
                    fleets_to_raise = int(unit_count)

            legions_cost = legions_to_raise * 10
            fleets_cost = fleets_to_raise * 10
            total_cost = legions_cost + fleets_cost
            game.state_treasury -= total_cost

            existing_legions = Legion.objects.filter(game=game)
            unavailable_legion_nums = [legion.number for legion in existing_legions]
            existing_fleets = Fleet.objects.filter(game=game)
            unavailable_fleet_nums = [fleet.number for fleet in existing_fleets]

            new_legions: List[Legion] = []
            new_fleets: List[Fleet] = []
            for num in range(1, 26):
                if legions_to_raise and num not in unavailable_legion_nums:
                    new_legions.append(Legion.objects.create(game=game, number=num))
                    legions_to_raise -= 1
                if fleets_to_raise and num not in unavailable_fleet_nums:
                    new_fleets.append(Fleet.objects.create(game=game, number=num))
                    fleets_to_raise -= 1

            units_text = unit_list_to_string(list(new_legions), list(new_fleets))
            Log.create_object(
                game_id=game.id,
                text=f"The State spent {total_cost}T to raise {units_text}.",
            )

            # Identify senators with Armaments/Ship building
            armaments_senator = ship_building_senator = None
            senators = Senator.objects.filter(game=game)
            for senator in senators:
                if legions_to_raise and senator.has_concession(Concession.ARMAMENTS):
                    armaments_senator = senator
                if fleets_to_raise and senator.has_concession(Concession.SHIP_BUILDING):
                    ship_building_senator = senator
                    
            if armaments_senator or ship_building_senator:
                if armaments_senator:
                    armaments_amount = legions_to_raise * 2
                    armaments_senator.talents += armaments_amount
                if ship_building_senator:
                    ship_building_amount = fleets_to_raise * 3
                    ship_building_senator.talents += ship_building_amount
                    
                # Build Armaments/Ship building log
                if armaments_senator.id == ship_building_senator.id:
                    log_text = (
                        f"{armaments_senator.id} earned"
                        + f" {armaments_amount}T from {Concession.ARMAMENTS.value} and"
                        + f" {ship_building_amount}T from {Concession.SHIP_BUILDING.value}."
                    )
                else:
                    messages = []
                    if armaments_senator:
                        messages.append(
                            f"{armaments_senator.id} earned {armaments_amount}T from {Concession.ARMAMENTS.value}"
                        )
                    if ship_building_senator:
                        messages.append(
                            f"{ship_building_senator.id} earned {ship_building_amount}T from {Concession.SHIP_BUILDING.value}"
                        )
                    log_text = " and ".join(messages) + "."
                Log.create_object(
                    game_id=game.id,
                    text=log_text,
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
