from typing import Dict, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Senator, Legion, Log


class ProposeRaisingForcesAction(ActionBase):
    NAME = "Propose raising forces"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.OTHER_BUSINESS
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
            and game_state.game.state_treasury >= 10
            and len(game_state.legions) + len(game_state.fleets) < 50
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> Optional[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if faction:
            state_treasury = snapshot.game.state_treasury
            max_recruitment = state_treasury // 10
            max_new_legions = 25 - len(snapshot.legions)
            max_new_fleets = 25 - len(snapshot.fleets)

            return AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                name=self.NAME,
                position=self.POSITION,
                schema=[
                    {
                        "type": "number",
                        "name": "Legions",
                        "min": [0],
                        "max": [
                            max_recruitment,
                            max_new_legions,
                            f"{max_recruitment} - signal:fleets",
                        ],
                        "signals": {
                            "legions": "VALUE",
                        },
                    },
                    {
                        "type": "number",
                        "name": "Fleets",
                        "min": [0],
                        "max": [
                            max_recruitment,
                            max_new_fleets,
                            f"{max_recruitment} - signal:legions",
                        ],
                        "signals": {
                            "fleets": "VALUE",
                        },
                    },
                ],
            )
        return None

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, str],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:

        game = Game.objects.get(id=game_id)
        faction = Faction.objects.get(game=game_id, id=faction_id)

        new_legions = int(selection["Legions"])
        new_fleets = int(selection["Fleets"])

        # Validate total cost
        recruitment_cost = (new_legions + new_fleets) * 10
        if recruitment_cost > game.state_treasury:
            return ExecutionResult(
                False, "The State cannot afford to recruit this many forces"
            )

        # Determine proposal
        if new_legions > 0:
            if new_fleets > 0:
                proposal = f"Raise {new_legions} legions and {new_fleets} fleets"
            else:
                proposal = f"Raise {new_legions} legion{'s' if new_legions > 1 else ''}"
        else:
            if new_fleets > 0:
                proposal = f"Raise {new_fleets} fleet{'s' if new_fleets > 1 else ''}"
            else:
                return ExecutionResult(
                    False, "Proposal must include at least 1 legion or fleet"
                )

        # Validate proposal
        if proposal in game.defeated_proposals:
            return ExecutionResult(False, "This proposal was previously rejected.")

        # Set current proposal
        game.current_proposal = proposal
        game.save()

        # Create log
        presiding_magistrate = [
            s
            for s in faction.senators.all()
            if s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
        ][0]
        Log.create_object(
            game_id,
            f"{presiding_magistrate.display_name} proposed the motion: {game.current_proposal}.",
        )

        return ExecutionResult(True)
