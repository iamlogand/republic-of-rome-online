from typing import Dict, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Senator


class SelectFactionLeaderAction(ActionBase):
    NAME = "Select faction leader"

    def validate(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if faction:
            if (
                game_state.game.phase == Game.Phase.INITIAL
                and game_state.game.sub_phase == Game.SubPhase.FACTION_LEADER
                and not faction.has_status_item(Faction.StatusItem.DONE)
            ):
                return faction
            elif (
                game_state.game.phase == Game.Phase.FORUM
                and game_state.game.sub_phase == Game.SubPhase.FACTION_LEADER
                and faction.has_status_item(Faction.StatusItem.CURRENT_INITIATIVE)
            ):
                return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> Optional[AvailableAction]:

        faction = self.validate(snapshot, faction_id)
        if faction:
            candidate_senators = sorted(
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
                        "name": "Faction leader",
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
            )
        return None

    def execute(self, game_id: int, faction_id: int, selection: Dict[str, str]) -> bool:

        # Remove faction leader titles
        senators = Senator.objects.filter(
            game_id=game_id, faction=faction_id, alive=True
        )
        for senator in senators:
            senator.remove_title(Senator.Title.FACTION_LEADER)

        # Assign faction leader title
        senator_id = int(selection["Faction leader"])
        senator = senators.get(id=senator_id)
        if not senator.has_title(Senator.Title.FACTION_LEADER):
            senator.add_title(Senator.Title.FACTION_LEADER)
            senator.save()

        # Done / end initiative
        game = Game.objects.get(id=game_id)
        faction = Faction.objects.get(game=game_id, id=faction_id)
        if game.phase == Game.Phase.INITIAL:
            faction.add_status_item(Faction.StatusItem.DONE)
        if game.phase == Game.Phase.FORUM:
            faction.remove_status_item(Faction.StatusItem.CURRENT_INITIATIVE)
            game.sub_phase = Game.SubPhase.END
            game.save()
        faction.save()

        return True
