import random
from typing import Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


class AttractKnightAction(ActionBase):
    NAME = "Attract knight"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.ATTRACT_KNIGHT
            and faction.has_status_item(Faction.StatusItem.CURRENT_INITIATIVE)
        ):
            return faction
        return []

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if faction:
            sender_senators = sorted(
                [
                    s
                    for s in snapshot.senators
                    if s.faction and s.faction.id == faction.id and s.alive
                ],
                key=lambda s: s.name,
            )

            return [AvailableAction.objects.create(
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
                                "signals": {"max_talents": s.talents},
                            }
                            for s in sender_senators
                        ],
                    },
                    {
                        "type": "number",
                        "name": "Talents",
                        "min": [0],
                        "max": [5, "signal:max_talents"],
                        "signals": {"talents": "VALUE"},
                    },
                    {
                        "type": "chance",
                        "name": "Chance of success",
                        "dice": 1,
                        "target_min": 6,
                        "modifiers": ["signal:talents"],
                    },
                ],
            )]
        return []

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, str],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:

        sender = selection["Senator"]
        talents = int(selection["Talents"])
        if talents < 0:
            return ExecutionResult(False, "Invalid talents amount.")

        # Spend talents
        senator = Senator.objects.get(game=game_id, faction=faction_id, id=sender)
        senator.talents -= talents
        if senator.talents < 0:
            return ExecutionResult(False, "Not enough talents.")

        # Dice roll
        dice_roll = random_resolver.roll_dice()
        modified_dice_roll = dice_roll + talents

        if modified_dice_roll >= 6:
            senator.knights += 1
            Log.create_object(
                game_id=game_id,
                text=f"{senator.display_name} successfully attracted a knight, spending {talents}T.",
            )
        else:
            Log.create_object(
                game_id=game_id,
                text=f"{senator.display_name} failed to attract a knight, wasting {talents}T.",
            )
        senator.save()

        # Progress game
        game = Game.objects.get(id=game_id)
        game.sub_phase = Game.SubPhase.SPONSOR_GAMES
        game.save()

        return ExecutionResult(True)
