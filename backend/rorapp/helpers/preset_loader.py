import json
import os

from django.conf import settings
from django.utils.timezone import now

from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.send_game_state import send_game_state
from rorapp.classes.concession import Concession
from rorapp.helpers.governor_election import assign_governor
from rorapp.helpers.provinces import province_static_fields
from rorapp.models import (
    Campaign,
    EnemyLeader,
    Faction,
    Fleet,
    Game,
    Legion,
    Province,
    Senator,
    War,
)

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
                base_senators[code] = (
                    {**base_senators[code], **s} if code in base_senators else s
                )
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
    game.concessions = game_fields.get("concessions", [])
    game.storm_at_sea_fleet_losses = game_fields.get(
        "storm_at_sea_fleet_losses", 0
    )
    game.started_on = now()
    game.save()

    for f in preset_data.get("factions", []):
        faction = factions.get(f["position"])
        if faction is None:
            continue
        faction.clear_status_items()
        for item_name in f.get("status_items", []):
            faction.add_status_item(item_name)
        faction.save()

    senators_by_code: dict[str, Senator] = {}
    for s in preset_data.get("senators", []):
        faction_position = s.get("faction_position")
        faction = (
            factions.get(faction_position) if faction_position is not None else None
        )
        senator = Senator.objects.create(
            family_name=s["family_name"],
            game=game,
            code=str(s["code"]),
            faction=faction,
            military=s["military"],
            oratory=s["oratory"],
            loyalty=s["loyalty"],
            influence=s["influence"],
            knights=s.get("knights", 0),
            talents=s.get("talents", 0),
            location=s.get("location", "Rome"),
        )
        for title_name in s.get("titles", []):
            senator.add_title(Senator.Title[title_name])
        for concession_value in s.get("concessions", []):
            senator.add_concession(Concession(concession_value))
        senator.save()
        senators_by_code[str(s["code"])] = senator

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

    for l in preset_data.get("enemy_leaders", []):
        EnemyLeader.objects.create(
            game=game,
            name=l["name"],
            series_name=l["series_name"],
            strength=l["strength"],
            disaster_number=l["disaster_number"],
            standoff_number=l["standoff_number"],
            active=l.get("active", False),
        )

    for num in preset_data.get("legions", []):
        Legion.objects.create(game=game, number=num, recently_raised=False)

    for num in preset_data.get("fleets", []):
        Fleet.objects.create(game=game, number=num, recently_raised=False)

    for c in preset_data.get("campaigns", []):
        campaign_war = War.objects.get(game=game, name=c["war"])
        commander = Senator.objects.get(game=game, code=str(c["commander_code"]))
        master_of_horse = (
            Senator.objects.get(game=game, code=str(c["master_of_horse_code"]))
            if "master_of_horse_code" in c
            else None
        )
        campaign = Campaign.objects.create(
            game=game,
            war=campaign_war,
            commander=commander,
            master_of_horse=master_of_horse,
            recently_deployed=False,
        )
        location = c.get("location", campaign_war.location)
        for participant in [commander, master_of_horse]:
            if participant:
                participant.location = location
                participant.save()
        for num in c.get("legions", []):
            Legion.objects.create(
                game=game, number=num, campaign=campaign, recently_raised=False
            )
        for num in c.get("fleets", []):
            Fleet.objects.create(
                game=game, number=num, campaign=campaign, recently_raised=False
            )

    for p in preset_data.get("provinces", []):
        province = Province.objects.create(
            game=game,
            name=p["name"],
            developed=p["developed"],
            **province_static_fields(p["name"]),
        )
        governor_code = p.get("governor_code")
        if governor_code is not None:
            governor = senators_by_code.get(str(governor_code))
            if governor is None:
                raise ValueError(
                    f"Unknown governor_code '{governor_code}' for province {p['name']}"
                )
            assign_governor(province, governor)
            province.term = p.get("term", 3)
            province.elected_this_turn = p.get("elected_this_turn", False)
            province.save()

    execute_effects_and_manage_actions(game.id)
    send_game_state(game.id)
