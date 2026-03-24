from rorapp.models import Game, Senator


def end_prosecutions(game_id: int) -> None:
    game = Game.objects.get(id=game_id)
    senators = list(Senator.objects.filter(game=game_id, alive=True))

    # Remove CORRUPT/MAJOR from senators in Rome (§1.09.45)
    for senator in senators:
        if senator.location == "Rome":
            senator.remove_status_item(Senator.StatusItem.CORRUPT)
            senator.remove_status_item(Senator.StatusItem.MAJOR_CORRUPT)
            senator.corrupt_concessions = []
            senator.save()

    # Return PM to Rome Consul (HRAO)
    for senator in senators:
        if senator.has_title(Senator.Title.CENSOR):
            senator.remove_title(Senator.Title.PRESIDING_MAGISTRATE)
            senator.save()
        if senator.has_title(Senator.Title.HRAO):
            senator.add_title(Senator.Title.PRESIDING_MAGISTRATE)
            senator.save()

    # Reset prosecution tracking
    game.prosecutions_remaining = 0
    game.defeated_proposals = []
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
