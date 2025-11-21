import json
import os
from typing import List
from django.conf import settings
from django.contrib.auth.models import User
import pytest
from django.utils.timezone import now
from rorapp.models import Game, Faction, Senator
from rorapp.classes.random_resolver import FakeRandomResolver

test_resolver = FakeRandomResolver()


@pytest.fixture
def basic_game() -> Game:
    host = User.objects.create_user(username="testuser", password="password")

    game = Game.objects.create(
        name="Test Game",
        host=host,
        step=1,
        started_on=now(),
        phase=Game.Phase.INITIAL,
        sub_phase=Game.SubPhase.FACTION_LEADER,
    )
    factions = []
    for i in range(1, 4):
        player = User.objects.create_user(username=f"player{i}", password="password")
        faction = Faction.objects.create(game=game, player=player, position=i)
        factions.append(faction)

    senator_json_path = os.path.join(
        settings.BASE_DIR, "rorapp", "data", "senator.json"
    )
    senators: List[Senator] = []
    with open(senator_json_path, "r") as file:
        senators_dict = json.load(file)

    for i, (senator_name, senator_data) in enumerate(senators_dict.items()):
        if i <= 3:
            current_faction = factions[0]
        elif i <= 6:
            current_faction = factions[1]
        elif i <= 9:
            current_faction = factions[2]
        else:
            break
        if senator_data["scenario"] == 1:
            senator = Senator.objects.create(
                name=senator_name,
                game=game,
                code=senator_data["code"],
                faction=current_faction,
                military=senator_data["military"],
                oratory=senator_data["oratory"],
                loyalty=senator_data["loyalty"],
                influence=senator_data["influence"],
            )
            senators.append(senator)
    return game
