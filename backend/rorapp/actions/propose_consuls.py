from typing import Dict, List, Optional, Tuple
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Senator, Log


class ProposeConsulsAction(ActionBase):
    NAME = "Propose consuls"
    POSITION = 0

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
            candidate_senators = sorted(
                [s for s in snapshot.senators if s.faction and s.alive],
                key=lambda s: s.name,
            )

            defeated_pairs = []
            for proposal in snapshot.game.defeated_proposals:
                if proposal.startswith("Elect consuls "):
                    candidate_names = proposal[len("Elect consuls ") :].split(" and ")
                    candidates = sorted(
                        [
                            s
                            for s in candidate_senators
                            if s.display_name in candidate_names
                        ],
                        key=lambda s: s.name,
                    )
                    defeated_pairs.append(candidates)

            candidate_senators_set = set()
            for senator1 in candidate_senators:
                for senator2 in candidate_senators:
                    candidates = sorted(
                        [senator1, senator2],
                        key=lambda s: s.name,
                    )
                    if (
                        candidates not in defeated_pairs
                        and candidates[0] != candidates[1]
                    ):
                        candidate_senators_set.add(candidates[0])
                        candidate_senators_set.add(candidates[1])

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
        current_proposal = f"Elect consuls {candidates[0].display_name} and {candidates[1].display_name}"
        if current_proposal in game.defeated_proposals:
            return ExecutionResult(False, "This proposal was previously rejected")

        # Set current proposal
        game.current_proposal = f"Elect consuls {candidates[0].display_name} and {candidates[1].display_name}"
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
