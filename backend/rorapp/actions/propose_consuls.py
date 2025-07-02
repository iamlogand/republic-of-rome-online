from typing import Dict, List, Optional, Tuple
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Senator, Log


class ProposeConsulsAction(ActionBase):
    NAME = "Propose consuls"
    POSITION = 0

    proposal_prefix = "Elect consuls "

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.CONSULAR_ELECTION
            and (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
            and any(
                s
                for s in game_state.senators
                if s.faction
                and s.faction.id == faction.id
                and s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
            )
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> Optional[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if faction:
            candidate_pairs = get_candidate_pairs(
                snapshot.senators, snapshot.game.defeated_proposals
            )

            candidate_senators_set = set()
            for pair in candidate_pairs:
                for senator in pair:
                    candidate_senators_set.add(senator)

            candidate_senators = sorted(
                candidate_senators_set,
                key=lambda s: s.name,
            )

            return AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                name=self.NAME,
                position=self.POSITION,
                schema=[
                    {
                        "type": "select",
                        "name": "Consul 1",
                        "options": [
                            {
                                "value": s.id,
                                "object_class": "senator",
                                "id": s.id,
                                "signals": {
                                    "selected_consul_1": s.id,
                                },
                            }
                            for s in candidate_senators
                        ],
                    },
                    {
                        "type": "select",
                        "name": "Consul 2",
                        "options": [
                            {
                                "value": s.id,
                                "object_class": "senator",
                                "id": s.id,
                                "signals": {
                                    "selected_consul_2": s.id,
                                },
                                "conditions": [
                                    {
                                        "value1": "signal:selected_consul_1",
                                        "operation": "!=",
                                        "value2": s.id,
                                    },
                                ],
                            }
                            for s in candidate_senators
                        ],
                    },
                ],
            )
        return None

    def execute(
        self, game_id: int, faction_id: int, selection: Dict[str, str]
    ) -> ExecutionResult:

        game = Game.objects.get(id=game_id)
        faction = Faction.objects.get(game=game_id, id=faction_id)
        if not faction:
            return ExecutionResult(False)

        # Identify candidates
        senators = Senator.objects.filter(game=game_id)
        candidate_1_id = selection["Consul 1"]
        candidate_1 = senators.get(id=candidate_1_id)
        candidate_2_id = selection["Consul 2"]
        candidate_2 = senators.get(id=candidate_2_id)

        candidates = sorted([candidate_1, candidate_2], key=lambda s: s.name)

        # Check if these candidates were previously defeated
        candidate_pairs = get_candidate_pairs(list(senators), game.defeated_proposals)
        pair_is_valid = False
        for pair in candidate_pairs:
            if pair[0].id == candidate_1.id and pair[1].id == candidate_2.id:
                pair_is_valid = True
                break
        if not pair_is_valid:
            return ExecutionResult(False, "This proposal was previously rejected")

        # Set current proposal
        game.current_proposal = f"{self.proposal_prefix}{candidates[0].display_name} and {candidates[1].display_name}"
        game.save()

        # Create log
        presiding_magistrate = [
            s
            for s in senators.filter(faction=faction_id)
            if s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
        ][0]
        Log.create_object(
            game_id,
            f"{presiding_magistrate.display_name} of {faction.display_name} proposed the election of {candidates[0].display_name} and {candidates[1].display_name} as consuls.",
        )

        return ExecutionResult(True)


def get_candidate_pairs(
    senators: List[Senator], defeated_proposals: List[str]
) -> List[List[Senator]]:
    """Returns a list of pairs and a list of all senators"""
    candidate_senators = sorted(
        [s for s in senators if s.faction and s.alive],
        key=lambda s: s.name,
    )

    defeated_pairs = []
    for proposal in defeated_proposals:
        if proposal.startswith(ProposeConsulsAction.proposal_prefix):
            candidate_names = proposal[
                len(ProposeConsulsAction.proposal_prefix) :
            ].split(" and ")
            candidates = sorted(
                [s for s in candidate_senators if s.display_name in candidate_names],
                key=lambda s: s.name,
            )
            defeated_pairs.append(candidates)

    valid_candidate_pairs = []
    for senator1 in candidate_senators:
        for senator2 in candidate_senators:
            candidates = sorted(
                [senator1, senator2],
                key=lambda s: s.name,
            )
            if (
                candidates not in defeated_pairs
                and candidates not in valid_candidate_pairs
                and candidates[0] != candidates[1]
            ):
                valid_candidate_pairs.append(candidates)

    return valid_candidate_pairs
