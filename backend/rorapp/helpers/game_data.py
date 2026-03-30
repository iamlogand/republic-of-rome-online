import json
import os
from django.conf import settings


def load_statesmen() -> dict:
    path = os.path.join(settings.BASE_DIR, "rorapp", "data", "statesman.json")
    with open(path, "r") as f:
        return json.load(f)


def load_senators() -> dict:
    path = os.path.join(settings.BASE_DIR, "rorapp", "data", "senator.json")
    with open(path, "r") as f:
        return json.load(f)


def load_enemy_leaders() -> dict:
    path = os.path.join(settings.BASE_DIR, "rorapp", "data", "enemy_leader.json")
    with open(path, "r") as f:
        return json.load(f)


def get_senator_codes(statesman_code: str) -> tuple[str, str]:
    family_code = statesman_code.rstrip("abcdefghijklmnopqrstuvwxyz")
    statesman_letter = statesman_code[len(family_code) :]
    return family_code, statesman_letter
