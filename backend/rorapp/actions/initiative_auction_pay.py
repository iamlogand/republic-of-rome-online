from typing import List, Dict, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


class InitiativeAuctionPayAction(ActionBase):
    NAME = "Pay for initiative"
    POSITION = 1

    def validate(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.INITIATIVE_AUCTION
            and faction.has_status_item(Faction.StatusItem.AUCTION_WINNER)
        ):
            bid_amount = faction.get_bid_amount()
            if (
                bid_amount
                and len(
                    [
                        s
                        for s in game_state.senators
                        if s.faction
                        and s.faction.id == faction.id
                        and s.talents >= bid_amount
                    ]
                )
                > 1  # More than one senator can afford to pay, so the player must choose
            ):
                return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> Optional[AvailableAction]:

        faction = self.validate(snapshot, faction_id)
        if not faction:
            return None

        bid_amount = faction.get_bid_amount()
        if bid_amount is None:
            return None

        candidate_senators = sorted(
            [
                s
                for s in snapshot.senators
                if s.faction
                and s.faction.id == faction.id
                and s.alive
                and s.talents >= bid_amount
            ],
            key=lambda s: s.name,
        )

        if len(candidate_senators) == 0:
            return None

        return AvailableAction.objects.create(
            game=snapshot.game,
            faction=faction,
            name=self.NAME,
            position=self.POSITION,
            schema=[
                {
                    "type": "select",
                    "name": "Payer",
                    "options": [
                        {
                            "value": s.id,
                            "object_class": "senator",
                            "id": s.id,
                        }
                        for s in candidate_senators
                    ],
                },
            ],
            context={"talents": bid_amount},
        )

    def execute(self, game_id: int, faction_id: int, selection: Dict[str, str]) -> bool:
        senator_id = selection["Payer"]
        senator = Senator.objects.get(game=game_id, faction=faction_id, id=senator_id)
        faction = Faction.objects.get(game=game_id, id=faction_id)

        bid_amount = faction.get_bid_amount()
        if bid_amount is None or bid_amount > senator.talents:
            return False

        senator.talents -= bid_amount
        senator.save()

        faction.remove_status_item(Faction.StatusItem.AUCTION_WINNER)
        faction.set_bid_amount(None)

        game = Game.objects.get(id=game_id)
        game.sub_phase = Game.SubPhase.INITIATIVE_ROLL
        game.save()

        factions = Faction.objects.filter(game=game_id)
        for initiative_index in Faction.INITIATIVE_INDICES:
            if not any(
                f.has_status_item(Faction.StatusItem.initiative(initiative_index))
                for f in factions
            ):
                faction.add_status_item(Faction.StatusItem.initiative(initiative_index))
                faction.add_status_item(Faction.StatusItem.CURRENT_INITIATIVE)
                faction.save()

                Log.create_object(
                    game_id=game_id,
                    text=f"{senator.display_name} paid {bid_amount}T for initiative {initiative_index}.",
                )

                # Clean up
                for f in Faction.objects.filter(game=game_id):
                    f.set_bid_amount(None)
                    if f.has_status_item(Faction.StatusItem.SKIPPED):
                        f.remove_status_item(Faction.StatusItem.SKIPPED)
                return True

        return False
