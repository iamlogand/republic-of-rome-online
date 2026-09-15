from typing import Any, Dict, List

from rorapp.helpers.clear_proposal_state import clear_proposal_state
from rorapp.helpers.suspended_proposal import record_suspended_deaths
from rorapp.models import Game, Senator


def death_record(senator: Senator) -> Dict[str, Any]:
    """
    Capture the role a senator holds in the proposal before he dies. While a
    proposal is suspended his role is the one stashed with it (1.09.74).

    Must be called BEFORE kill_senator(), which clears all status items.
    """

    game = Game.objects.get(id=senator.game_id)
    stashed = (game.suspended_proposal or {}).get("senators", {})
    status_items = stashed.get(str(senator.id), senator.status_items)
    return {
        "senator_id": senator.id,
        "named_in_proposal": Senator.StatusItem.NAMED_IN_PROPOSAL.value in status_items,
        "was_censor": senator.has_title(Senator.Title.CENSOR),
    }


def apply_proposal_consequences(game_id: int, deaths: List[Dict[str, Any]]) -> None:
    """
    Apply the consequence of each senator killed mid-vote, based on the role he
    held in the current proposal and the interrupted sub_phase. Deaths during a
    suspension are settled when the proposal returns to the floor (1.09.74).

    The game's interrupted_sub_phase is used rather than parsing proposal strings.
    """

    if record_suspended_deaths(game_id, deaths):
        return

    game = Game.objects.get(id=game_id)
    for death in deaths:
        _settle(game, death)
        game.refresh_from_db()


def _settle(game: Game, death: Dict[str, Any]) -> None:

    sub_phase = game.interrupted_sub_phase

    # §1.09.721: If the Censor dies during the Prosecution step, the current
    # Prosecution is cancelled and no more Prosecutions are possible.
    if death["was_censor"] and sub_phase == Game.SubPhase.PROSECUTION:
        clear_proposal_state(game.id)
        game.refresh_from_db()
        game.prosecutions_remaining = 0
        game.save()
        return

    if (
        not game.current_proposal
        and game.sub_phase != Game.SubPhase.DICTATOR_APPOINTMENT
    ):
        return
    if not death["named_in_proposal"]:
        return

    if sub_phase == Game.SubPhase.PROSECUTION:
        # Cancel prosecution; it still counts toward the Censor's limit
        clear_proposal_state(game.id)
        game.refresh_from_db()
        game.prosecutions_remaining -= 1
        game.save()

    elif sub_phase in (
        Game.SubPhase.CONSULAR_ELECTION,
        Game.SubPhase.CENSOR_ELECTION,
        Game.SubPhase.DICTATOR_ELECTION,
    ):
        # Cancel proposal — PM can re-propose with a different nominee
        clear_proposal_state(game.id)

    elif sub_phase == Game.SubPhase.OTHER_BUSINESS:
        proposal = game.current_proposal or ""
        if "land bill" in proposal.lower():
            # Land Bill vote is never cancelled by the death of a named senator
            pass
        elif proposal.startswith("Award the ") and " concession to " in proposal:
            # Concession award: once per turn, cannot be re-proposed
            game.add_unavailable_proposal(proposal)
            game.save()
            clear_proposal_state(game.id)
        else:
            # Deploy forces / replace proconsul: PM can re-propose
            clear_proposal_state(game.id)
