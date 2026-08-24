from rorapp.models import Game, Log


def log_motion_result(game: Game, passed: bool) -> None:
    """Log the outcome of a motion, including the vote counts that decided it."""

    outcome = "passed" if passed else "defeated"
    Log.create_object(
        game.id,
        f"Motion {outcome}: {game.current_proposal}"
        f" ({game.votes_yea} yea, {game.votes_nay} nay).",
    )
