from typing import Any, Dict, Iterable, List, Optional

from rorapp.classes.random_resolver import RandomResolver
from rorapp.helpers.assassination_proposal_consequences import (
    handle_proposal_consequences,
)
from rorapp.helpers.clear_proposal_state import clear_proposal_state
from rorapp.helpers.game_data import get_senator_codes
from rorapp.helpers.kill_senator import CauseOfDeath, kill_senator
from rorapp.helpers.resume_interrupted_sub_phase import resume_interrupted_sub_phase
from rorapp.helpers.suspended_proposal import (
    resume_proposal,
    stashed_status_items,
    suspend_proposal,
)
from rorapp.helpers.text import pluralize, possessive
from rorapp.helpers.transfer_presiding_magistrate import (
    transfer_presiding_magistrate_to_hrao,
)
from rorapp.models import Faction, Game, Log, Senator

PROSECUTION_REASON = "the attempted assassination of "


def special_major_prosecution_proposal(accused_name: str, target_name: str) -> str:
    return f"Prosecute {accused_name} for {PROSECUTION_REASON}{target_name}"


def punish_caught_assassin(
    game_id: int,
    assassin: Senator,
    target_name: str,
    target_popularity: int,
    random_resolver: RandomResolver,
) -> bool:
    """
    Apply the punishment for a caught assassin (1.09.74). Returns True if a
    special major prosecution was opened, in which case the interrupted
    sub-phase must not be resumed until it has been resolved.
    """

    faction_id = assassin.faction_id
    deaths = [death_record(game_id, assassin)]

    # A caught assassin who is his own faction leader is killed automatically and
    # there is no special major prosecution (1.09.74)
    if assassin.has_title(Senator.Title.FACTION_LEADER):
        kill_senator(assassin, CauseOfDeath.EXECUTION, leave_heir=False)
        log_no_heir(game_id, assassin)
        deaths += implicate_faction_members(
            game_id, faction_id, target_popularity, random_resolver
        )
        _apply_proposal_consequences(game_id, deaths)
        return False

    kill_senator(assassin, CauseOfDeath.EXECUTION)
    _apply_proposal_consequences(game_id, deaths)

    faction_leader = next(
        (
            s
            for s in Senator.objects.filter(
                game=game_id, faction=faction_id, alive=True
            )
            if s.has_title(Senator.Title.FACTION_LEADER)
        ),
        None,
    )
    if faction_leader is None:
        return False

    influence_lost = min(5, faction_leader.influence)
    faction_leader.influence -= influence_lost
    faction_leader.save()
    if influence_lost > 0:
        Log.create_object(
            game_id,
            f"{faction_leader.display_name} lost {influence_lost} influence for the crime of his faction member.",
        )

    # Only a faction leader in Rome faces the prosecution (1.09.74)
    if faction_leader.location != "Rome":
        return False

    _open_special_major_prosecution(
        game_id, faction_leader, target_name, target_popularity
    )
    return True


def implicate_faction_members(
    game_id: int,
    faction_id: Optional[int],
    target_popularity: int,
    random_resolver: RandomResolver,
) -> List[Dict[str, Any]]:
    """
    Draw mortality chits equal to the assassination target's popularity and kill
    the members of the assassin's faction in Rome that they implicate (1.09.74).
    """

    if target_popularity <= 0 or faction_id is None:
        return []

    faction = Faction.objects.get(game=game_id, id=faction_id)
    Log.create_object(
        game_id,
        f"The senate hunted for accomplices in {faction.display_name}.",
    )

    chits = set(random_resolver.draw_mortality_chits(target_popularity))
    deaths = []
    for senator in Senator.objects.filter(
        game=game_id, faction=faction_id, alive=True, location="Rome"
    ):
        family_code, _ = get_senator_codes(senator.code)
        if family_code in chits:
            deaths.append(death_record(game_id, senator))
            kill_senator(senator, CauseOfDeath.EXECUTION)

    if not deaths:
        Log.create_object(game_id, "No accomplices were implicated.")

    return deaths


def convict(
    game_id: int, accused: Senator, random_resolver: RandomResolver
) -> List[Dict[str, Any]]:
    """Kill a convicted faction leader and hunt down his accomplices (1.09.74)."""

    game = Game.objects.get(id=game_id)
    faction_id = accused.faction_id
    deaths = [death_record(game_id, accused)]
    kill_senator(accused, CauseOfDeath.EXECUTION, leave_heir=False)
    log_no_heir(game_id, accused)
    return deaths + implicate_faction_members(
        game_id, faction_id, game.assassination_target_popularity, random_resolver
    )


def conclude_special_major_prosecution(
    game_id: int, deaths: List[Dict[str, Any]]
) -> None:
    """Put the suspended proposal back on the floor and resume the senate."""

    dead_senator_ids = [death["senator"].id for death in deaths]
    clear_proposal_state(game_id)
    _restore_presiding_magistrate(game_id, dead_senator_ids)
    resume_proposal(game_id, dead_senator_ids)
    _apply_proposal_consequences(game_id, deaths)
    resume_interrupted_sub_phase(game_id)


def _apply_proposal_consequences(game_id: int, deaths: List[Dict[str, Any]]) -> None:
    game = Game.objects.get(id=game_id)
    for death in deaths:
        handle_proposal_consequences(
            game, death["senator"], death["named_in_proposal"], death["was_censor"]
        )
        game.refresh_from_db()


def _open_special_major_prosecution(
    game_id: int, accused: Senator, target_name: str, target_popularity: int
) -> None:

    suspend_proposal(game_id)

    game = Game.objects.get(id=game_id)
    game.sub_phase = Game.SubPhase.SPECIAL_MAJOR_PROSECUTION
    game.assassination_target_popularity = target_popularity
    game.current_proposal = special_major_prosecution_proposal(
        accused.display_name, target_name
    )
    game.votes_nay = accused.influence
    game.save()

    accused.refresh_from_db()
    accused.add_status_item(Senator.StatusItem.ACCUSED)
    accused.save()

    Log.create_object(
        game_id,
        f"{accused.display_name} was put on trial for {PROSECUTION_REASON}{target_name}.",
    )
    if accused.influence > 0:
        Log.create_object(
            game_id,
            f"{possessive(accused.display_name)} influence adds {pluralize(accused.influence, 'vote')} against the conviction.",
        )

    _install_censor_as_presiding_magistrate(game_id)


def censor_in_rome(game_id: int) -> Optional[Senator]:
    """
    The Censor, if he is in Rome. Only a Censor in Rome can preside over a
    special major prosecution or be reached by the mob (1.09.74, 1.09.421).
    """

    return next(
        (
            s
            for s in Senator.objects.filter(game=game_id, alive=True)
            if s.has_title(Senator.Title.CENSOR) and s.location == "Rome"
        ),
        None,
    )


def _install_censor_as_presiding_magistrate(game_id: int) -> None:
    """
    The Censor presides over a special major prosecution, even when he is the
    accused. Without a Censor the current presiding magistrate runs it (1.09.74).
    """

    censor = censor_in_rome(game_id)
    if censor is None or censor.has_title(Senator.Title.PRESIDING_MAGISTRATE):
        return

    senators = list(Senator.objects.filter(game=game_id, alive=True))

    for senator in senators:
        if senator.has_title(Senator.Title.PRESIDING_MAGISTRATE):
            senator.remove_title(Senator.Title.PRESIDING_MAGISTRATE)
            senator.save()

    censor.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    censor.save()
    Log.create_object(
        game_id,
        f"{censor.display_name} took over as presiding magistrate for the prosecution.",
    )


def _restore_presiding_magistrate(
    game_id: int, dead_senator_ids: Iterable[int] = ()
) -> None:

    game = Game.objects.get(id=game_id)
    previous_id = (game.suspended_proposal or {}).get("presiding_magistrate_id")
    dead = set(dead_senator_ids)
    senators = list(Senator.objects.filter(game=game_id, alive=True))
    current = next(
        (s for s in senators if s.has_title(Senator.Title.PRESIDING_MAGISTRATE)), None
    )
    previous = next(
        (
            s
            for s in senators
            if s.id == previous_id and s.id not in dead and s.location == "Rome"
        ),
        None,
    )

    # The Censor only holds the meeting for the trial (1.09.74), so when the
    # magistrate he took it from is gone it passes to the HRAO instead
    if previous is None:
        if current is not None and not current.has_title(Senator.Title.HRAO):
            transfer_presiding_magistrate_to_hrao(game_id)
        return

    if current is None or previous.id == current.id:
        return

    current.remove_title(Senator.Title.PRESIDING_MAGISTRATE)
    current.save()
    previous.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    previous.save()
    Log.create_object(
        game_id,
        f"{previous.display_name} resumed as presiding magistrate.",
    )


def death_record(game_id: int, senator: Senator) -> Dict[str, Any]:
    game = Game.objects.get(id=game_id)
    return {
        "senator": senator,
        "named_in_proposal": senator.has_status_item(
            Senator.StatusItem.NAMED_IN_PROPOSAL
        )
        or Senator.StatusItem.NAMED_IN_PROPOSAL.value
        in stashed_status_items(game, senator.id),
        "was_censor": senator.has_title(Senator.Title.CENSOR),
    }


def log_no_heir(game_id: int, senator: Senator) -> None:
    Log.create_object(
        game_id,
        f"The {senator.family_name} family was left without an heir.",
    )
