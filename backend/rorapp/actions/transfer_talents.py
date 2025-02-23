from typing import Dict, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


class TransferTalentsAction(ActionBase):
    NAME = "Transfer talents"

    def validate(
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

        faction = self.validate(snapshot, faction_id)
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
                        "selected_sender": s.id,
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
                            "selected_sender": "faction_treasury",
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
                                    {"not_equal": ["signal:selected_sender", s.id]}
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
                                        "not_equal": [
                                            "signal:selected_sender",
                                            "faction_treasury",
                                        ]
                                    }
                                ],
                            }
                        ],
                    },
                    {
                        "type": "number",
                        "name": "Talents",
                        "min": 1,
                        "max": "signal:max_talents",
                    },
                ],
            )
        return None

    def execute(self, game_id: int, faction_id: int, selection: Dict[str, str]) -> bool:

        game = Game.objects.get(id=game_id)
        talents = int(selection["Talents"])
        faction = Faction.objects.get(game=game_id, id=faction_id)

        # Take talents from sender
        sender = selection["Sender"]
        if sender == "Faction treasury":
            if talents > faction.treasury:
                return False
            faction.treasury -= talents
            faction.save()
        elif sender.startswith("senator:"):
            sender_senator = Senator.objects.get(
                game=game_id, faction=faction_id, id=sender.split(":")[1]
            )
            if talents > sender_senator.talents:
                return False
            sender_senator.talents -= talents
            sender_senator.save()
        else:
            return False

        # Give talents to recipient
        recipient = selection["Recipient"]
        if recipient == "Faction treasury":
            faction = Faction.objects.get(game=game_id, id=faction_id)
            faction.treasury += talents
            faction.save()
        elif recipient.startswith("senator:"):
            recipient_senator = Senator.objects.get(
                game=game_id, id=recipient.split(":")[1]
            )
            recipient_senator.talents += talents
            recipient_senator.save()

            if recipient_senator.faction and recipient_senator.faction.id != faction_id:
                recipient_faction = Faction.objects.get(id=recipient_senator.faction.id)
                Log.create_object(
                    game_id=game.id,
                    text=f"{faction.display_name} transferred {talents}T to {recipient_senator.display_name} of {recipient_faction.display_name}.",
                )
        else:
            return False

        return True
