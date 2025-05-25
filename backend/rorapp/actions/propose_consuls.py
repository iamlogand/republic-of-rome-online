from typing import Dict, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.faction_leader import assign_faction_leader
from rorapp.models import AvailableAction, Faction, Game, Senator, Log


class ProposeConsulsAction(ActionBase):
    NAME = "Propose consuls"
    POSITION = 0

    def validate(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.CONSULAR_ELECTION
            and game_state.game.current_proposal is None
            and any(
                s
                for s in game_state.senators
                if s.faction
                and s.faction.id == faction.id
                and s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
            )
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> Optional[AvailableAction]:

        faction = self.validate(snapshot, faction_id)
        if faction:
            candidate_senators = sorted(
                [s for s in snapshot.senators if s.faction and s.alive],
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
                        "name": "Consul 1",
                        "options": [
                            {
                                "value": s.id,
                                "object_class": "senator",
                                "id": s.id,
                                "signals": {
                                    "selected_consul_1": s.id,
                                },
                            }
                            for s in candidate_senators
                        ],
                    },
                    {
                        "type": "select",
                        "name": "Consul 2",
                        "options": [
                            {
                                "value": s.id,
                                "object_class": "senator",
                                "id": s.id,
                                "conditions": [
                                    {
                                        "value1": "signal:selected_consul_1",
                                        "operation": "!=",
                                        "value2": s.id,
                                    },
                                ],
                            }
                            for s in candidate_senators
                        ],
                    },
                ],
            )
        return None

    def execute(self, game_id: int, faction_id: int, selection: Dict[str, str]) -> bool:
        game = Game.objects.get(id=game_id)
        faction = Faction.objects.get(game=game_id, id=faction_id)
        if not faction:
            return False

        candidate_1_id = selection["Consul 1"]
        candidate_1 = Senator.objects.get(game=game_id, id=candidate_1_id)
        candidate_2_id = selection["Consul 2"]
        candidate_2 = Senator.objects.get(game=game_id, id=candidate_2_id)

        candidates = sorted([candidate_1, candidate_2], key=lambda s: s.name)

        game.current_proposal = f"Elect consuls {candidates[0].display_name} and {candidates[1].display_name}"
        game.save()

        presiding_magistrate = [
            s
            for s in Senator.objects.filter(game=game_id, faction=faction_id)
            if s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
        ][0]

        Log.create_object(
            game_id,
            f"{presiding_magistrate.display_name} of {faction.display_name} proposed the election of {candidates[0].display_name} and {candidates[1].display_name} as consuls.",
        )

        return True
