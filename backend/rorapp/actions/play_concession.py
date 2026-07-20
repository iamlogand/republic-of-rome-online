from typing import Any, Dict, List, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.concession import Concession
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


class PlayConcessionAction(ActionBase):
    NAME = "Play concession"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if not faction:
            return None

        if not bool(faction.get_cards_by_prefix("concession:")):
            return None

        if (
            game_state.game.phase == Game.Phase.REVOLUTION
            and game_state.game.sub_phase == Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
            and faction.has_status_item(FactionStatusItem.AWAITING_DECISION)
        ):
            return faction

        if (
            game_state.game.phase == Game.Phase.INITIAL
            and game_state.game.sub_phase == Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
            and faction.has_status_item(FactionStatusItem.AWAITING_DECISION)
        ):
            return faction

        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if faction:
            land_bill_active = (
                snapshot.game.has_effect(GameEffect.LAND_BILL_1)
                or snapshot.game.has_effect(GameEffect.LAND_BILL_2)
                or snapshot.game.has_effect(GameEffect.LAND_BILL_3)
            )
            concession_cards = [
                c
                for c in faction.get_cards_by_prefix("concession:")
                if c != f"concession:{Concession.LAND_COMMISSIONER.value}"
                or land_bill_active
            ]
            if not concession_cards:
                return []
            senators = sorted(
                [
                    s
                    for s in snapshot.senators
                    if s.faction and s.faction.id == faction.id and s.alive
                ],
                key=lambda s: s.family_name,
            )

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
                                    "value": c,
                                    "name": c.split(":", 1)[1],
                                }
                                for c in concession_cards
                            ],
                        },
                        {
                            "type": "select",
                            "name": "Senator",
                            "options": [
                                {
                                    "value": s.id,
                                    "object_class": "senator",
                                    "id": s.id,
                                }
                                for s in senators
                            ],
                        },
                    ],
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

        # Get senator
        senator = Senator.objects.get(
            game=game_id, faction=faction_id, id=selection["Senator"], alive=True
        )

        # Parse concession
        concession_card = selection["Concession"]
        concession_name = concession_card.split(":", 1)[1]
        try:
            concession = Concession(concession_name)
        except ValueError:
            return ExecutionResult(False, "Invalid concession.")

        if concession == Concession.LAND_COMMISSIONER:
            game = Game.objects.get(id=game_id)
            land_bill_active = (
                game.has_effect(GameEffect.LAND_BILL_1)
                or game.has_effect(GameEffect.LAND_BILL_2)
                or game.has_effect(GameEffect.LAND_BILL_3)
            )
            if not land_bill_active:
                return ExecutionResult(
                    False,
                    "The land commissioner concession can only be played when a land bill is in effect.",
                )

        # Remove card from faction
        faction = Faction.objects.get(game=game_id, id=faction_id)
        faction.remove_card(concession_card)
        faction.save()

        # Add concession to senator
        senator.add_concession(concession)
        senator.save()

        # Create log
        Log.create_object(
            game_id=game_id,
            text=f"{faction.display_name} played the {concession.value} concession, awarding it to {senator.display_name}.",
        )

        return ExecutionResult(True)
