from typing import Dict, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Senator


class VoteCallFactionAction(ActionBase):
    NAME = "Call faction to vote"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.SENATE
            and not (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
            and not any(
                s
                for s in game_state.senators
                if s.has_status_item(Senator.StatusItem.CONSENT_REQUIRED)
            )
            and any(
                s
                for s in game_state.senators
                if s.faction
                and s.faction.id == faction.id
                and s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
            )
            and not any(
                f
                for f in game_state.factions
                if f.has_status_item(Faction.StatusItem.CALLED_TO_VOTE)
            )
            and any(
                f
                for f in game_state.factions
                if f.id != faction.id and not f.has_status_item(Faction.StatusItem.DONE)
            )
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> Optional[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if faction:
            factions = sorted(
                [
                    f
                    for f in snapshot.factions
                    if f.id != faction.id
                    and not f.has_status_item(Faction.StatusItem.DONE)
                ],
                key=lambda f: f.position,
            )

            return AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                name=self.NAME,
                position=self.POSITION,
                schema=[
                    {
                        "type": "select",
                        "name": "Faction",
                        "options": [
                            {
                                "value": f.id,
                                "object_class": "faction",
                                "id": f.id,
                            }
                            for f in factions
                        ],
                    }
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

        # Call faction to vote
        selected_faction_id = selection["Faction"]
        selected_faction = Faction.objects.get(game=game_id, id=selected_faction_id)
        selected_faction.add_status_item(Faction.StatusItem.CALLED_TO_VOTE)
        selected_faction.save()

        return ExecutionResult(True)
