from typing import Dict, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


class ContributeAction(ActionBase):
    NAME = "Contribute"
    POSITION = 0

    def validate(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.REVENUE
            and game_state.game.sub_phase == Game.SubPhase.REDISTRIBUTION
            and sum(
                s.talents
                for s in game_state.senators
                if s.faction
                and s.faction.id == faction.id
                and s.alive
                and not s.has_status_item(Senator.StatusItem.CONTRIBUTED)
            )
            > 0
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
                    if s.faction
                    and s.faction.id == faction.id
                    and s.alive
                    and s.talents > 0
                    and not s.has_status_item(Senator.StatusItem.CONTRIBUTED)
                ],
                key=lambda s: s.name,
            )

            return AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                name=self.NAME,
                position=self.POSITION,
                schema=[
                    {
                        "type": "select",
                        "name": "Contributor",
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
                        "min": [1],
                        "max": ["signal:max_talents"],
                    },
                ],
            )
        return None

    def execute(self, game_id: int, faction_id: int, selection: Dict[str, str]) -> bool:

        talents = int(selection["Talents"])
        faction = Faction.objects.get(game=game_id, id=faction_id)

        # Take talents from sender
        sender = selection["Contributor"]
        senator = Senator.objects.get(game=game_id, faction=faction_id, id=sender)
        if talents > senator.talents or senator.has_status_item(
            Senator.StatusItem.CONTRIBUTED
        ):
            return False
        senator.talents -= talents

        # Award influence
        if talents >= 50:
            senator.influence += 7
        elif talents >= 25:
            senator.influence += 3
        elif talents >= 10:
            senator.influence += 1

        # Prevent further contributions
        senator.add_status_item(Senator.StatusItem.CONTRIBUTED)
        senator.save()

        # Give talents to the State treasury
        game = Game.objects.get(id=game_id)
        game.state_treasury += talents
        game.save()

        Log.create_object(
            game_id=game.id,
            text=f"{senator.display_name} of {faction.display_name} contributed {talents}T to the State treasury.",
        )

        return True
