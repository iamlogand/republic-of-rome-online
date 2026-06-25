import random
from typing import Any, Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
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
            and faction.has_status_item(FactionStatusItem.CURRENT_INITIATIVE)
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if faction:
            evil_omens_level = snapshot.game.count_effect(GameEffect.EVIL_OMENS)
            sender_senators = sorted(
                [
                    s
                    for s in snapshot.senators
                    if s.faction
                    and s.faction.id == faction.id
                    and s.alive
                    and s.talents >= evil_omens_level
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
                            "min": [evil_omens_level],
                            "max": [5, "signal:max_talents"],
                            "signals": {"talents": "VALUE"},
                        },
                        {
                            "type": "chance",
                            "name": "Chance of success",
                            "dice": 1,
                            "target_min": 6,
                            "modifiers": [
                                "signal:talents",
                                -evil_omens_level,
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
        game = Game.objects.get(id=game_id)
        evil_omens_level = game.count_effect(GameEffect.EVIL_OMENS)
        dice_roll = random_resolver.roll_dice()
        modified_dice_roll = dice_roll + talents - evil_omens_level
        guaranteed = (modified_dice_roll - dice_roll) + 1 >= 6

        if modified_dice_roll >= 6:
            senator.knights += 1
            if guaranteed and talents > 0:
                text = f"{senator.display_name} bought a knight for {talents}T."
            else:
                text = f"{senator.display_name} successfully attracted a knight{' for free' if talents == 0 else f', spending {talents}T'}."
            Log.create_object(game_id=game_id, text=text)
        else:
            Log.create_object(
                game_id=game_id,
                text=f"{senator.display_name} failed to attract a knight{'' if talents == 0 else f', wasting {talents}T'}.",
            )
        senator.save()

        # Progress game
        game.sub_phase = Game.SubPhase.SPONSOR_GAMES
        game.save()

        return ExecutionResult(True)
