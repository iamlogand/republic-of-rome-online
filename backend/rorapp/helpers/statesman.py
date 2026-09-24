from typing import Iterable, Optional

from rorapp.helpers.game_data import get_senator_codes
from rorapp.models import Senator


def statesman_in_play(
    senators: Iterable[Senator], family_code: str
) -> Optional[Senator]:
    return next(
        (
            senator
            for senator in senators
            if senator.alive
            and not senator.family
            and get_senator_codes(senator.code)[0] == family_code
        ),
        None,
    )
