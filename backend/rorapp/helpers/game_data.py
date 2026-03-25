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
