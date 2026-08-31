from typing import Any, Dict

from rorapp.models import Faction, Game, Senator


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
        "factions": {str(f.id): list(f.status_items) for f in factions},
        "senators": {str(s.id): list(s.status_items) for s in senators},
    }
    game.current_proposal = None
    game.votes_yea = 0
    game.votes_nay = 0
    game.save()

    for faction in factions:
        faction.status_items = []
    Faction.objects.bulk_update(factions, ["status_items"])

    for senator in senators:
        senator.status_items = []
    Senator.objects.bulk_update(senators, ["status_items"])


def resume_proposal(game_id: int) -> Dict[str, Any]:
    """
    Put the stashed business back on the floor and return the stash, so that
    callers can tell what a senator's role in it was before they died.
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
        faction.status_items = list(faction_statuses.get(str(faction.id), []))
    Faction.objects.bulk_update(factions, ["status_items"])

    senator_statuses = stash.get("senators", {})
    senators = list(Senator.objects.filter(game=game_id, alive=True))
    for senator in senators:
        senator.status_items = list(senator_statuses.get(str(senator.id), []))
    Senator.objects.bulk_update(senators, ["status_items"])

    return stash


def stashed_status_items(game: Game, senator_id: int) -> list:
    return (game.suspended_proposal or {}).get("senators", {}).get(str(senator_id), [])
