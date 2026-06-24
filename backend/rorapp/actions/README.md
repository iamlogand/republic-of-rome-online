# Actions

Actions are how players interact with the game. Each action is implemented as a class inheriting `ActionBase` and registered in `meta/registry.py`. To register a new action, import it and add an entry to the `action_registry` dict:

```python
# meta/registry.py
action_registry: Dict[str, Type[ActionBase]] = {
    ...
    MyNewAction.NAME: MyNewAction,
}
```

## Example

A condensed version of `ContributeAction` showing the three-method flow. Status-item guards, influence gain, sorting, and logging are omitted for brevity — see `contribute.py` for the full implementation:

```python
class ContributeAction(ActionBase):
    NAME = "Contribute"
    POSITION = 2

    def is_allowed(self, game_state, faction_id):
        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.REVENUE
            and game_state.game.sub_phase == Game.SubPhase.REDISTRIBUTION
            and any(s.talents > 0 for s in game_state.senators
                    if s.faction and s.faction.id == faction.id and s.alive)
        ):
            return faction
        return None

    def get_schema(self, snapshot, faction_id):
        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        senators = [s for s in snapshot.senators
                    if s.faction and s.faction.id == faction.id
                    and s.alive and s.talents > 0]

        return [AvailableAction.objects.create(
            game=snapshot.game,
            faction=faction,
            base_name=self.NAME,
            position=self.POSITION,
            field_descriptors=[
                {
                    "type": "select",
                    "name": "Contributor",
                    "options": [
                        {"value": s.id, "object_class": "senator", "id": s.id,
                         "signals": {"max_talents": s.talents}}
                        for s in senators
                    ],
                },
                {
                    "type": "number",
                    "name": "Talents",
                    "min": [1],
                    "max": ["signal:max_talents"],
                },
            ],
        )]

    def execute(self, game_id, faction_id, selection, random_resolver):
        senator_id = selection["Contributor"]
        talents = int(selection["Talents"])
        senator = Senator.objects.get(game=game_id, faction=faction_id, id=senator_id)
        if talents > senator.talents:
            return ExecutionResult(False)

        senator.talents -= talents
        senator.save()
        # ... transfer to Rome's treasury, create action log, etc.
        return ExecutionResult(True)
```

`is_allowed` checks preconditions. `get_schema` builds the form — here a senator picker whose selection signals the max talent value to a number input. `execute` validates and applies the result.

## Structure

Every action class defines:

| Attribute  | Description                                                    |
| ---------- | -------------------------------------------------------------- |
| `NAME`     | Display name used for the button and dialog title              |
| `POSITION` | UI ordering — lower numbers appear further left (default: `5`) |

Every action class implements three methods:

### `is_allowed()`

Returns the `Faction` if the action is currently available to the player, `None` otherwise. This validates preconditions, not the player's specific input.

The `game_state` parameter is a `GameStateSnapshot` — an object that loads all game data (senators, factions, wars, etc.) into memory once, so action methods can read state without repeated DB queries. It is created by `manage_actions()` in `meta/action_manager.py` and passed to both `is_allowed` and `get_schema` for every action and faction. `is_allowed` also accepts a `GameStateLive` (which queries the DB on each property access) for calls outside that flow; prefer the snapshot when available.

### `get_schema()`

Returns a list of `AvailableAction` objects. Returns `[]` if the action is not allowed. The `field_descriptors` field on each `AvailableAction` is a JSON array of field descriptors that drive the frontend form.

### `execute()`

Full signature:

```python
def execute(self, game_id: int, faction_id: int, selection: Dict[str, Any], random_resolver: RandomResolver) -> ExecutionResult:
```

`selection` keys match the `name` of each field descriptor (plus any `context` keys — see Context below). Re-validate inputs here — do not trust that the client submitted exactly what the field descriptors offered.

`random_resolver` is an abstract interface for dice rolls (see `classes/random_resolver.py`). Actions call `random_resolver.roll_dice(count)` rather than using `random` directly, so that tests can inject deterministic results.

Return an `ExecutionResult` (see `meta/execution_result.py`): `ExecutionResult(True)` on success, or `ExecutionResult(False, "reason")` on failure.

## AvailableAction fields

| Field               | Description                                                                                              |
| ------------------- | -------------------------------------------------------------------------------------------------------- |
| `game`              | ForeignKey to `Game` (required)                                                                          |
| `faction`           | ForeignKey to `Faction` (required)                                                                       |
| `base_name`         | The action class `NAME`                                                                                  |
| `variant_name`      | Optional display name override (should be used when one action class produces multiple distinct buttons) |
| `position`          | UI ordering, copied from the class `POSITION`                                                            |
| `field_descriptors` | Array of field descriptors (see below)                                                                   |
| `context`           | Arbitrary data the action needs at execution time but that is not collected from the player              |

The read-only `name` property returns `variant_name` if set, otherwise `base_name`.

## Field descriptor types

### `select`

Renders a [HTMLSelectElement](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/select) element. Use this when you need the player to select one item from a list of options.

You must pass at least one option to a select field type. Options take one of two shapes depending on whether they represent a plain value or a game object. Either way, you must give each option a `value` to populate the [HTMLSelectElement `value` property](https://developer.mozilla.org/en-US/docs/Web/API/HTMLSelectElement/value) and send back to the API to be read by the `execute()` method.

For a plain value, use `name` as a display label. For a game object, the `object_class` and `id` tell the frontend how to look up and render the object using game state.

The optional `group_by` property groups options visually. Currently only `"faction"` is supported — options are wrapped in `<optgroup>` elements labeled by faction name.

#### Examples

Select field with two plain value options:

```python
{
    "type": "select",
    "name": "Card",
    "options": [
        {"value": "s:fabia", "name": "Fabia"},
        {"value": "concession:harbor fees", "name": "Harbor Fees"},
    ],
}
```

Select field with two game object options:

```python
{
    "type": "select",
    "name": "Senator",
    "group_by": "faction",  # Optional — groups objects by field
    "options": [
        {"value": 1, "object_class": "senator", "id": 1},
        {"value": 2, "object_class": "senator", "id": 2},
    ],
}
```

Select field with dynamically built game object options:

```python
{
    "type": "select",
    "name": "Senator",
    "group_by": "faction",
    "options": [
        {"value": s.id, "object_class": "senator", "id": s.id}
        for s in candidate_senators
    ],
}
```

### `multiselect`

Like `select`, but the player may choose zero or more options. The selection value is a list of `value` entries. Options follow the same two shapes as `select` (plain value or game object).

#### Example

Multiselect field with dynamically built game object options:

```python
{
    "type": "multiselect",
    "name": "Fleets",
    "inline": True,
    "options": [
        {"value": f.id, "object_class": "fleet", "id": f.id}
        for f in available_fleets
    ],
}
```

### `number`

Renders a number input. Use this when you need the player to enter an integer.

`min` and `max` are arrays of lower and upper bounds respectively. The most restrictive value across all entries is used.

#### Example

```python
{
    "type": "number",
    "name": "Talents",
    "min": [1],
    "max": [20],
}
```

### `boolean`

Renders a checkbox. Use this when you need the player to make a yes/no decision.

#### Example

```python
{
    "type": "boolean",
    "name": "Recall commander",
}
```

### `chance`

Renders a read-only display showing the player their probability of success before they commit. Takes no input and contributes nothing to `selection`.

| Property          | Description                                                              |
| ----------------- | ------------------------------------------------------------------------ |
| `dice`            | Number of dice rolled (1, 2, or 3)                                       |
| `label`           | Display label (optional — defaults to `name`)                            |
| `target_min`      | Minimum roll required to succeed                                         |
| `target_max`      | Maximum roll that still succeeds (optional)                              |
| `target_exacts`   | Array of exact roll values that succeed (optional)                       |
| `modifiers`       | Array of values added to the roll — accepts signal references (optional) |
| `ignored_numbers` | Array of roll values that are ignored/rerolled (optional)                |

#### Example

```python
{
    "type": "chance",
    "name": "Chance of success",
    "dice": 1,
    "target_min": 6,
    "modifiers": ["signal:talents"],
}
```

### `calculation`

Renders a read-only display showing a computed value. Takes no input and contributes nothing to `selection`. The `value` is an expression string resolved against signals. No backend action uses this type yet, but the frontend rendering logic is in place.

| Property | Description                                                           |
| -------- | --------------------------------------------------------------------- |
| `value`  | Expression string (can reference signals)                             |
| `label`  | Display label (optional — defaults to `name`, `"HIDDEN"` to suppress) |
| `style`  | Optional — `"warning"` renders in red instead of blue                 |

#### Example

```python
{
    "type": "calculation",
    "name": "Remaining treasury",
    "value": f"{treasury} - signal:talents",
}
```

## Common field properties

### `inline`

An optional boolean supported on all field types. When `True`, the field renders on the same row as the previous field rather than on a new row below it. Useful for pairing related fields (e.g., selecting legions and fleets for the same deployment).

## Signals

Signals let fields communicate client-side: one field emits a named value, and downstream fields consume it to adjust their bounds, visibility, or displayed calculations.

Signals are resolved in the browser as the player makes selections and are never sent back to the server — only the final selected values are. You must therefore re-validate all signal-driven constraints in `execute`.

### Emitting signals

#### From a select or multiselect option

A `signals` dict on an option emits values when the player selects that option. The values are baked in at `get_schema` generation time.

```python
{
    "value": s.id,
    "object_class": "senator",
    "id": s.id,
    "signals": {"max_talents": s.talents},
}
```

An option can emit multiple signals at once:

```python
{
    "value": c.id,
    "object_class": "campaign",
    "id": c.id,
    "signals": {
        "campaign": c.id,
        "commander": c.commander_id,
    },
}
```

#### From a number field

A `signals` dict on a `number` field emits the player's typed value in real time. Use the special keyword `"VALUE"` as the value:

```python
{
    "type": "number",
    "name": "Talents",
    "min": [0],
    "max": [5],
    "signals": {"talents": "VALUE"},
}
```

### Consuming signals

Signal references use the `"signal:<name>"` string syntax.

#### In number min/max

Signal references can appear as entries in a `number` field's `min` or `max` arrays. The most restrictive value across all entries is used:

```python
{
    "type": "number",
    "name": "Talents",
    "min": [0],
    "max": [5, "signal:max_talents"],  # Most restrictive of 5 and the signal value
}
```

Entries can also be arithmetic expressions combining a literal with a signal:

```python
"max": [
    max_recruitment,
    f"{max_recruitment} - signal:fleets",
]
```

#### In conditions

Conditions filter which options or fields are visible based on signal values. See the Conditions section below.

#### In chance modifiers

A `chance` field's `modifiers` array accepts signal references, whose resolved values are added to the dice roll:

```python
{
    "type": "chance",
    "name": "Chance of success",
    "dice": 1,
    "target_min": 6,
    "modifiers": ["signal:talents"],
}
```

### Conditions

Conditions control visibility: they hide an option or field unless all conditions pass. Multiple conditions can be passed in an array; all must be met.

A condition is an object with three keys:

| Key         | Description                                                       |
| ----------- | ----------------------------------------------------------------- |
| `value1`    | A signal reference (`"signal:<name>"`), literal value, or `None`  |
| `operation` | Comparison operator: `"=="`, `"!="`, `">="`, `">"`, `"<="`, `"<"` |
| `value2`    | A literal value or `None`                                         |

Conditions are supported on `select`/`multiselect` options, and on `boolean`, `calculation`, and `chance` fields.

#### On options

Conditions on a `select` or `multiselect` option hide that individual option unless all conditions pass:

```python
{
    "value": s.id,
    "object_class": "senator",
    "id": s.id,
    "conditions": [
        {
            "value1": "signal:consul_1",
            "operation": "!=",
            "value2": s.id,
        },
    ],
}
```

#### On fields

Conditions on a `boolean`, `calculation`, or `chance` field hide the entire field unless all conditions pass:

```python
{
    "type": "boolean",
    "name": "Recall commander",
    "conditions": [
        {
            "value1": "signal:commander",
            "operation": "!=",
            "value2": None,
        },
    ],
}
```

## Context

Use `context` to store data the action needs at execution time that the player did not supply. The frontend passes `context` back in the selection payload alongside field descriptor values.

```python
AvailableAction.objects.create(
    ...,
    field_descriptors=[],
    context={"target_faction_id": target_faction.id},
)
```

In `execute`, read it from `selection`:

```python
target_faction_id = selection.get("target_faction_id")
```

## Multiple actions from one handler

`get_schema` returns a list, so a single handler can produce multiple buttons — one per valid target, for example.

```python
actions = []
for target_faction in callable_factions:
    actions.append(AvailableAction.objects.create(
        ...,
        variant_name=f"Call {target_faction.display_name} to vote",
        context={"target_faction_id": target_faction.id},
    ))
return actions
```

Each button appears separately in the UI. All route to the same `execute` method; use `context` to distinguish them.

## Custom frontend forms

When the field descriptor system cannot express the required input, set `field_descriptors=[]` and handle the action in a dedicated frontend form component. The component is responsible for building the `selection` payload and submitting it to the same endpoint as the generic form.

The frontend dispatches forms via a registry in `customActionForms/meta/registry.ts` that maps action `NAME` strings to React components. If the action's `base_name` matches a key in the registry, the custom component renders instead of `GenericActionForm`. To add a custom form, create a component that accepts `CustomActionFormProps` and add an entry to the registry:

```typescript
// customActionForms/meta/registry.ts
export const customActionFormRegistry: Record<
  string,
  ComponentType<CustomActionFormProps>
> = {
  "Attempt assassination": AttemptAssassinationForm,
  // ...
};
```
