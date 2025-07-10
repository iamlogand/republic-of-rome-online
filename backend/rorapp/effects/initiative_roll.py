import json
import os
import random
from typing import Optional
from django.conf import settings

from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Log, War


class InitiativeRollEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.INITIATIVE_ROLL
        )

    def execute(self, game_id: int) -> bool:

        game = Game.objects.get(id=game_id)

        current_faction: Optional[Faction] = None
        factions = Faction.objects.filter(game=game_id)
        for faction in factions:
            if faction.has_status_item(Faction.StatusItem.CURRENT_INITIATIVE):
                current_faction = faction

        if not current_faction:
            return False

        # The random bit is temporary to prevent too many wars coming out,
        # whilst other cards are not yet implemented
        # TODO remove the random thing
        if len(game.deck) > 0:
            if random.random() < 0.2:
                next_card: str = game.deck[0]
                game.deck = game.deck[1:]

                if next_card.split(":")[0] == "war":
                    # New war drawn
                    war_name = next_card.split(":")[1]
                    war_json_path = os.path.join(
                        settings.BASE_DIR, "rorapp", "data", "war.json"
                    )
                    with open(war_json_path, "r") as file:
                        wars_dict = json.load(file)
                    war_data = wars_dict[war_name]
                    war = War(
                        game=game,
                        name=war_name,
                        index=war_data["index"],
                        land_strength=war_data["land_strength"],
                        fleet_support=war_data["fleet_support"],
                        naval_strength=war_data["naval_strength"],
                        disaster_numbers=war_data["disaster_numbers"],
                        standoff_numbers=war_data["standoff_numbers"],
                        spoils=war_data["spoils"],
                        famine=war_data["famine"],
                    )
                    if "series_name" in war_data:
                        war.series_name = war_data["series_name"]
                    if war.naval_strength > 0:
                        war.undefeated_navy = True
                    if war_data["immediately_active"]:
                        war.status = War.Status.ACTIVE
                    else:
                        war.status = War.Status.INACTIVE

                    new_war_message = (
                        f"{current_faction.display_name} has drawn the {war.name}."
                    )
                    matching_war_messages = []

                    # Handle matching wars
                    for matching_war in (
                        War.objects.filter(game=game_id, series_name=war.series_name)
                        .exclude(id=war.id, status=War.Status.DEFEATED)
                        .order_by("index")
                    ):
                        if matching_war.status == War.Status.INACTIVE:
                            matching_war.status = War.Status.ACTIVE
                            matching_war.save()
                            matching_war_messages.append(
                                f"The {matching_war.name} has been activated by the {war.name}."
                            )
                        war.status = War.Status.IMMINENT

                    if war.status == War.Status.IMMINENT:
                        new_war_message = f"{new_war_message[:-1]}, which is imminent due to a matching war."
                    elif war.status == War.Status.ACTIVE:
                        new_war_message = (
                            f"{new_war_message[:-1]}, which is immediately active."
                        )
                    war.save()

                    Log.create_object(game_id, new_war_message)
                    for message in matching_war_messages:
                        Log.create_object(game_id, message)
            else:
                Log.create_object(game_id, "[[card not yet implemented]]")

        # Progress game
        game.sub_phase = Game.SubPhase.ATTRACT_KNIGHT
        game.save()

        return True
