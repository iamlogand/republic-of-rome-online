from typing import Optional
from rorapp.actions.meta.action_manager import manage_actions
from rorapp.classes.random_resolver import RandomResolver, RealRandomResolver
from rorapp.effects.meta.registry import effect_registry
from rorapp.game_state.game_state_snapshot import GameStateSnapshot


def execute_effects_and_manage_actions(
    game_id: int, random_resolver: Optional[RandomResolver] = None
) -> None:
    random_resolver = random_resolver or RealRandomResolver()
    while True:
        if not execute_effect(game_id, random_resolver):
            manage_actions(game_id)
            return


def execute_effect(game_id: int, random_resolver: RandomResolver) -> bool:
    """
    Finds the first effect that can be executed.

    Returns true if at least one effect was executed, otherwise returns false.
    """

    snapshot = GameStateSnapshot(game_id)

    if snapshot.game.finished_on is None:
        for effect_cls in effect_registry:
            effect = effect_cls()
            if effect.validate(snapshot):
                return effect.execute(game_id, random_resolver)
    return False
