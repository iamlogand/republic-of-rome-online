from typing import Dict, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


class SponsorGamesAction(ActionBase):
    NAME = "Sponsor games"

    def validate(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.SPONSOR_GAMES
            and faction.has_status_item(Faction.StatusItem.CURRENT_INITIATIVE)
        ):
            if any(
                s.talents >= 7
                for s in game_state.senators
                if s.faction and s.faction.id == faction.id and s.alive
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
                    and s.talents >= 7
                    and not s.has_status_item(Senator.StatusItem.CONTRIBUTED)
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
                        "name": "Sponsor",
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
                        "type": "select",
                        "name": "Type",
                        "options": [
                            {
                                "value": "Slice and dice",
                                "name": "Slice and dice",
                                "conditions": [
                                    {
                                        "value1": "signal:max_talents",
                                        "operation": ">=",
                                        "value2": "7",
                                    }
                                ],
                            },
                            {
                                "value": "Blood fest",
                                "name": "Blood fest",
                                "conditions": [
                                    {
                                        "value1": "signal:max_talents",
                                        "operation": ">=",
                                        "value2": "13",
                                    }
                                ],
                            },
                            {
                                "value": "Gladiator gala",
                                "name": "Gladiator gala",
                                "conditions": [
                                    {
                                        "value1": "signal:max_talents",
                                        "operation": ">=",
                                        "value2": "18",
                                    }
                                ],
                            },
                        ],
                    },
                ],
            )
        return None

    def execute(self, game_id: int, faction_id: int, selection: Dict[str, str]) -> bool:

        type = selection["Type"]

        sender = selection["Sponsor"]
        senator = Senator.objects.get(game=game_id, faction=faction_id, id=sender)

        # Award popularity
        if type == "Slice and dice":
            talents = 7
            popularity = 1
        if type == "Blood fest":
            talents = 13
            popularity = 2
        if type == "Gladiator gala":
            talents = 18
            popularity = 3

        # Take talents from sender
        if talents > senator.talents:
            return False
        senator.talents -= talents
        senator.popularity += popularity
        senator.save()

        # TODO implement unrest decrease for sponsoring games

        faction = Faction.objects.get(game=game_id, id=faction_id)
        Log.create_object(
            game_id=game_id,
            text=f"{senator.display_name} of {faction.display_name} sponsored games ({type.lower()}) at a cost of {talents}T. {senator.display_name} gained {popularity} popularity.",
        )

        # Progress game
        game = Game.objects.get(id=game_id)
        game.sub_phase = Game.SubPhase.FACTION_LEADER
        game.save()

        return True
