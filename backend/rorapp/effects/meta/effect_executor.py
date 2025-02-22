from rorapp.actions.meta.action_manager import manage_actions
from rorapp.effects.meta.registry import effect_registry
from rorapp.game_state.game_state_snapshot import GameStateSnapshot


def execute_effects_and_manage_actions(game_id: int) -> None:
    while True:
        if not execute_effect(game_id):
            manage_actions(game_id)
            return


def execute_effect(game_id: int) -> bool:
    """
    Finds the first effect that can be executed.

    Returns true if at least one effect was executed, otherwise returns false.
    """

    snapshot = GameStateSnapshot(game_id)

    for effect_cls in effect_registry:
        effect = effect_cls()
        if effect.validate(snapshot):
            effect.execute(game_id)
            return True
    return False
