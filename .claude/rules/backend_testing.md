---
paths:
  - "backend/tests/**/*.py"
---
# Backend Testing Conventions

## Directory structure

`tests/s{N}_{chapter}/s{MM}_{section}/{X}_{description}_test.py`

- `s{N}_{chapter}`: e.g. `s1_basic_game`, `s3_scenarios`
- `s{MM}_{section}`: rule file name minus leading chapter number and `.md`, with `s` prefix (e.g. `1.05-mortality-phase.md` → `s05_mortality_phase`)
- `{X}_{description}_test.py`: `{X}` is the 3rd-level sub-section number (e.g. `421_popular_appeal_test.py` for §1.09.421)
- Tests with no rule section: `tests/internals/`

## AAA structure

Every test uses exactly these comment lines — no extra text after them:

```python
@pytest.mark.django_db
def test_name(basic_game: Game):
    # Arrange
    ...
    # Act
    ...
    # Assert
    ...
```

- Omit `# Arrange` only if there are zero arrangement lines
- Never omit `# Act` or `# Assert`

## Fixtures

- Global: `basic_game` (minimal game, no phase) and `resolver` (`FakeRandomResolver` with empty rolls) in root `conftest.py`
- Phase-scoped fixtures (e.g. `senate_game`) in per-section `conftest.py`, built on `basic_game`
- Promote a fixture to parent `conftest.py` only when used by more than one section
- `_setup_*` helpers within a file are allowed for complex shared state that doesn't warrant a fixture

## Other rules

- Drive behaviour through `execute_effects_and_manage_actions`; call actions/effects directly only when testing their own validation logic
- Assert only what the behaviour under test specifies; ignore unrelated side effects
- Use `refresh_from_db()` to reload model state
- Use `@pytest.mark.parametrize` for discrete outcome tables (one param set per row); prefer separate test functions otherwise
- No docstrings; test names must be self-describing (e.g. `test_censor_appointed_when_one_prior_consul_eligible`)
