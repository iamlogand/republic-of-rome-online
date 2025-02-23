import re
from typing import Optional, Tuple
from rorapp.models import Faction, Game, Log, Senator


def set_new_hrao(game_id) -> None:

    game = Game.objects.get(id=game_id)
    senators = Senator.objects.filter(game=game_id, faction__isnull=False, alive=True)

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

    selected_hrao.add_title(Senator.Title.HRAO)

    if selected_hrao.faction:  # This should always be true
        faction = Faction.objects.get(game=game_id, id=selected_hrao.faction.id)
        Log.objects.create(
            game=game,
            text=f"{selected_hrao.display_name} of {faction.display_name} is the new HRAO.",
        )
