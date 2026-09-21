from django.db.models import F

from rorapp.classes.game_effect_item import GameEffect
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import Fleet, Game, Log, War

# Increased Rhodian involvement brings the total to 12 fleets, not 20 (1.13.2)
RHODIAN_FLEETS = {1: 8, 2: 12}


def end_rhodian_alliance(game: Game) -> None:
    count = RHODIAN_FLEETS[game.count_effect(GameEffect.RHODIAN_ALLIANCE)]
    fleets = sorted(
        Fleet.objects.filter(game=game).order_by(
            F("campaign").asc(nulls_first=True), "number"
        )[:count],
        key=lambda fleet: fleet.number,
    )
    Fleet.objects.filter(id__in=[fleet.id for fleet in fleets]).delete()
    War.objects.filter(game=game, rhodian_alliance=True).update(rhodian_alliance=False)

    game.remove_effect(GameEffect.RHODIAN_ALLIANCE)
    game.rhodian_alliance_rejectable = False
    game.save()

    if fleets:
        Log.create_object(
            game.id,
            f"Rhodes recalled {unit_list_to_string([], fleets)}, ending the alliance.",
        )
    else:
        Log.create_object(game.id, "The Rhodian alliance ended.")
