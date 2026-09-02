from typing import Any, Dict, Iterable, List

from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.models import Faction, Game, Senator

# Cleared once a turn rather than with the proposal (1.09.7), so a suspension
# must not hand a faction back its attempt or its immunity
_TURN_SCOPED_FACTION_STATUS_ITEMS = [
    FactionStatusItem.ATTEMPTED_ASSASSINATION.value,
    FactionStatusItem.ASSASSINATION_TARGETED.value,
]


def suspend_proposal(game_id: int) -> None:
    """
    Stash the business on the senate floor so that an interrupting vote can be
    held with a clean slate. A special major prosecution only temporarily
    suspends the current proposal (1.09.74).
    """

    game = Game.objects.get(id=game_id)
    factions = list(Faction.objects.filter(game=game_id))
    senators = list(Senator.objects.filter(game=game_id))
    presiding_magistrate = next(
        (s for s in senators if s.has_title(Senator.Title.PRESIDING_MAGISTRATE)), None
    )

    game.suspended_proposal = {
        "current_proposal": game.current_proposal,
        "votes_yea": game.votes_yea,
        "votes_nay": game.votes_nay,
        "presiding_magistrate_id": (
            presiding_magistrate.id if presiding_magistrate else None
        ),
        "factions": {str(f.id): _stashed(f.status_items) for f in factions},
        "senators": {str(s.id): list(s.status_items) for s in senators},
        "deaths": [],
    }
    game.current_proposal = None
    game.votes_yea = 0
    game.votes_nay = 0
    game.save()

    for faction in factions:
        faction.status_items = _turn_scoped(faction.status_items)
    Faction.objects.bulk_update(factions, ["status_items"])

    for senator in senators:
        senator.status_items = []
    Senator.objects.bulk_update(senators, ["status_items"])


def record_suspended_deaths(game_id: int, deaths: List[Dict[str, Any]]) -> bool:
    """
    Note senators killed while the proposal is suspended, so that the roles they
    held in it can be settled when it returns. Returns False if nothing is
    suspended, in which case the caller must settle them now.
    """

    game = Game.objects.get(id=game_id)
    stash = game.suspended_proposal
    if not stash:
        return False
    stash["deaths"] = stash.get("deaths", []) + list(deaths)
    game.suspended_proposal = stash
    game.save()
    return True


def suspended_deaths(game_id: int) -> List[Dict[str, Any]]:
    game = Game.objects.get(id=game_id)
    return (game.suspended_proposal or {}).get("deaths", [])


def resume_proposal(game_id: int, skip_senator_ids: Iterable[int] = ()) -> None:
    """
    Put the stashed business back on the floor.

    Senators in skip_senator_ids keep the status items they have now. A faction
    leader who died during the suspension is still alive as his heir, and the
    heir must not inherit his predecessor's role in the proposal.
    """

    game = Game.objects.get(id=game_id)
    stash: Dict[str, Any] = game.suspended_proposal or {}

    game.current_proposal = stash.get("current_proposal")
    game.votes_yea = stash.get("votes_yea", 0)
    game.votes_nay = stash.get("votes_nay", 0)
    game.suspended_proposal = {}
    game.save()

    faction_statuses = stash.get("factions", {})
    factions = list(Faction.objects.filter(game=game_id))
    for faction in factions:
        faction.status_items = list(
            faction_statuses.get(str(faction.id), [])
        ) + _turn_scoped(faction.status_items)
    Faction.objects.bulk_update(factions, ["status_items"])

    senator_statuses = stash.get("senators", {})
    skipped = set(skip_senator_ids)
    senators = [
        s
        for s in Senator.objects.filter(game=game_id, alive=True)
        if s.id not in skipped
    ]
    for senator in senators:
        senator.status_items = list(senator_statuses.get(str(senator.id), []))
    Senator.objects.bulk_update(senators, ["status_items"])


def _stashed(status_items: List[str]) -> List[str]:
    return [i for i in status_items if i not in _TURN_SCOPED_FACTION_STATUS_ITEMS]


def _turn_scoped(status_items: List[str]) -> List[str]:
    return [i for i in status_items if i in _TURN_SCOPED_FACTION_STATUS_ITEMS]
