from typing import Optional
from rorapp.models import Senator


def extract_master_of_horse(remainder_after_name: str, senators) -> Optional[Senator]:
    """If remainder starts with ' and {senator display name}', return that senator."""
    if remainder_after_name.startswith(" and "):
        name_and_more = remainder_after_name[len(" and "):]
        return next(
            (s for s in senators if name_and_more.startswith(s.display_name)),
            None,
        )
    return None
