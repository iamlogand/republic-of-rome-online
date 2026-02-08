import re
from typing import Optional, Tuple
from rorapp.models import Faction, Game, Log, Senator


def set_hrao(game_id) -> None:

    game = Game.objects.get(id=game_id)
    senators = Senator.objects.filter(game=game_id, faction__isnull=False, alive=True, location="Rome")

    selected_hrao: Optional[Senator] = None
    major_offices = [Senator.Title.ROME_CONSUL]
    for office in major_offices:
        if selected_hrao:
            break
        for senator in senators:
            if senator.has_title(office):
                selected_hrao = senator
                break

    def sort_key(senator: Senator) -> Tuple[int, int, int, str]:
        match = re.match(r"(\d+)([A-Z]?)", senator.code)
        if match:
            code_number = int(match.group(1))
            code_letter = match.group(2) or ""
            return (-senator.influence, -senator.oratory, code_number, code_letter)
        raise ValueError(f"Invalid senator code: {senator.code}")

    if not selected_hrao:
        selected_hrao = sorted(list(senators), key=sort_key)[0]

    # Remove HRAO title from any previous HRAO
    previous_hraos = Senator.objects.filter(game=game_id, titles__contains=[Senator.Title.HRAO.value])
    for previous_hrao in previous_hraos:
        if previous_hrao == selected_hrao:
            return  # No change
        previous_hrao.remove_title(Senator.Title.HRAO)
        previous_hrao.save()

    selected_hrao.add_title(Senator.Title.HRAO)
    selected_hrao.save()

    if selected_hrao.faction:  # This should always be true
        faction = Faction.objects.get(game=game_id, id=selected_hrao.faction.id)
        Log.create_object(
            game_id=game.id,
            text=f"{selected_hrao.display_name} of {faction.display_name} is the new HRAO.",
        )
