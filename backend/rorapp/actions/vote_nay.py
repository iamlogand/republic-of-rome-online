from typing import Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Senator, Log


class VoteNayAction(ActionBase):
    NAME = "Vote nay"
    POSITION = 2

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
        selection: Dict[str, str],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:

        faction = Faction.objects.get(game=game_id, id=faction_id)
        faction.remove_status_item(FactionStatusItem.CALLED_TO_VOTE)
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

        senators = Senator.objects.filter(game=game_id, faction=faction)
        vote_count = 0
        for senator in senators:
            senator.add_status_item(Senator.StatusItem.VOTED_NAY)
            vote_count += senator.votes
        Senator.objects.bulk_update(senators, ["status_items"])

        game = Game.objects.get(id=game_id)
        game.votes_nay += vote_count
        game.save()

        Log.create_object(
            game_id,
            f"Senators in {faction.display_name} voted nay with {vote_count} votes.",
        )

        return ExecutionResult(True)
