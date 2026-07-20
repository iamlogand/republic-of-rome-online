import json
import os

from django.conf import settings
from django.utils.timezone import now

from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.send_game_state import send_game_state
from rorapp.helpers.provinces import province_static_fields
from rorapp.models import Faction, Game, Legion, Province, Senator, War

PRESETS_DIR = os.path.join(settings.BASE_DIR, "rorapp", "data", "presets")


def _load_preset_file(name: str) -> dict:
    path = os.path.join(PRESETS_DIR, f"{name}.json")
    with open(path) as f:
        return json.load(f)


def resolve_preset(name: str) -> dict:
    data = _load_preset_file(name)
    if "extends" not in data:
        return data
    base = resolve_preset(data["extends"])
    merged = {**base}
    for key, value in data.items():
        if key == "extends":
            continue
        if key == "game" and "game" in base:
            merged["game"] = {**base["game"], **value}
        elif key == "senators" and "senators" in base:
            base_senators = {s["code"]: s for s in base["senators"]}
            for s in value:
                code = s["code"]
                base_senators[code] = {**base_senators[code], **s} if code in base_senators else s
            merged["senators"] = list(base_senators.values())
        else:
            merged[key] = value
    return merged


def list_presets() -> list[dict]:
    presets = []
    for filename in sorted(os.listdir(PRESETS_DIR)):
        if not filename.endswith(".json"):
            continue
        name = filename[:-5]
        data = _load_preset_file(name)
        if "label" in data:
            presets.append({"name": name, "label": data["label"]})
    return presets


def load_preset(game: Game, preset_data: dict) -> None:
    factions = {f.position: f for f in Faction.objects.filter(game=game)}

    game_fields = preset_data["game"]
    game.phase = game_fields["phase"]
    game.sub_phase = game_fields.get("sub_phase", Game.SubPhase.START)
    game.turn = game_fields.get("turn", 1)
    game.step = game_fields.get("step", 1)
    game.state_treasury = game_fields.get("state_treasury", 100)
    game.unrest = game_fields.get("unrest", 0)
    game.deck = game_fields.get("deck", [])
    game.started_on = now()
    game.save()

    for f in preset_data.get("factions", []):
        faction = factions.get(f["position"])
        if faction is None:
            continue
        faction.clear_status_items()
        for item_name in f.get("status_items", []):
            faction.add_status_item(FactionStatusItem[item_name])
        faction.save()

    for s in preset_data.get("senators", []):
        senator = Senator.objects.create(
            family_name=s["family_name"],
            game=game,
            code=str(s["code"]),
            faction=factions.get(s["faction_position"]),
            military=s["military"],
            oratory=s["oratory"],
            loyalty=s["loyalty"],
            influence=s["influence"],
            knights=s.get("knights", 0),
        )
        for title_name in s.get("titles", []):
            senator.add_title(Senator.Title[title_name])
        senator.save()

    for w in preset_data.get("wars", []):
        war = War(
            game=game,
            name=w["name"],
            index=w["index"],
            land_strength=w["land_strength"],
            fleet_support=w["fleet_support"],
            naval_strength=w["naval_strength"],
            disaster_numbers=w["disaster_numbers"],
            standoff_numbers=w["standoff_numbers"],
            spoils=w["spoils"],
            famine=w["famine"],
            location=w["location"],
            status=w["status"],
        )
        if "series_name" in w:
            war.series_name = w["series_name"]
        war.save()

    for num in preset_data.get("legions", []):
        Legion.objects.create(game=game, number=num)

    for p in preset_data.get("provinces", []):
        Province.objects.create(
            game=game,
            name=p["name"],
            developed=p["developed"],
            **province_static_fields(p["name"]),
        )

    execute_effects_and_manage_actions(game.id)
    send_game_state(game.id)
