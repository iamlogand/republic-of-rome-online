from rorapp.helpers.game_data import load_provinces
from rorapp.models import Game, Log, Province, War

ILLYRIAN_WARS = ("1st Illyrian War", "2nd Illyrian War")
GALLIC_WARS = ("2nd Gallic War", "3rd Gallic War")

def award_provinces_for_war(game: Game, war: War) -> list[Province]:
    created: list[Province] = []
    for name, data in load_provinces().items():
        if Province.objects.filter(game=game, name=name).exists():
            continue
        if not _created_by_matches(data["created_by"], war.name):
            continue
        if not _should_award_now(game, war, data["created_by"]):
            continue

        province = Province.objects.create(
            game=game,
            name=name,
            developed=False,
        )
        created.append(province)
        Log.create_object(game.id, f"{name} was established as a province.")
    return created


def get_province_definition(name: str) -> dict:
    return load_provinces()[name]


def provinces_created_by(war_name: str) -> list[str]:
    return [
        name
        for name, data in load_provinces().items()
        if _created_by_matches(data["created_by"], war_name)
    ]


def _created_by_matches(created_by: str, war_name: str) -> bool:
    if created_by == war_name:
        return True
    if " or " in created_by:
        return any(
            _created_by_matches(part.strip(), war_name)
            for part in created_by.split(" or ")
        )
    if created_by == "2nd/3rd Gallic War":
        return war_name in GALLIC_WARS
    if created_by == "both Illyrian Wars":
        return war_name in ILLYRIAN_WARS
    return False


def _should_award_now(game: Game, war: War, created_by: str) -> bool:
    if created_by == "both Illyrian Wars":
        return _both_illyrian_wars_defeated(game, war.id)
    return True


def _both_illyrian_wars_defeated(game: Game, excluding_war_id: int) -> bool:
    return not War.objects.filter(
        game=game,
        name__in=ILLYRIAN_WARS,
    ).exclude(id=excluding_war_id).exists()
