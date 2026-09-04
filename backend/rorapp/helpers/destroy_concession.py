from typing import NamedTuple, Optional

from rorapp.classes.concession import Concession
from rorapp.models import Game, Senator


class ConcessionDestruction(NamedTuple):
    destroyed: bool
    holder: Optional[Senator]


def destroy_concession(game: Game, concession: Concession) -> ConcessionDestruction:
    """Move a concession from play to the Curia (1.07.321).

    Only a concession held by a senator or sitting unawarded in the forum is in
    play; one still in the deck, in a faction's hand, or already in the Curia is
    left alone.
    """

    holder = next(
        (
            s
            for s in Senator.objects.filter(game=game.id, alive=True)
            if s.has_concession(concession)
        ),
        None,
    )
    if holder:
        holder.remove_concession(concession)
        holder.remove_corrupt_concession(concession)
        holder.save()
    elif game.has_concession(concession):
        game.remove_concession(concession)
    else:
        return ConcessionDestruction(False, None)

    game.add_destroyed_concession(concession)
    game.save()
    return ConcessionDestruction(True, holder)
