from typing import Optional
from rorapp.helpers.game_data import get_senator_codes
from rorapp.models import Faction, Game, Log, Senator


def highest_ranking_senator(
    senators: list[Senator],
    exclude_stepped_down: bool = False,
) -> Optional[Senator]:
    major_offices = [
        Senator.Title.DICTATOR,
        Senator.Title.ROME_CONSUL,
        Senator.Title.FIELD_CONSUL,
        Senator.Title.PROCONSUL,
        Senator.Title.CENSOR,
    ]

    candidates = [
        s
        for s in senators
        if not exclude_stepped_down
        or not s.has_status_item(Senator.StatusItem.STEPPED_DOWN)
    ]
    if not candidates:
        return None

    def sort_key(s: Senator):
        office_rank = len(major_offices)
        for rank, office in enumerate(major_offices):
            if s.has_title(office):
                office_rank = rank
                break
        family_code, statesman_letter = get_senator_codes(s.code)
        return (
            office_rank,
            -s.influence,
            -s.oratory,
            int(family_code),
            statesman_letter,
        )

    return sorted(candidates, key=sort_key)[0]


def set_hrao(game_id: int, log_presiding_magistrate: bool = False) -> None:

    game = Game.objects.get(id=game_id)
    senators = list(
        Senator.objects.filter(
            game=game_id, faction__isnull=False, alive=True, location="Rome"
        )
    )

    selected_hrao = highest_ranking_senator(senators)
    if not selected_hrao:
        return

    previous_hraos = Senator.objects.filter(
        game=game_id, titles__contains=[Senator.Title.HRAO.value]
    )
    for previous_hrao in previous_hraos:
        if previous_hrao == selected_hrao:
            return
        previous_hrao.remove_title(Senator.Title.HRAO)
        previous_hrao.save()

    selected_hrao.add_title(Senator.Title.HRAO)
    selected_hrao.save()

    if selected_hrao.faction:
        faction = Faction.objects.get(game=game_id, id=selected_hrao.faction.id)
        message = f"{selected_hrao.display_name} of {faction.display_name} became HRAO"
        message += " and presiding magistrate." if log_presiding_magistrate else "."
        Log.create_object(
            game.id,
            message,
        )
