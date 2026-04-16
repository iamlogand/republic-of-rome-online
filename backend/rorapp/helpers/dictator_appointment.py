from rorapp.helpers.hrao import set_hrao
from rorapp.models import Game, Log, Senator


def appoint_dictator(game_id: int, senator_id: int) -> bool:
    game = Game.objects.get(id=game_id)
    senators = list(Senator.objects.filter(game=game_id, alive=True))

    for s in senators:
        if s.has_title(Senator.Title.PRESIDING_MAGISTRATE):
            s.remove_title(Senator.Title.PRESIDING_MAGISTRATE)
            s.save()

    dictator = Senator.objects.get(id=senator_id)
    dictator.add_title(Senator.Title.DICTATOR)
    dictator.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    dictator.influence += 7
    dictator.save()

    if dictator.faction:
        Log.create_object(
            game_id,
            f"{dictator.display_name} of {dictator.faction.display_name} was appointed Dictator. He gained 7 influence.",
        )

    set_hrao(game_id, log_presiding_magistrate=True)

    game.sub_phase = Game.SubPhase.MASTER_OF_HORSE_APPOINTMENT
    game.clear_defeated_proposals()
    game.save()
    return True
