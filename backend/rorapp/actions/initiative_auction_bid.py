from typing import List, Dict, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


class InitiativeAuctionBidAction(ActionBase):
    NAME = "Place bid"
    POSITION = 1

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.INITIATIVE_AUCTION
            and faction.has_status_item(FactionStatusItem.CURRENT_BIDDER)
        ):
            min_bid = get_min_bid(game_state.factions)
            if any(
                s.talents >= min_bid
                for s in game_state.senators
                if s.faction and s.faction.id == faction.id
            ):
                return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:

        # Get maximum bid amount
        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []
        max_bid = 0
        faction_senators = [
            s
            for s in snapshot.senators
            if s.faction and s.faction.id == faction.id and s.alive
        ]
        for senator in faction_senators:
            if senator.talents > max_bid:
                max_bid = senator.talents
        if max_bid < 1:
            return []

        # Get minimum bid amount
        min_bid = get_min_bid(list(snapshot.factions))

        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                schema=[
                    {
                        "type": "number",
                        "name": "Talents",
                        "min": [min_bid],
                        "max": [max_bid],
                    },
                ],
            )
        ]

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, str],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:

        talents = int(selection["Talents"])
        faction = Faction.objects.get(game=game_id, id=faction_id)
        faction.set_bid_amount(talents)
        faction.save()

        Log.create_object(
            game_id,
            f"{faction.display_name} bid {talents}T.",
        )
        return ExecutionResult(True)


def get_min_bid(
    factions: List[Faction],
) -> int:  # If used elsewhere too, consider moving to a helper file
    min_bid = 1
    for f in factions:
        bid = f.get_bid_amount()
        if bid is not None:
            min_bid = bid + 1
    return min_bid
