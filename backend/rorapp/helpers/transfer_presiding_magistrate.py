from rorapp.models import Game, Log, Senator


def transfer_presiding_magistrate_to_hrao(game_id: int) -> None:
    """
    Transfer the PRESIDING_MAGISTRATE title from its current holder to the HRAO.
    Called when the current presiding magistrate dies and set_hrao() has already
    assigned a new HRAO.
    """
    game = Game.objects.get(id=game_id)
    senators = game.senators.filter(alive=True)

    old_pm = senators.filter(titles__contains=Senator.Title.PRESIDING_MAGISTRATE.value).first()
    if old_pm:
        old_pm.remove_title(Senator.Title.PRESIDING_MAGISTRATE)
        old_pm.save()

    new_hrao = senators.filter(titles__contains=Senator.Title.HRAO.value).first()
    if new_hrao:
        new_hrao.add_title(Senator.Title.PRESIDING_MAGISTRATE)
        new_hrao.save()
        Log.create_object(
            game_id,
            f"{new_hrao.display_name} became the new Presiding Magistrate.",
        )
