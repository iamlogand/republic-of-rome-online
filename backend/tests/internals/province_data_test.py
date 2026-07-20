import json
import sys
from pathlib import Path

import pytest
from django.conf import settings

from rorapp.helpers.game_data import load_provinces

REPO_ROOT = Path(settings.BASE_DIR).parent
if not (REPO_ROOT / "game-data").exists():
    REPO_ROOT = Path("/repo")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from rorcli.parsers.provinces import parse_provinces
from rorcli.parsers.wars import parse_wars


def _normalize_dice_expression(value):
    if isinstance(value, str):
        return value.replace("\u2212", "-")
    return value


def _normalize_stats(stats: dict) -> dict:
    return {key: _normalize_dice_expression(val) for key, val in stats.items()}


def _known_war_names() -> set[str]:
    war_json_path = Path(settings.BASE_DIR) / "rorapp" / "data" / "war.json"
    with open(war_json_path, "r") as file:
        war_json = json.load(file)
    wars_md_path = REPO_ROOT / "game-data" / "components" / "wars.md"
    parsed_wars = parse_wars(wars_md_path)
    return set(war_json.keys()) | {war["name"] for war in parsed_wars.values()}


def _known_war_series() -> set[str]:
    war_json_path = Path(settings.BASE_DIR) / "rorapp" / "data" / "war.json"
    with open(war_json_path, "r") as file:
        war_json = json.load(file)
    series = {
        war_data["series_name"]
        for war_data in war_json.values()
        if war_data.get("series_name")
    }
    wars_md_path = REPO_ROOT / "game-data" / "components" / "wars.md"
    for war in parse_wars(wars_md_path).values():
        raw_series = war.get("series")
        if raw_series:
            series.add(raw_series.split()[0])
    return series


def test_province_json_matches_parsed_provinces_md():
    # Arrange
    provinces_md_path = REPO_ROOT / "game-data" / "components" / "provinces.md"
    parsed_by_name = {
        province["name"]: province
        for province in parse_provinces(provinces_md_path).values()
    }
    loaded = load_provinces()

    # Act
    # Assert
    assert set(loaded.keys()) == set(parsed_by_name.keys())
    for name, loaded_province in loaded.items():
        parsed_province = parsed_by_name[name]
        assert loaded_province["name"] == parsed_province["name"]
        assert _normalize_stats(loaded_province["undeveloped"]) == _normalize_stats(
            parsed_province["undeveloped"]
        )
        assert _normalize_stats(loaded_province["developed"]) == _normalize_stats(
            parsed_province["developed"]
        )
        assert loaded_province.get("frontier", False) == parsed_province.get(
            "frontier", False
        )
        assert loaded_province["created_by"] == parsed_province["created_by"]


def test_province_defends_reference_known_wars():
    # Arrange
    known_war_names = _known_war_names()
    known_war_series = _known_war_series()
    loaded = load_provinces()

    # Act
    # Assert
    for name, province in loaded.items():
        defends = province["defends"]
        assert set(defends.keys()) == {"war_names", "war_series"}, name
        for war_name in defends["war_names"]:
            assert war_name in known_war_names, f"{name}: unknown war name {war_name}"
        for war_series in defends["war_series"]:
            assert war_series in known_war_series, (
                f"{name}: unknown war series {war_series}"
            )
        assert defends["war_names"] or defends["war_series"], name
