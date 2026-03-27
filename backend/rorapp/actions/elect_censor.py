from typing import Any, Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.censor_candidates import get_eligible_censor_candidates
from rorapp.models import AvailableAction, Faction, Game, Senator, Log


class ElectCensorAction(ActionBase):
    NAME = "Elect Censor"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.CENSOR_ELECTION
            and (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
            and not any(
                s
                for s in game_state.senators
                if s.has_status_item(Senator.StatusItem.UNANIMOUSLY_DEFEATED)
            )
            and (
                any(
                    s
                    for s in game_state.senators
                    if s.faction
                    and s.faction.id == faction.id
                    and s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
                )
                and not any(
                    f
                    for f in game_state.factions
                    if f.id != faction.id
                    and f.has_status_item(FactionStatusItem.PLAYED_TRIBUNE)
                )
                or faction.has_status_item(FactionStatusItem.PLAYED_TRIBUNE)
            )
            and not any(
                f
                for f in game_state.factions
                if f.has_status_item(FactionStatusItem.CALLED_TO_VOTE)
            )
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        # Build list of already-defeated censor nominations
        defeated_names = set()
        for proposal in snapshot.game.defeated_proposals:
            if proposal.startswith("Elect Censor "):
                defeated_names.add(proposal[len("Elect Censor ") :])

        all_candidates, is_fallback = get_eligible_censor_candidates(snapshot.senators)

        candidate_senators = sorted(
            [s for s in all_candidates if s.display_name not in defeated_names],
            key=lambda s: s.family_name,
        )

        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                schema=[
                    {
                        "type": "select",
                        "name": "Censor",
                        "options": [
                            {
                                "value": s.id,
                                "object_class": "senator",
                                "id": s.id,
                            }
                            for s in candidate_senators
                        ],
                    }
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

        game = Game.objects.get(id=game_id)
        faction = Faction.objects.get(game=game_id, id=faction_id)
        senators = Senator.objects.filter(game=game_id)
        senator_id = selection["Censor"]
        senator = senators.get(id=senator_id)

        game.current_proposal = f"Elect Censor {senator.display_name}"
        game.save()

        is_tribune_proposal = faction.has_status_item(FactionStatusItem.PLAYED_TRIBUNE)
        if is_tribune_proposal:
            faction.remove_status_item(FactionStatusItem.PLAYED_TRIBUNE)
            Log.create_object(
                game_id,
                f"{faction.display_name} used their tribune to propose the motion: {game.current_proposal}.",
            )
        else:
            presiding_magistrate = next(
                (
                    s
                    for s in faction.senators.all()
                    if s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
                ),
                None,
            )
            pm_name = (
                presiding_magistrate.display_name
                if presiding_magistrate
                else "Presiding Magistrate"
            )
            Log.create_object(
                game_id,
                f"{pm_name} proposed the motion: {game.current_proposal}.",
            )
        faction.add_status_item(FactionStatusItem.PROPOSER)
        faction.save()

        return ExecutionResult(True)
