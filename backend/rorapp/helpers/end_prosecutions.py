from rorapp.models import Game, Senator
from rorapp.models.log import Log


def end_prosecutions(game_id: int) -> None:
    game = Game.objects.get(id=game_id)
    senators = list(Senator.objects.filter(game=game_id, alive=True))

    # Remove CORRUPT/MAJOR from senators in Rome
    for senator in senators:
        if senator.location == "Rome":
            senator.remove_status_item(Senator.StatusItem.CORRUPT)
            senator.remove_status_item(Senator.StatusItem.MAJOR_CORRUPT)
            senator.clear_corrupt_concessions()
            senator.save()

    # Return PM to HRAO
    hrao = None
    for senator in senators:
        if senator.has_title(Senator.Title.CENSOR):
            senator.remove_title(Senator.Title.PRESIDING_MAGISTRATE)
            senator.save()
        if senator.has_title(Senator.Title.HRAO):
            senator.add_title(Senator.Title.PRESIDING_MAGISTRATE)
            senator.save()
            hrao = senator

    if hrao:
        Log.create_object(
            game_id,
            f"With prosecutions over, {hrao.display_name} took over as presiding magistrate.",
        )

    # Reset prosecution tracking
    game.prosecutions_remaining = 0
    game.clear_senate_sub_phase_proposals()
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
