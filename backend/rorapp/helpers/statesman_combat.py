import math
from rorapp.models import Senator

# Statesman code → war series whose disasters/standoffs are nullified
_SERIES_NULLIFIERS = {"1a": "Punic", "18a": "Macedonian", "19a": "Macedonian"}

# Statesman codes that halve combat losses
_LOSS_HALVERS = {"2a"}


def check_disaster_standoff_nullified(game_id: int, war_series_name: str | None) -> bool:
    """Returns True if any statesman in this game nullifies disasters/standoffs for the war's series."""
    if not war_series_name:
        return False
    statesmen = Senator.objects.filter(game=game_id, alive=True).exclude(statesman_name=None)
    return any(_SERIES_NULLIFIERS.get(s.code) == war_series_name for s in statesmen)
    # TODO: should return False if war has an active Enemy Leader (deferred)


def apply_fabius_loss_halving(
    game_id: int, fleet_losses: int, legion_losses: int
) -> tuple[int, int]:
    """Halves losses (rounded up) if Fabius Maximus is alive in this game."""
    statesmen = Senator.objects.filter(game=game_id, alive=True).exclude(statesman_name=None)
    if any(s.code in _LOSS_HALVERS for s in statesmen):
        # TODO: halving should not apply if Fabius holds Master of Horse title (deferred)
        return math.ceil(fleet_losses / 2), math.ceil(legion_losses / 2)
    return fleet_losses, legion_losses
