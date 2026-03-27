from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.send_game_state import send_game_state
from rorapp.models.available_action import AvailableAction
from rorapp.models.game import Game


PHASE_ORDER = [
    Game.Phase.MORTALITY,
    Game.Phase.REVENUE,
    Game.Phase.FORUM,
    Game.Phase.POPULATION,
    Game.Phase.SENATE,
    Game.Phase.COMBAT,
    Game.Phase.REVOLUTION,
]


def _get_next_phase(game: Game) -> Game.Phase:
    if game.phase in (Game.Phase.REVOLUTION, Game.Phase.INITIAL):
        next_phase = Game.Phase.MORTALITY
    else:
        if game.phase is None:
            raise ValueError(f"Game {game.id} has no phase")
        current_index = PHASE_ORDER.index(Game.Phase(game.phase))
        next_phase = PHASE_ORDER[current_index + 1]
    if game.phase == Game.Phase.REVOLUTION:
        game.turn += 1
    return next_phase


def advance_to_next_phase(game_id: int) -> tuple[Game, Game.Phase]:
    """
    Advance the game to the next phase, execute effects, and return
    (refreshed game, the phase it was advanced to before effects ran).
    """
    game = Game.objects.get(id=game_id)

    next_phase = _get_next_phase(game)

    AvailableAction.objects.filter(game=game).delete()

    for faction in game.factions.all():
        faction.status_items = []
        faction.save()

    for faction in game.factions.all():
        for senator in faction.senators.all():
            senator.status_items = []
            senator.save()

    for senator in game.senators.filter(faction__isnull=True):
        senator.status_items = []
        senator.save()

    game.current_proposal = None
    game.defeated_proposals = []
    game.votes_yea = 0
    game.votes_nay = 0
    game.phase = next_phase
    game.sub_phase = Game.SubPhase.START
    game.save()

    execute_effects_and_manage_actions(game_id)
    send_game_state(game_id)

    game.refresh_from_db()
    return game, next_phase
