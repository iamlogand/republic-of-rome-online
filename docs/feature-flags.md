# Feature flags

Feature flags allow incomplete features to be merged to `main` before they are ready for players. This keeps branches short-lived and avoids long-running divergence from `main`.

## How flags are defined

Flags are read from environment variables at startup. Any variable named `FEATURE_FLAG_<NAME>` is automatically available as `settings.FEATURE_FLAGS["<name>"]` (lowercased):

```
FEATURE_FLAG_CIVIL_WAR=True
```

```python
from django.conf import settings

settings.FEATURE_FLAGS.get("civil_war")  # True
settings.FEATURE_FLAGS.get("unknown")   # None (falsy)
```

No changes to `settings.py` are needed when adding a new flag — just choose a name and start using it.

## Using flags

Flag checks must only appear in `is_allowed`, `validate`, and `execute` — never inside helpers. Helpers are shared logic and should not need to know about features; keeping flags at the action/effect level makes it easy to see at a glance what a flag controls. For example:

```python
def validate(self, game_state):
    return (
        game_state.game.sub_phase == Game.SubPhase.CIVIL_WAR_DECLARATION
        and not settings.FEATURE_FLAGS.get("civil_war")
        and any(c.land_victory for c in game_state.campaigns)
    )
```

```python
def is_allowed(self, game_state, faction_id):
    if not settings.FEATURE_FLAGS.get("civil_war"):
        return None
    ...
```

## The off-path must be a valid game flow

A flag is only safe if the game can progress with the flag off. This applies to both actions and effects — a required action that is never available leaves the game waiting for input that will never come, just as a required effect that never fires leaves it unable to advance.

How you handle the off-path is up to you, as long as the flag check stays in `is_allowed`, `validate`, or `execute`. It might be a branch in `execute`, a condition in `validate`, a separate effect that fires instead, or something else. What matters is that there is a complete, playable path through the game regardless of the flag state.

Before shipping a flagged feature, verify that a game can be played with the flag both on and off.

## Removing a flag

Once a feature is fully shipped and enabled in production, remove the flag check from the code and delete the environment variable. Flags are not intended to be permanent.
