from rorapp.helpers.clear_proposal_state import clear_proposal_state
from rorapp.helpers.end_prosecutions import end_prosecutions
from rorapp.models import Game


def finish_prosecution(game_id: int, is_major: bool, guilty: bool) -> None:
    game = Game.objects.get(id=game_id)
    if is_major:
        game.prosecutions_remaining = 0
    else:
        game.prosecutions_remaining = max(0, game.prosecutions_remaining - 1)
    game.save()

    clear_proposal_state(game_id)

    game = Game.objects.get(id=game_id)
    if game.prosecutions_remaining == 0:
        end_prosecutions(game_id)
