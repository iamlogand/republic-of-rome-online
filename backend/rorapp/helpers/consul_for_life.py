from typing import List, Optional

from rorapp.models import Game, Log, Senator

CONSUL_FOR_LIFE_PREFIX = "Elect Consul for Life "

ELECTION_INFLUENCE_REQUIRED = 21
APPOINTMENT_INFLUENCE_REQUIRED = 35


def _is_eligible(senator: Senator) -> bool:
    return bool(senator.alive and senator.location == "Rome" and senator.faction)


def get_eligible_consul_for_life_candidates(senators) -> List[Senator]:
    return [
        s
        for s in senators
        if _is_eligible(s) and s.influence >= ELECTION_INFLUENCE_REQUIRED
    ]


def get_consul_for_life_appointee(senators) -> Optional[Senator]:
    candidates = [
        s
        for s in senators
        if _is_eligible(s) and s.influence >= APPOINTMENT_INFLUENCE_REQUIRED
    ]
    if not candidates:
        return None

    faction_influence: dict[int, int] = {}
    for senator in senators:
        if senator.alive and senator.faction:
            faction_influence[senator.faction.id] = (
                faction_influence.get(senator.faction.id, 0) + senator.influence
            )

    return sorted(
        candidates,
        key=lambda s: (-s.influence, -faction_influence[s.faction.id], s.code),
    )[0]


def get_consul_for_life(senators) -> Optional[Senator]:
    return next(
        (
            s
            for s in senators
            if s.alive and s.has_title(Senator.Title.CONSUL_FOR_LIFE)
        ),
        None,
    )


# The nominee adds his influence to his own vote total (1.09.821)
def consul_for_life_vote_bonus(senator: Senator, proposal: Optional[str]) -> int:
    if (
        proposal
        and proposal.startswith(CONSUL_FOR_LIFE_PREFIX)
        and senator.has_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    ):
        return senator.influence
    return 0


def grant_consul_for_life(game_id: int, senator_id: int, appointed: bool) -> None:
    # An appointment supersedes an election made in the same turn (1.09.822)
    previous_holders = Senator.objects.filter(
        game=game_id, titles__contains=[Senator.Title.CONSUL_FOR_LIFE.value]
    )
    for previous_holder in previous_holders:
        if previous_holder.id != senator_id:
            previous_holder.remove_title(Senator.Title.CONSUL_FOR_LIFE)
            previous_holder.save()

    # Consul for Life is not an office, so it grants no influence and does not
    # affect the HRAO or presiding magistrate (1.09.823)
    senator = Senator.objects.get(id=senator_id)
    senator.add_title(Senator.Title.CONSUL_FOR_LIFE)
    senator.save()

    if appointed:
        game = Game.objects.get(id=game_id)
        game.consul_for_life_appointed = True
        game.save()

    if senator.faction:
        if appointed:
            text = (
                f"{senator.display_name} of {senator.faction.display_name} reached "
                f"{senator.influence} influence and became Consul for Life."
            )
        else:
            text = (
                f"{senator.display_name} of {senator.faction.display_name} was "
                f"elected Consul for Life."
            )
        Log.create_object(game_id, text)
