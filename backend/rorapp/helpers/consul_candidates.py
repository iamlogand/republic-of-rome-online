from itertools import combinations
from typing import List, Tuple

from rorapp.models import Senator


def get_eligible_consul_pairs(
    senators, defeated_proposals
) -> List[Tuple[Senator, Senator]]:
    """Return every pair of senators that may still be nominated as Consuls (1.09.2)."""

    candidates = sorted(
        (
            s
            for s in senators
            if s.faction_id
            and s.alive
            and not s.has_title(Senator.Title.ROME_CONSUL)
            and not s.has_title(Senator.Title.FIELD_CONSUL)
            and not s.has_title(Senator.Title.DICTATOR)
            and not s.has_title(Senator.Title.PROCONSUL)
        ),
        key=lambda s: s.family_name,
    )
    defeated = {
        tuple(sorted(p[len("Elect consuls ") :].split(" and ")))
        for p in defeated_proposals
        if p.startswith("Elect consuls ")
    }
    return [
        pair
        for pair in combinations(candidates, 2)
        if tuple(sorted(s.display_name for s in pair)) not in defeated
    ]
