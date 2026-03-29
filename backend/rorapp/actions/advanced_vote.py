from typing import Any, Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.text import format_list, pluralize
from rorapp.models import AvailableAction, Faction, Game, Senator, Log


VALID_DECISIONS = {"yea", "nay", "abstain"}


class AdvancedVoteAction(ActionBase):
    NAME = "Advanced vote"
    POSITION = 4

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
            and (
                faction.has_status_item(FactionStatusItem.CALLED_TO_VOTE)
                or (
                    any(
                        s
                        for s in game_state.senators
                        if s.faction
                        and s.faction.id == faction.id
                        and s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
                    )
                    and not faction.has_status_item(FactionStatusItem.DONE)
                    and not any(
                        f
                        for f in game_state.factions
                        if f.has_status_item(FactionStatusItem.CALLED_TO_VOTE)
                    )
                )
            )
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if faction:
            return [
                AvailableAction.objects.create(
                    game=snapshot.game,
                    faction=faction,
                    base_name=self.NAME,
                    position=self.POSITION,
                    schema=[],
                )
            ]
        return []

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, Any],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:

        senator_votes = selection.get("senator_votes")
        if not isinstance(senator_votes, dict):
            return ExecutionResult(False)

        faction = Faction.objects.get(game=game_id, id=faction_id)
        own_senators = list(Senator.objects.filter(game=game_id, faction=faction))

        # Keys must exactly match faction's senator IDs
        valid_ids = {str(s.id) for s in own_senators}
        if set(senator_votes.keys()) != valid_ids:
            return ExecutionResult(False)

        # Validate all entries
        for senator in own_senators:
            entry = senator_votes.get(str(senator.id))
            if not isinstance(entry, dict):
                return ExecutionResult(False)

            decision = entry.get("decision")
            if decision not in VALID_DECISIONS:
                return ExecutionResult(False)

            try:
                bought_votes = int(entry.get("bought_votes", 0))
            except (ValueError, TypeError):
                return ExecutionResult(False)

            if bought_votes < 0:
                return ExecutionResult(False)

            if bought_votes > senator.talents:
                return ExecutionResult(False)

        # Apply changes
        faction.remove_status_item(FactionStatusItem.CALLED_TO_VOTE)
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

        yea_count = 0
        nay_count = 0
        total_bought = 0
        yea_senators: List[Senator] = []
        nay_senators: List[Senator] = []
        abstain_senators: List[Senator] = []
        yea_bought = 0
        nay_bought = 0

        for senator in own_senators:
            entry = senator_votes[str(senator.id)]
            decision = entry["decision"]
            bought_votes = int(entry["bought_votes"])
            effective_votes = senator.votes + bought_votes

            senator.talents -= bought_votes
            total_bought += bought_votes

            if decision == "yea":
                senator.add_status_item(Senator.StatusItem.VOTED_YEA)
                yea_count += effective_votes
                yea_senators.append(senator)
                yea_bought += bought_votes
            elif decision == "nay":
                senator.add_status_item(Senator.StatusItem.VOTED_NAY)
                nay_count += effective_votes
                nay_senators.append(senator)
                nay_bought += bought_votes
            else:
                senator.add_status_item(Senator.StatusItem.ABSTAINED)
                abstain_senators.append(senator)

        Senator.objects.bulk_update(own_senators, ["status_items", "talents"])

        game = Game.objects.get(id=game_id)
        game.votes_yea += yea_count
        game.votes_nay += nay_count
        game.save()

        decisions = {senator_votes[str(s.id)]["decision"] for s in own_senators}
        if decisions == {"yea"}:
            log_message = f"Senators in {faction.display_name} voted yea with {pluralize(yea_count, 'vote')}"
            if total_bought > 0:
                log_message += f", spending {total_bought}T to buy {'a vote' if total_bought == 1 else 'votes'}"
            log_message += "."
        elif decisions == {"nay"}:
            log_message = f"Senators in {faction.display_name} voted nay with {pluralize(nay_count, 'vote')}"
            if total_bought > 0:
                log_message += f", spending {total_bought}T to buy {'a vote' if total_bought == 1 else 'votes'}"
            log_message += "."
        elif decisions == {"abstain"}:
            log_message = f"Senators in {faction.display_name} abstained."
        else:
            log_message = f"Senators in {faction.display_name} split their vote."
            if yea_senators:
                part = f" {format_list([s.display_name for s in yea_senators])} voted yea with {pluralize(yea_count, 'vote')}"
                if yea_bought > 0:
                    part += f", spending {yea_bought}T to buy {'a vote' if yea_bought == 1 else 'votes'}"
                log_message += part + "."
            if nay_senators:
                part = f" {format_list([s.display_name for s in nay_senators])} voted nay with {pluralize(nay_count, 'vote')}"
                if nay_bought > 0:
                    part += f", spending {nay_bought}T to buy {'a vote' if nay_bought == 1 else 'votes'}"
                log_message += part + "."
            if abstain_senators:
                log_message += f" {format_list([s.display_name for s in abstain_senators])} abstained."

        Log.create_object(game_id, log_message)

        return ExecutionResult(True)
