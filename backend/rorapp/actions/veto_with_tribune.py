from typing import Any, Dict, List, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.end_prosecutions import end_prosecutions
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


class VetoWithTribuneAction(ActionBase):
    NAME = "Veto with tribune"
    POSITION = 100

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if not (
            faction
            and game_state.game.phase == Game.Phase.SENATE
            and game_state.game.current_proposal
            and game_state.game.current_proposal.strip()
            and faction.has_card("tribune")
            and not faction.has_status_item(FactionStatusItem.DONE)
        ):
            return None

        # Proposals raised by the Dictator (as PM) cannot be vetoed.
        # This does NOT apply when: the Dictator stepped down (no PM title) or the
        # proposal was raised via tribune by another faction.
        dictator_is_pm = any(
            s
            for s in game_state.senators
            if s.has_title(Senator.Title.DICTATOR)
            and s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
        )
        if dictator_is_pm:
            tribune_proposal = any(
                f.has_status_item(FactionStatusItem.PROPOSED_VIA_TRIBUNE)
                for f in game_state.factions
            )
            if not tribune_proposal:
                return None

        return faction

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                schema=[],
            )
        ]

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, Any],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:

        faction = Faction.objects.get(game=game_id, id=faction_id)
        game = Game.objects.get(id=game_id)

        if not faction.has_card("tribune"):
            return ExecutionResult(False, "No tribune card in hand.")
        if not game.current_proposal:
            return ExecutionResult(False, "No proposal on the floor.")

        is_prosecution = game.current_proposal.startswith("Prosecute ")

        # Consume the tribune card
        faction.remove_card("tribune")
        faction.save()

        # Record the veto
        vetoed_proposal = game.current_proposal
        game.add_defeated_proposal(vetoed_proposal)
        game.current_proposal = None
        game.votes_yea = 0
        game.votes_nay = 0

        if is_prosecution:
            is_major = vetoed_proposal.endswith("major corruption in office")
            if is_major:
                game.prosecutions_remaining = 0
            else:
                game.prosecutions_remaining = max(0, game.prosecutions_remaining - 1)

        game.save()

        # Clear faction statuses
        factions = list(Faction.objects.filter(game=game_id))
        for f in factions:
            f.remove_status_item(FactionStatusItem.DONE)
            f.remove_status_item(FactionStatusItem.CALLED_TO_VOTE)
            f.remove_status_item(FactionStatusItem.PROPOSED_VIA_TRIBUNE)
        Faction.objects.bulk_update(factions, ["status_items"])

        # Clear senator statuses
        senator_fields_to_clear = [
            Senator.StatusItem.VOTED_YEA,
            Senator.StatusItem.VOTED_NAY,
            Senator.StatusItem.ABSTAINED,
            Senator.StatusItem.CONSENT_REQUIRED,
        ]
        if is_prosecution:
            senator_fields_to_clear += [
                Senator.StatusItem.ACCUSED,
                Senator.StatusItem.PROSECUTOR,
                Senator.StatusItem.APPEALED_TO_PEOPLE,
            ]

        senators = list(Senator.objects.filter(game=game_id))
        for senator in senators:
            for item in senator_fields_to_clear:
                senator.remove_status_item(item)
        Senator.objects.bulk_update(senators, ["status_items"])

        Log.create_object(
            game_id,
            f"{faction.display_name} played a tribune to veto the motion: {vetoed_proposal}.",
        )

        # If all prosecutions used up, close the prosecution phase
        if is_prosecution:
            game.refresh_from_db()
            if game.prosecutions_remaining == 0:
                end_prosecutions(game_id)

        return ExecutionResult(True)
