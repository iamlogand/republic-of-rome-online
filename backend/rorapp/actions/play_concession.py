from typing import Dict, List, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.concession import Concession
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
        if (
            faction
            and game_state.game.phase == Game.Phase.REVOLUTION
            and game_state.game.sub_phase == Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
            and faction.has_status_item(FactionStatusItem.MAKING_DECISION)
            and any(c.startswith("concession:") for c in faction.cards)
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if faction:
            concession_cards = [c for c in faction.cards if c.startswith("concession:")]
            senators = sorted(
                [
                    s
                    for s in snapshot.senators
                    if s.faction and s.faction.id == faction.id and s.alive
                ],
                key=lambda s: s.name,
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
                    ],
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

        # Remove card from faction
        faction = Faction.objects.get(game=game_id, id=faction_id)
        faction.cards.remove(concession_card)
        faction.save()

        # Add concession to senator
        senator.add_concession(concession)
        senator.save()

        # Create log
        Log.create_object(
            game_id=game_id,
            text=f"{senator.display_name} of {faction.display_name} received the {concession.value} concession.",
        )

        return ExecutionResult(True)
