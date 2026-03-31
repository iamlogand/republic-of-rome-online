import json
import os
from typing import Optional
from django.conf import settings

from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.game_data import (
    get_senator_codes,
    load_enemy_leaders,
    load_senators,
)
from rorapp.helpers.text import format_list
from rorapp.models import EnemyLeader, Faction, Game, Log, Senator, War


class InitiativeRollEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.INITIATIVE_ROLL
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        game = Game.objects.get(id=game_id)

        current_faction: Optional[Faction] = None
        factions = Faction.objects.filter(game=game_id)
        for faction in factions:
            if faction.has_status_item(FactionStatusItem.CURRENT_INITIATIVE):
                current_faction = faction

        if not current_faction:
            return False

        if game.deck:
            next_card: str = game.deck[0]
            game.deck = game.deck[1:]

            parts = next_card.split(":", 1)
            prefix = parts[0]
            card_name = parts[1] if len(parts) > 1 else ""

            if prefix == "war":
                # New war drawn
                war_json_path = os.path.join(
                    settings.BASE_DIR, "rorapp", "data", "war.json"
                )
                with open(war_json_path, "r") as file:
                    wars_dict = json.load(file)
                war_data = wars_dict[card_name]
                war = War(
                    game=game,
                    name=card_name,
                    index=war_data["index"],
                    land_strength=war_data["land_strength"],
                    fleet_support=war_data["fleet_support"],
                    naval_strength=war_data["naval_strength"],
                    disaster_numbers=war_data["disaster_numbers"],
                    standoff_numbers=war_data["standoff_numbers"],
                    spoils=war_data["spoils"],
                    famine=war_data["famine"],
                    location=war_data["location"],
                )
                if "series_name" in war_data:
                    war.series_name = war_data["series_name"]
                if war_data["immediately_active"]:
                    war.status = War.Status.ACTIVE
                else:
                    war.status = War.Status.INACTIVE

                new_war_message = f"{current_faction.display_name} drew the {war.name}."
                matching_war_messages = []

                inactive_leaders = list(
                    EnemyLeader.objects.filter(
                        game=game_id, series_name=war.series_name, active=False
                    )
                )
                if bool(inactive_leaders):
                    for leader in inactive_leaders:
                        leader.active = True
                        leader.save()
                    leaders_text = format_list([l.name for l in inactive_leaders])
                    if war.status == War.Status.ACTIVE:
                        new_war_message = f"{new_war_message[:-1]}, which is immediately active. The war is joined by {leaders_text}."
                    else:
                        war.status = War.Status.ACTIVE
                        new_war_message = f"{new_war_message[:-1]}, which is activated and joined by {leaders_text}."
                else:
                    # Handle matching wars
                    for matching_war in War.objects.filter(
                        game=game_id, series_name=war.series_name
                    ).order_by("index"):
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

            elif prefix == "leader":
                # Enemy leader drawn
                enemy_leaders_dict = load_enemy_leaders()
                leader_data = enemy_leaders_dict[card_name]
                series_name = leader_data["series_name"]

                # Check for matching wars
                matching_wars = list(
                    War.objects.filter(
                        game=game_id,
                        series_name=series_name,
                        status__in=[War.Status.INACTIVE, War.Status.ACTIVE],
                    ).order_by("index")
                )

                enemy_leader = EnemyLeader.objects.create(
                    game=game,
                    name=card_name,
                    series_name=series_name,
                    strength=leader_data["strength"],
                    disaster_number=leader_data["disaster_number"],
                    standoff_number=leader_data["standoff_number"],
                    active=bool(matching_wars),
                )

                # Handle matching wars
                if matching_wars:
                    wars_name = (
                        matching_wars[0].name
                        if len(matching_wars) == 1
                        else (matching_wars[0].series_name or "") + " Wars"
                    )
                    Log.create_object(
                        game_id,
                        f"{current_faction.display_name} drew {enemy_leader.name}, who joined the {wars_name}.",
                    )
                    for war in matching_wars:
                        if war.status == War.Status.INACTIVE:
                            war.status = War.Status.ACTIVE
                            war.save()
                            Log.create_object(
                                game_id,
                                f"The {war.name} has been activated by {enemy_leader.name}.",
                            )
                else:
                    Log.create_object(
                        game_id,
                        f"{current_faction.display_name} drew {enemy_leader.name}.",
                    )

            elif prefix == "senator":
                # New senator drawn
                senator_code = card_name
                senators_dict = load_senators()
                senator_entry = next(
                    (
                        (name, data)
                        for name, data in senators_dict.items()
                        if str(data["code"]) == senator_code
                    ),
                    None,
                )
                if senator_entry:
                    senator_name, senator_data = senator_entry
                    matching_statesman = next(
                        (
                            s
                            for s in Senator.objects.filter(
                                game=game_id, alive=True, family=False
                            )
                            if get_senator_codes(s.code)[0] == senator_code
                        ),
                        None,
                    )
                    if matching_statesman:
                        matching_statesman.family = True
                        matching_statesman.save()
                        Log.create_object(
                            game_id,
                            f"{current_faction.display_name} drew the {senator_name} senator. {matching_statesman.display_name} now has family support.",
                        )
                    else:
                        Senator.objects.create(
                            game_id=game_id,
                            faction=None,
                            family_name=senator_name,
                            family=True,
                            code=senator_code,
                            military=senator_data["military"],
                            oratory=senator_data["oratory"],
                            loyalty=senator_data["loyalty"],
                            influence=senator_data["influence"],
                        )
                        Log.create_object(
                            game_id,
                            f"{current_faction.display_name} drew {senator_name}, who entered play as an unaligned senator.",
                        )

            elif prefix == "era ends":
                game.era_ends = True
                Log.create_object(
                    game_id,
                    f"{current_faction.display_name} drew the era ends card. At the end of this forum phase, the faction with the most influence wins.",
                )

            else:
                # Card moves to faction hand
                current_faction.cards.append(next_card)
                current_faction.save()

                message = (
                    f"{current_faction.display_name} gets to keep the card they drew."
                )
                Log.create_object(game_id, message)

        # Progress game
        game.sub_phase = Game.SubPhase.ATTRACT_KNIGHT
        game.save()

        return True
