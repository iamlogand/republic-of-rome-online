from typing import Any, Dict, List, Optional, Tuple
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.concession import GRAIN_CONCESSION_REVENUE, Concession
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


def _unclaimed_grain_concessions(
    game_state: GameStateLive | GameStateSnapshot, faction_id: int
) -> List[Tuple[Senator, Concession]]:
    return [
        (s, c)
        for s in game_state.senators
        if s.faction and s.faction.id == faction_id and s.alive
        for c in s.get_concessions()
        if c in GRAIN_CONCESSION_REVENUE
        and Senator.StatusItem.profiteered(c) not in s.status_items
    ]


class ProfiteerFromFamineAction(ActionBase):
    NAME = "Profiteer from famine"
    POSITION = 3

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.REVENUE
            and game_state.game.sub_phase == Game.SubPhase.REDISTRIBUTION
            and _unclaimed_grain_concessions(game_state, faction.id)
            and game_state.game.famine_severity > 0
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        severity = snapshot.game.famine_severity
        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                field_descriptors=[
                    {
                        "type": "select",
                        "name": "Concession",
                        "options": [
                            {
                                "value": c.value,
                                "name": f"{c.value} (+{GRAIN_CONCESSION_REVENUE[c] * severity}T, -{severity + 1} popularity)",
                            }
                            for _, c in _unclaimed_grain_concessions(
                                snapshot, faction.id
                            )
                        ],
                    },
                ],
            )
        ]

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, Any],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:

        game_state = GameStateLive(game_id)
        claim = next(
            (
                (s, c)
                for s, c in _unclaimed_grain_concessions(game_state, faction_id)
                if c.value == selection["Concession"]
            ),
            None,
        )
        if claim is None:
            return ExecutionResult(False)
        senator, concession = claim

        # Revenue already paid the base income, so only the extra multiples are added (1.06.12)
        severity = game_state.game.famine_severity
        talents = GRAIN_CONCESSION_REVENUE[concession] * severity
        senator.talents += talents
        popularity_loss = -senator.change_popularity(-(severity + 1))
        senator.status_items.append(Senator.StatusItem.profiteered(concession))
        senator.save()

        message = f"{senator.display_name} profiteered from the famine on the {concession.value} concession, earning an extra {talents}T."
        if popularity_loss > 0:
            message += f" He lost {popularity_loss} popularity."
        Log.create_object(game_id=game_id, text=message)

        return ExecutionResult(True)
