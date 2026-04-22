from typing import Any, Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.dictator_appointment import appoint_dictator
from rorapp.helpers.dictator_candidates import get_eligible_dictator_candidates
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


class AppointDictatorAction(ActionBase):
    NAME = "Appoint Dictator"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if not faction:
            return None
        if not (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.DICTATOR_APPOINTMENT
            and (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
        ):
            return None
        if faction.has_status_item(FactionStatusItem.SKIPPED):
            return None
        # Faction must control at least one consul senator
        has_consul = any(
            s
            for s in game_state.senators
            if s.faction
            and s.faction.id == faction.id
            and (
                s.has_title(Senator.Title.ROME_CONSUL)
                or s.has_title(Senator.Title.FIELD_CONSUL)
            )
        )
        if not has_consul:
            return None
        return faction

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        defeated_names = set()
        for proposal in snapshot.game.defeated_proposals:
            if proposal.startswith("Appoint Dictator "):
                defeated_names.add(proposal[len("Appoint Dictator ") :])

        all_candidates = get_eligible_dictator_candidates(snapshot.senators)
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
                        "name": "Dictator",
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
        senators = list(Senator.objects.filter(game=game_id, alive=True))
        senator_id = selection["Dictator"]
        nominee = Senator.objects.get(id=senator_id)

        # If this faction already nominated someone, clear that pick so we treat this as a fresh nomination
        if faction.has_status_item(FactionStatusItem.DONE):
            for s in senators:
                if s.has_status_item(Senator.StatusItem.SUGGESTED_DICTATOR):
                    s.remove_status_item(Senator.StatusItem.SUGGESTED_DICTATOR)
                    s.save()
                    break
            faction.remove_status_item(FactionStatusItem.DONE)
            faction.save()

        if nominee.has_status_item(Senator.StatusItem.SUGGESTED_DICTATOR):
            # Other consul already suggested this senator — both consuls agree → appoint
            Log.create_object(
                game_id,
                f"Both consuls agreed to appoint {nominee.display_name} as Dictator.",
            )
            nominee.remove_status_item(Senator.StatusItem.SUGGESTED_DICTATOR)
            nominee.save()
            # Clear DONE from all factions
            factions = list(Faction.objects.filter(game=game_id))
            for f in factions:
                f.remove_status_item(FactionStatusItem.DONE)
            Faction.objects.bulk_update(factions, ["status_items"])
            appoint_dictator(game_id, senator_id)
            return ExecutionResult(True)

        # Check if any other senator already has SUGGESTED_DICTATOR (disagreement)
        other_suggested = [
            s
            for s in senators
            if s.id != senator_id
            and s.has_status_item(Senator.StatusItem.SUGGESTED_DICTATOR)
        ]
        if other_suggested:
            # Consuls nominated different senators → go to election
            Log.create_object(
                game_id,
                "Consuls could not agree on a Dictator.",
            )
            # Clear all SUGGESTED_DICTATOR statuses
            for s in senators:
                s.remove_status_item(Senator.StatusItem.SUGGESTED_DICTATOR)
            Senator.objects.bulk_update(senators, ["status_items"])
            # Clear DONE and SKIPPED from consul-holding factions
            consul_faction_ids = {
                s.faction_id
                for s in senators
                if s.faction_id
                and (
                    s.has_title(Senator.Title.ROME_CONSUL)
                    or s.has_title(Senator.Title.FIELD_CONSUL)
                )
            }
            factions = list(
                Faction.objects.filter(game=game_id, id__in=consul_faction_ids)
            )
            for f in factions:
                f.remove_status_item(FactionStatusItem.DONE)
                f.remove_status_item(FactionStatusItem.SKIPPED)
            Faction.objects.bulk_update(factions, ["status_items"])
            game.sub_phase = Game.SubPhase.DICTATOR_ELECTION
            game.clear_senate_sub_phase_proposals()
            game.save()
            return ExecutionResult(True)

        # First nomination — mark senator and record that this faction has decided
        nominee.add_status_item(Senator.StatusItem.SUGGESTED_DICTATOR)
        nominee.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
        nominee.save()
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()
        Log.create_object(
            game_id,
            f"{faction.display_name} nominated {nominee.display_name} as Dictator.",
        )
        return ExecutionResult(True)
