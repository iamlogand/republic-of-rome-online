from typing import Dict, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import (
    AvailableAction,
    Campaign,
    Faction,
    Fleet,
    Game,
    Legion,
    Log,
    Senator,
    War,
)
from rorapp.helpers.unit_lists import unit_list_to_string


class ProposeRecallingForcesAction(ActionBase):
    NAME = "Propose recalling forces"
    POSITION = 2

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
        ):
            deployed_legions = [
                l for l in game_state.legions if l.campaign_id is not None
            ]
            deployed_fleets = [
                f for f in game_state.fleets if f.campaign_id is not None
            ]
            campaign__commander_ids = [c.commander_id for c in game_state.campaigns]
            deployed_commanders = [
                s for s in game_state.senators if s in campaign__commander_ids
            ]
            if (
                len(deployed_legions) + len(deployed_fleets) + len(deployed_commanders)
                > 0
            ):
                return faction

        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> Optional[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if faction:
            deployed_legions = sorted(
                [l for l in snapshot.legions if l.campaign_id is not None],
                key=lambda l: l.number,
            )
            deployed_fleets = sorted(
                [f for f in snapshot.fleets if f.campaign_id is not None],
                key=lambda f: f.number,
            )

            return AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                name=self.NAME,
                position=self.POSITION,
                schema=[
                    {
                        "type": "select",
                        "name": "Campaign",
                        "options": [
                            {
                                "value": c.id,
                                "object_class": "campaign",
                                "id": c.id,
                                "signals": {"campaign": c.id, "commander": c.commander_id},
                            }
                            for c in snapshot.campaigns
                        ],
                    },
                    {
                        "type": "boolean",
                        "name": "Recall commander",
                        "conditions": [
                            {
                                "value1": "signal:commander",
                                "operation": "!=",
                                "value2": None,
                            },
                        ],
                    },
                    {
                        "type": "multiselect",
                        "name": "Legions",
                        "options": [
                            {
                                "value": l.id,
                                "object_class": "legion",
                                "id": l.id,
                                "conditions": [
                                    {
                                        "value1": "signal:campaign",
                                        "operation": "==",
                                        "value2": l.campaign_id,
                                    },
                                ],
                            }
                            for l in deployed_legions
                        ],
                    },
                    {
                        "type": "multiselect",
                        "name": "Fleets",
                        "options": [
                            {
                                "value": f.id,
                                "object_class": "fleet",
                                "id": f.id,
                                "conditions": [
                                    {
                                        "value1": "signal:campaign",
                                        "operation": "==",
                                        "value2": f.campaign_id,
                                    },
                                ],
                            }
                            for f in deployed_fleets
                        ],
                        "inline": True,
                    },
                ],
            )
        return None

    def execute(
        self, game_id: int, faction_id: int, selection: Dict[str, str]
    ) -> ExecutionResult:

        game = Game.objects.get(id=game_id)
        faction = Faction.objects.get(game=game_id, id=faction_id)

        #

        return ExecutionResult(True)
