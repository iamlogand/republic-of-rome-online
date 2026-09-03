from contextlib import contextmanager
from copy import deepcopy
from typing import Generator, Optional

from django.core.cache import cache

from rorapp.classes.random_resolver import FakeRandomResolver

EMPTY_RESOLVER_STATE: dict = {
    "dice_rolls": [],
    "land_casualty_order": [],
    "naval_casualty_order": [],
    "mortality_chits": [],
    "veteran_order": [],
}


def _resolver_cache_key(game_id: int) -> str:
    return f"fake_resolver_{game_id}"


def _get_resolver_state(cache_key: str) -> dict:
    return cache.get(cache_key, deepcopy(EMPTY_RESOLVER_STATE))


def _save_resolver_state(cache_key: str, state: dict) -> None:
    if any(state.values()):
        cache.set(cache_key, state)
    else:
        cache.delete(cache_key)


def send_resolver_state(game_id: int, state: dict) -> None:
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"debug_{game_id}",
        {"type": "debug_update", "data": {"resolver": state}},
    )


@contextmanager
def fake_resolver_from_cache(
    game_id: int,
) -> Generator[Optional[FakeRandomResolver], None, None]:
    cache_key = _resolver_cache_key(game_id)
    state = _get_resolver_state(cache_key)

    resolver: Optional[FakeRandomResolver] = None
    if any(state.values()):
        resolver = FakeRandomResolver()
        resolver.dice_rolls = list(state["dice_rolls"])
        resolver.land_casualty_order = [list(e) for e in state["land_casualty_order"]]
        resolver.naval_casualty_order = [list(e) for e in state["naval_casualty_order"]]
        resolver.mortality_chits = [list(e) for e in state["mortality_chits"]]
        resolver.veteran_order = list(state["veteran_order"])

    yield resolver

    if resolver is not None:
        remaining = {
            "dice_rolls": resolver.dice_rolls,
            "land_casualty_order": resolver.land_casualty_order,
            "naval_casualty_order": resolver.naval_casualty_order,
            "mortality_chits": resolver.mortality_chits,
            "veteran_order": resolver.veteran_order,
        }
        _save_resolver_state(cache_key, remaining)

    send_resolver_state(game_id, _get_resolver_state(cache_key))
