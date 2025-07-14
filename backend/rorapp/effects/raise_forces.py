from typing import List
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.clear_proposal_and_votes import clear_proposal_and_votes
from rorapp.models import Faction, Fleet, Game, Legion, Log


class RaiseForcesEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.OTHER_BUSINESS
            and not (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
            and all(
                f.has_status_item(Faction.StatusItem.DONE) for f in game_state.factions
            )
            and game_state.game.current_proposal.startswith("Raise ")
        )

    def execute(self, game_id: int) -> bool:

        game = Game.objects.get(id=game_id)
        if not game.current_proposal:
            return False

        if game.votes_yea > game.votes_nay:

            # Proposal passed
            Log.create_object(game.id, f"Motion passed: {game.current_proposal}.")
            force_amounts = game.current_proposal[len("Raise ") :].split(" and ")
            legions_to_raise = 0
            fleets_to_raise = 0
            for amount in force_amounts:
                (force_count, force_type) = amount.split(" ")
                if force_type.startswith("legion"):
                    legions_to_raise = int(force_count)
                if force_type.startswith("fleet"):
                    fleets_to_raise = int(force_count)

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
                if legions_to_raise > 0 and num not in unavailable_legion_nums:
                    new_legions.append(Legion.objects.create(game=game, number=num))
                    legions_to_raise -= 1
                if fleets_to_raise > 0 and num not in unavailable_fleet_nums:
                    new_fleets.append(Fleet.objects.create(game=game, number=num))
                    fleets_to_raise -= 1

            if len(new_legions) > 0:
                legion_log_text = f"The State spent {legions_cost}T to raise {len(new_legions)} legion{'s' if len(new_legions) > 1 else ''}: "
                for i in range(len(new_legions)):
                    legion_log_text += new_legions[i].name
                    if i < len(new_legions) - 2:
                        legion_log_text += ", "
                    elif i == len(new_legions) - 2:
                        legion_log_text += " and "
                legion_log_text += "."
                Log.create_object(game_id=game.id, text=legion_log_text)

            if len(new_fleets) > 0:
                fleet_log_text = f"The State spent {fleets_cost}T to raise {len(new_fleets)} fleet{'s' if len(new_fleets) > 1 else ''}: "
                for i in range(len(new_fleets)):
                    fleet_log_text += new_fleets[i].name
                    if i < len(new_fleets) - 2:
                        fleet_log_text += ", "
                    elif i == len(new_fleets) - 2:
                        fleet_log_text += " and "
                fleet_log_text += "."
                Log.create_object(game_id=game.id, text=fleet_log_text)

        else:

            # Proposal failed
            game.defeated_proposals.append(game.current_proposal)

        game.save()

        clear_proposal_and_votes(game_id)

        return True
