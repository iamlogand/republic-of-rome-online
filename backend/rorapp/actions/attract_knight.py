import random
from typing import Dict, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


class AttractKnightAction(ActionBase):
    NAME = "Attract knight"

    def validate(
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
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> Optional[AvailableAction]:

        faction = self.validate(snapshot, faction_id)
        if faction:
            sender_senators = sorted(
                [
                    s
                    for s in snapshot.senators
                    if s.faction and s.faction.id == faction.id and s.alive
                ],
                key=lambda s: s.name,
            )

            return AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                name=self.NAME,
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
            )
        return None

    def execute(self, game_id: int, faction_id: int, selection: Dict[str, str]) -> bool:

        sender = selection["Senator"]
        talents = int(selection["Talents"])

        # Dice roll
        dice_roll = random.randint(1, 6)
        modified_dice_roll = dice_roll + talents

        senator = Senator.objects.get(game=game_id, faction=faction_id, id=sender)
        faction = Faction.objects.get(game=game_id, id=faction_id)
        if modified_dice_roll >= 6:
            senator.knights += 1
            senator.save()
            Log.create_object(
                game_id=game_id,
                text=f"{senator.display_name} of {faction.display_name} successfully attracted a knight, spending {talents}T.",
            )
        else:
            Log.create_object(
                game_id=game_id,
                text=f"{senator.display_name} of {faction.display_name} failed to attract a knight, wasting {talents}T.",
            )

        # Progress game
        game = Game.objects.get(id=game_id)
        game.sub_phase = Game.SubPhase.SPONSOR_GAMES
        game.save()

        return True
