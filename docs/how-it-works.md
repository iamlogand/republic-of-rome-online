# How it works

Republic of Rome Online is a Next.js frontend paired with a Django backend. The backend owns all game logic and state; the frontend is responsible for rendering that state and collecting player input.

## System overview

```
Browser (Next.js)
  ├── REST API (fetch + session cookie)  →  Django / DRF
  └── WebSockets (react-use-websocket)   →  Django Channels / Daphne
                                                  │
                                             PostgreSQL (RDS)
                                             Redis (channel layer)
```

Two WebSocket connections are maintained per game session:

- **Game socket** (`ws/games/<id>/`) — public game state pushed to all connected clients including spectators. Also carries collaborative combat calculator updates.
- **Player socket** (`ws/games/<id>/player/`) — private state (faction treasury, hand of cards, available actions) pushed only to the authenticated player.

After every action or automated effect, the server pushes a fresh state snapshot over both sockets. Clients never poll.

## Backend structure

The Django project (`rorsite`) contains a single app (`rorapp`). Inside `rorapp`, the key subdirectories are:

| Directory | Responsibility |
|-----------|---------------|
| `models/` | Database models |
| `views/` | REST API endpoints |
| `serializers/` | DRF serializers |
| `consumers/` | WebSocket consumers |
| `actions/` | Player action system |
| `effects/` | Automated effect system |
| `game_state/` | State serialisation and delivery |
| `helpers/` | Shared game logic |
| `classes/` | Domain value types |
| `data/` | Static JSON game data (senators, wars, events, etc.) |

## Models

The key models and their relationships:

**`Game`** — The root entity. Holds all Rome-level state: `turn`, `phase`, `sub_phase`, `state_treasury`, `unrest`. Also stores several JSONFields for transient state: `deck` (ordered list of card codes), `effects` (active game-wide effects), `current_proposal`, `votes_yea`, `votes_nay`. A `step` counter increments every time available actions are recomputed; the frontend uses this for change detection.

**`Faction`** — One per player per game. Holds the player's private `treasury` and `cards` hand (both JSONFields), plus a `status_items` list of transient flags (e.g. `"done"`, `"current bidder"`, `"initiative 3"`).

**`Senator`** — A Roman senator. Belongs to a `Faction` (or is unaligned). Carries the full stat block: `military`, `oratory`, `loyalty`, `influence`, `popularity`, `knights`, `talents`. Also holds `titles` (e.g. `"Rome Consul"`, `"HRAO"`) and `status_items` (e.g. `"persuader"`, `"abstained"`), both as JSONFields.

**`War`** — An active or inactive war. Has `status` (`inactive`, `imminent`, `active`), strength values, spoils, and per-turn combat tracking fields.

**`Campaign`** — Links a `War` to a commander `Senator` and the forces assigned to it. Legions and fleets point back to their campaign via FK.

**`Legion` / `Fleet`** — Individual military units. Veterans give double strength.

**`AvailableAction`** — Represents one action currently available to a player. Holds the `base_name` (maps to an action class), `field_descriptors` (JSON array that drives the frontend form), `context` (server-computed data stored server-side and echoed back on submission), and `position` (UI sort order). The full set is recomputed from scratch after every state change.

**`Log`** — Append-only game log entries, tagged with `turn`, `phase`, and `text`.

**`CombatCalculation`** — Collaborative combat planning tool. Not part of game logic; synced across all connected clients via the game WebSocket.

## REST API

Three standard DRF ViewSets handle CRUD for games, factions (joining/leaving), and users.

Two custom endpoints carry the most weight:

**`POST /api/games/<id>/start-game/`** — Host-only. Initialises all game state: deals the deck, creates senator instances from static JSON data, sets up the starting war, and begins turn 1.

**`POST /api/games/<game_id>/submit-action/<action_id>`** — The core game loop endpoint. Validates and executes a player action, then runs the effect/action cycle and pushes updated state to all clients. Wrapped in `select_for_update()` on the game row to prevent concurrent submissions.

Authentication uses Django sessions. The `/auth-status/` endpoint sets the CSRF cookie; all subsequent POST requests include it via the `X-CSRFToken` header.

## Actions

Every player-initiated game action is a class in `rorapp/actions/`, inheriting from `ActionBase`. Each class implements three methods:

**`is_allowed(game_state, faction_id)`** — Returns the `Faction` if this action is currently available, `None` otherwise. Checks phase, sub-phase, and other preconditions, but not specific input values.

**`get_schema(snapshot, faction_id)`** — Returns a list of `AvailableAction` objects describing the UI form. A single action class can return multiple objects (e.g. one per target faction).

**`execute(game_id, faction_id, selection, random_resolver)`** — Performs the state change. Re-validates all inputs (the server never trusts the client). Uses `random_resolver` for all dice rolls so that tests can inject a predictable resolver.

All action classes are registered by name in `actions/meta/registry.py`.

### Frontend forms

Each `AvailableAction` carries a `field_descriptors` JSON array that `GenericActionForm` uses to render and validate the form without any action-specific code. For more complex actions where this isn't expressive enough, a custom React form can be registered in `customActionForms/meta/registry.ts` instead; `ActionDispatcher` checks this registry first and falls back to `GenericActionForm` if no match is found. Either way, the backend receives the same JSON payload and the same `execute()` method handles it — the choice of form is purely a frontend concern.

For the full field descriptor spec — types, signals, conditions, context, and custom forms — see [`backend/rorapp/actions/README.md`](../backend/rorapp/actions/README.md).

## Effects

Automated game procedures — phase transitions, revenue generation, combat resolution, unrest changes, end-game checks — are effect classes in `rorapp/effects/`, inheriting from `EffectBase`. Each implements:

**`validate(snapshot)`** — Returns `True` if this effect should fire now, typically by checking `phase` and `sub_phase`.

**`execute(game_id, random_resolver)`** — Performs the automated action.

Effects are listed in priority order in `effects/meta/registry.py`. High-priority entries (game-over conditions) come first.

## The game loop

After every player action, the server runs this loop. Each time an effect fires, the loop restarts from the top with a fresh snapshot, allowing effects to cascade. Only when no effects remain does `manage_actions` run:

```
execute_effects_and_manage_actions(game_id):
    while True:
        snapshot = GameStateSnapshot(game_id)
        for each effect in registry (priority order):
            if effect.validate(snapshot):
                effect.execute(game_id)
                break  ← restart the loop; effects can cascade
        else:
            manage_actions(game_id)
            return
```

`manage_actions` recomputes all available actions from scratch: it calls `get_schema()` for every action class × every faction, deletes all existing `AvailableAction` rows for the game, bulk-inserts the new ones, and increments `game.step`.

The result is that phases advance automatically through chains of effects until the game reaches a state where a player needs to do something, at which point `AvailableAction` rows describe exactly what each player can do next.

## Game state delivery

After every state change, `send_game_state(game_id)` runs:

1. Serialises all public entities (game, factions, senators, wars, campaigns, legions, fleets, logs) and broadcasts to the Redis channel group `game_{id}`, which all `GameConsumer` instances relay to their connected clients.
2. For each player, serialises private state (treasury, cards, available actions) and broadcasts to the per-player group `game_{id}_user_{uid}`, relayed by their `PlayerConsumer`.

The frontend receives these as WebSocket messages and replaces its React state, triggering a re-render.

## Game state snapshots

Two abstractions avoid repeated database queries during the effect/action cycle:

**`GameStateSnapshot`** — Loads all entities into Python lists at construction time. Used inside the loop where multiple effects and actions read the same state in one cycle.

**`GameStateLive`** — Queries the database on each property access. Used for one-off reads outside the normal cycle.

## Phase progression

Phases advance in order: `MORTALITY → REVENUE → FORUM → POPULATION → SENATE → COMBAT → REVOLUTION`, then back to `MORTALITY` with the turn counter incremented.

Most phases begin with a `START` sub-phase. An effect fires immediately on `START`, does its initialisation work, and advances to the next sub-phase — which may trigger another effect, or may leave the game waiting for player input.

Phase transitions happen either via a player action (e.g. "Close senate") which sets `phase`/`sub_phase` directly in `execute()`, or via an effect that detects the phase is complete.

## Frontend structure

The frontend uses the Next.js App Router. All game UI is client-rendered.

**Key pages:**
- `/games` — game list
- `/games/[id]` — the main game interface
- `/auth/login`, `/auth/callback`, `/auth/logout` — authentication flow

**Key components:**

| Component | Purpose |
|-----------|---------|
| `GameContainer` | Main in-game view: Rome state, factions, wars, campaigns, log, actions panel |
| `ActionDispatcher` | Routes each available action to a custom form or the generic form |
| `GenericActionForm` | Renders forms driven by `field_descriptors`; implements the signal system |
| `CombatCalculator` | Collaborative combat planning tool |

**Custom action forms** (`components/customActionForms/`) exist for a handful of actions where the generic field descriptor system isn't expressive enough (e.g. persuasion, assassination, vote, redistribute talents). All custom forms are registered in `customActionForms/meta/registry.ts`.

**TypeScript classes** (`frontend/classes/`) are thin wrappers around the WebSocket JSON payload. They handle snake_case → camelCase conversion and expose typed properties for all game entities.

## Authentication

Google OAuth is handled by django-allauth (headless mode):

1. The frontend POSTs to `/_allauth/browser/v1/auth/provider/redirect`, which redirects the browser to Google.
2. Google redirects back to Django with an auth code; allauth exchanges it and creates a Django session.
3. Django redirects to `/login-callback/`, which sets a `sessionid` cookie scoped to the parent domain (shared between the `api.` and `www.` subdomains), then redirects back to the frontend.
4. All subsequent API requests include this cookie via `credentials: "include"`; DRF's `SessionAuthentication` identifies the user from it.

## End-to-end example: attracting a knight

1. After the previous action, `manage_actions()` computed available actions. For the current player in the forum phase, `AttractKnightAction.get_schema()` returned an `AvailableAction` with a `select` of eligible senators (each emitting `oratory` and `talents` signals) and a `chance` field showing the success probability. This was delivered via the player WebSocket.

2. The frontend renders an "Attract knight" button. The player clicks it, selects a senator, and sees the success probability update in real time.

3. The player clicks confirm. The frontend POSTs `{ "Senator": 42 }` to `/api/games/7/submit-action/123`.

4. `SubmitActionViewSet.submit_action` acquires a lock on the game row, re-validates the action is still allowed, merges the submission with the stored context, and calls `AttractKnightAction.execute()`.

5. `execute()` validates the senator is in this faction, is alive, and has at least 2 talents. It rolls a die, adds the senator's oratory, and on a result of 7+ adds a knight and deducts 2 talents. A log entry is created.

6. `execute_effects_and_manage_actions()` runs. Any applicable effects fire and cascade until none remain, then `manage_actions()` recomputes all available actions and increments `game.step`.

7. `send_game_state()` pushes the updated senator stats and log to all clients via the game WebSocket, and the updated available actions to the player via the player WebSocket.

8. The frontend receives both messages, updates React state, and re-renders.
