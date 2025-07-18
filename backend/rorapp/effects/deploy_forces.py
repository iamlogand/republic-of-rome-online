import re
from typing import cast, List
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.clear_proposal_and_votes import clear_proposal_and_votes
from rorapp.helpers.unit_lists import string_to_unit_list
from rorapp.models import Campaign, Faction, Fleet, Game, Legion, Log, Senator, War


class DeployForcesEffect(EffectBase):

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
            and game_state.game.current_proposal.startswith("Deploy ")
        )

    def execute(self, game_id: int) -> bool:

        game = Game.objects.get(id=game_id)
        if not game.current_proposal:
            return False

        if game.votes_yea > game.votes_nay:

            # Proposal passed
            Log.create_object(game.id, f"Motion passed: {game.current_proposal}.")

            commander_name = game.current_proposal[len("Deploy ") :].split(" with")[0]
            senators = Senator.objects.filter(game=game, alive=True)
            commander = next(
                (s for s in senators if s.display_name == commander_name), None
            )
            if commander is None or commander.faction is None:
                raise ValueError("Invalid commander")

            war_name = game.current_proposal.split("to the ")[1]
            wars = War.objects.filter(game=game)
            war = next((w for w in wars if w.name == war_name), None)
            if war is None:
                raise ValueError("Invalid war")

            legion_pattern = r"(?P<legion_count>\d+)\s+legions\s*\((?P<legions>[^)]+)\)"
            fleet_pattern = r"(?P<fleet_count>\d+)\s+fleets\s*\((?P<fleets>[^)]+)\)"

            legion_match = re.search(legion_pattern, game.current_proposal)
            fleet_match = re.search(fleet_pattern, game.current_proposal)

            if not legion_match and not fleet_match:
                raise ValueError("Could not parse legions or fleets from proposal")

            legion_count = (
                int(legion_match.group("legion_count")) if legion_match else 0
            )
            legions_string = legion_match.group("legions") if legion_match else ""
            fleet_count = int(fleet_match.group("fleet_count")) if fleet_match else 0
            fleets_string = fleet_match.group("fleets") if fleet_match else ""

            legions = (
                cast(List[Legion], string_to_unit_list(legions_string, game_id, Legion))
                if legions_string
                else []
            )
            fleets = (
                cast(List[Fleet], string_to_unit_list(fleets_string, game_id, Fleet))
                if fleets_string
                else []
            )

            if len(legions) != legion_count:
                raise ValueError("Legion count didn't match legion names")
            if len(fleets) != fleet_count:
                raise ValueError("Fleet count didn't match fleet names")

            campaign = Campaign.objects.create(game=game, commander=commander, war=war)
            for legion in legions:
                legion.campaign = campaign
            Legion.objects.bulk_update(legions, ["campaign"])
            for fleet in fleets:
                fleet.campaign = campaign
            Fleet.objects.bulk_update(fleets, ["campaign"])

            commander.location = war.location
            commander.save()

            Log.create_object(
                game_id,
                f"{commander.display_name} departed Rome to the {war.name} in {war.location}.",
            )

            # Activate the war if it's not already active
            if war.status != War.Status.ACTIVE:
                original_status = war.status
                war.status = War.Status.ACTIVE
                war.save()
                Log.create_object(
                    game_id,
                    f"Rome's actions have escalated the {war.name} from {original_status.lower()} to active.",
                )

            # Close the senate if the commander was presiding magistrate
            if commander.has_title(Senator.Title.PRESIDING_MAGISTRATE):

                for senator in Senator.objects.filter(game=game):
                    if senator.has_title(Senator.Title.PRESIDING_MAGISTRATE):
                        senator.remove_title(Senator.Title.PRESIDING_MAGISTRATE)
                        senator.save()

                Log.create_object(
                    game_id,
                    f"Following the departure of {commander.display_name}, the presiding magistrate, the Senate meeting has closed.",
                )

                game.phase = Game.Phase.COMBAT
                game.sub_phase = Game.SubPhase.START

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
