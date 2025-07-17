import re
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.clear_proposal_and_votes import clear_proposal_and_votes
from rorapp.helpers.force_lists import string_to_force_list
from rorapp.models import Faction, Fleet, Game, Legion, Senator
from rorapp.models.log import Log


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
            Log.create_object(game.id, f"Motion passed: {game.current_proposal}")
            commander_name = game.current_proposal[len("Deploy ") :].split(" with")[0]
            senators = Senator.objects.filter(game=game, alive=True)
            commander = next(
                (s for s in senators if s.display_name == commander_name), None
            )
            if commander is None:
                raise ValueError("Invalid commander")

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
                string_to_force_list(legions_string, game_id, Legion)
                if legions_string
                else []
            )
            fleets = (
                string_to_force_list(fleets_string, game_id, Fleet)
                if fleets_string
                else []
            )

            if len(legions) != legion_count:
                raise ValueError("Legion count didn't match legion names")
            if len(fleets) != fleet_count:
                raise ValueError("Fleet count didn't match fleet names")

        else:
            # Proposal failed
            game.defeated_proposals.append(game.current_proposal)
            game.save()

        clear_proposal_and_votes(game_id)

        return True
