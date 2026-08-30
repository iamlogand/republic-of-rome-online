from typing import NamedTuple, Optional

from rorapp.classes.concession import Concession
from rorapp.models import Game, Senator


class ConcessionDestruction(NamedTuple):
    destroyed: bool
    holder: Optional[Senator]


def destroy_concession(game: Game, concession: Concession) -> ConcessionDestruction:
    """Move a concession from play to the Curia (1.07.321).

    A concession is in play when a senator holds it or when it sits unawarded in
    the forum. Cards still in the deck or in a faction's hand cannot be
    destroyed, and neither can a concession that is already in the Curia.
    """

    if game.has_destroyed_concession(concession):
        return ConcessionDestruction(False, None)

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
