from typing import Optional
from rorapp.helpers.hrao import set_hrao
from rorapp.models import Game, Log, Senator


def close_senate_on_presiding_magistrate_departure(
    game: Game, commander: Optional[Senator]
) -> None:
    if commander and commander.has_title(Senator.Title.PRESIDING_MAGISTRATE):
        for senator in Senator.objects.filter(game=game):
            if senator.has_title(Senator.Title.PRESIDING_MAGISTRATE):
                senator.remove_title(Senator.Title.PRESIDING_MAGISTRATE)
                senator.save()

        Log.create_object(
            game.id,
            f"Following the departure of {commander.display_name}, the presiding magistrate, the Senate meeting has closed.",
        )
        if commander.has_title(Senator.Title.HRAO):
            set_hrao(game.id)

        game.sub_phase = Game.SubPhase.END
