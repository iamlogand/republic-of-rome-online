from typing import Dict, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


class TransferTalentsAction(ActionBase):
    NAME = "Transfer talents"
    POSITION = 1

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.REVENUE
            and game_state.game.sub_phase == Game.SubPhase.REDISTRIBUTION
        ):
            total_talents = (
                sum(
                    s.talents
                    for s in game_state.senators
                    if s.faction and s.faction.id == faction.id and s.alive
                )
                + faction.treasury
            )
            if total_talents > 0:
                return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> Optional[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if faction:
            sender_senators = sorted(
                [
                    s
                    for s in snapshot.senators
                    if s.faction
                    and s.faction.id == faction.id
                    and s.alive
                    and s.talents > 0
                ],
                key=lambda s: s.name,
            )
            sender_options = [
                {
                    "value": f"senator:{s.id}",
                    "object_class": "senator",
                    "id": s.id,
                    "signals": {
                        "max_talents": s.talents,
                        "sender": s.id,
                    },
                }
                for s in sender_senators
            ]
            if faction.treasury > 0:
                sender_options.append(
                    {
                        "value": "Faction treasury",
                        "name": "Faction treasury",
                        "signals": {
                            "max_talents": faction.treasury,
                            "sender": "faction_treasury",
                        },
                    }
                )
            recipient_senators = sorted(
                [s for s in snapshot.senators if s.alive], key=lambda x: x.name
            )

            return AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                name=self.NAME,
                position=self.POSITION,
                schema=[
                    {"type": "select", "name": "Sender", "options": sender_options},
                    {
                        "type": "select",
                        "name": "Recipient",
                        "options": [
                            {
                                "value": f"senator:{s.id}",
                                "object_class": "senator",
                                "id": s.id,
                                "conditions": [
                                    {
                                        "value1": "signal:sender",
                                        "operation": "!=",
                                        "value2": s.id,
                                    },
                                ],
                            }
                            for s in recipient_senators
                        ]
                        + [
                            {
                                "value": "Faction treasury",
                                "name": "Faction treasury",
                                "conditions": [
                                    {
                                        "value1": "signal:sender",
                                        "operation": "!=",
                                        "value2": "faction_treasury",
                                    }
                                ],
                            }
                        ],
                    },
                    {
                        "type": "number",
                        "name": "Talents",
                        "min": [1],
                        "max": ["signal:max_talents"],
                    },
                ],
            )
        return None

    def execute(
        self, game_id: int, faction_id: int, selection: Dict[str, str]
    ) -> ExecutionResult:

        game = Game.objects.get(id=game_id)
        talents = int(selection["Talents"])
        faction = Faction.objects.get(game=game_id, id=faction_id)

        # Take talents from sender
        sender_id = selection["Sender"]
        if sender_id == "Faction treasury":
            if talents > faction.treasury:
                return ExecutionResult(False)
            faction.treasury -= talents
            faction.save()
        elif sender_id.startswith("senator:"):
            sender = Senator.objects.get(
                game=game_id, faction=faction_id, id=sender_id.split(":")[1]
            )
            if talents > sender.talents:
                return ExecutionResult(False)
            sender.talents -= talents
            sender.save()
        else:
            return ExecutionResult(False)

        # Give talents to recipient
        recipient_id = selection["Recipient"]
        if recipient_id == "Faction treasury":
            faction = Faction.objects.get(game=game_id, id=faction_id)
            faction.treasury += talents
            faction.save()
        elif recipient_id.startswith("senator:"):
            recipient = Senator.objects.get(game=game_id, id=recipient_id.split(":")[1])
            recipient.talents += talents
            recipient.save()

            if recipient.faction and recipient.faction.id != faction_id:
                Log.create_object(
                    game_id=game.id,
                    text=f"{faction.display_name} transferred {talents}T to {recipient.faction.display_name}.",
                )
        else:
            return ExecutionResult(False)

        return ExecutionResult(True)
