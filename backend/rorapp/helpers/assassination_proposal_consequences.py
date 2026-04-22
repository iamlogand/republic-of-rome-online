from rorapp.helpers.clear_proposal_and_votes import clear_proposal_and_votes
from rorapp.models import Game, Senator


def handle_proposal_consequences(
    game: Game, victim: Senator, was_named_in_proposal: bool
) -> None:
    """
    Apply the consequence of a senator being killed mid-vote, based on their
    role in the current proposal and the interrupted sub_phase.

    Must be called AFTER kill_senator() so the victim is already dead.
    was_named_in_proposal must be captured BEFORE kill_senator() because
    kill_senator() clears all status items.
    The game's interrupted_sub_phase is used rather than parsing proposal strings.
    """
    if (
        not game.current_proposal
        and game.sub_phase != Game.SubPhase.DICTATOR_APPOINTMENT
    ):
        return
    if not was_named_in_proposal:
        return

    sub_phase = game.interrupted_sub_phase

    if sub_phase == Game.SubPhase.PROSECUTION:
        # Cancel prosecution; it still counts toward the Censor's limit
        clear_proposal_and_votes(game.id)
        game.refresh_from_db()
        game.prosecutions_remaining -= 1
        game.save()

    elif sub_phase in (
        Game.SubPhase.CONSULAR_ELECTION,
        Game.SubPhase.CENSOR_ELECTION,
        Game.SubPhase.DICTATOR_ELECTION,
    ):
        # Cancel proposal — PM can re-propose with a different nominee
        clear_proposal_and_votes(game.id)

    elif sub_phase == Game.SubPhase.DICTATOR_APPOINTMENT:
        # No current_proposal; the SUGGESTED_DICTATOR and NAMED_IN_PROPOSAL statuses
        # are removed by clear_status_items in kill_senator. Nothing else to do.
        pass

    elif sub_phase == Game.SubPhase.OTHER_BUSINESS:
        proposal = game.current_proposal or ""
        if "land bill" in proposal.lower():
            # Land Bill vote is never cancelled by the death of a named senator
            pass
        elif proposal.startswith("Award the ") and " concession to " in proposal:
            # Concession award: once per turn, cannot be re-proposed
            game.add_unavailable_proposal(proposal)
            game.save()
            clear_proposal_and_votes(game.id)
        else:
            # Deploy forces / replace proconsul: PM can re-propose
            clear_proposal_and_votes(game.id)
