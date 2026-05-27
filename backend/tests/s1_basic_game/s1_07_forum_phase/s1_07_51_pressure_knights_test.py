import pytest
from rorapp.actions.pressure_knight import PressureKnightAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Faction, Game, Senator
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.game_state_snapshot import GameStateSnapshot


@pytest.mark.django_db
def test_pressure_one_knight_adds_roll_to_talents_and_removes_knight(forum_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = forum_game
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()

    senator = faction.senators.first()
    assert senator is not None
    senator.knights = 2
    senator.talents = 5
    senator.save()

    execute_effects_and_manage_actions(game.id)

    resolver.dice_rolls = [4]

    # Act
    result = PressureKnightAction().execute(
        game.id,
        faction.id,
        {"Pressures": {str(senator.id): 1}},
        resolver,
    )

    # Assert
    assert result.success
    senator.refresh_from_db()
    assert senator.knights == 1
    assert senator.talents == 5 + 4
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.SPONSOR_GAMES

@pytest.mark.django_db
def test_pressure_multiple_knights_rolls_separate_dice_for_each(forum_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = forum_game
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()

    senator = faction.senators.first()
    assert senator is not None
    senator.knights = 3
    senator.talents = 0
    senator.save()

    execute_effects_and_manage_actions(game.id)

    resolver.dice_rolls = [2, 5, 1]

    # Act
    result = PressureKnightAction().execute(
        game.id,
        faction.id,
        {"Pressures": {str(senator.id): 3}},
        resolver,
    )

    # Assert
    assert result.success
    senator.refresh_from_db()
    assert senator.knights == 0
    assert senator.talents == 2 + 5 + 1
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.SPONSOR_GAMES

@pytest.mark.django_db
def test_pressure_knights_from_two_senators_affects_each_correctly(forum_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = forum_game
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()

    senators = list(faction.senators.all()[:2])
    senators[0].knights = 1
    senators[0].talents = 10
    senators[0].save()
    senators[1].knights = 2
    senators[1].talents = 20
    senators[1].save()

    execute_effects_and_manage_actions(game.id)

    resolver.dice_rolls = [6, 3, 4]

    # Act
    result = PressureKnightAction().execute(
        game.id,
        faction.id,
        {"Pressures": {str(senators[0].id): 1, str(senators[1].id): 2}},
        resolver,
    )

    # Assert
    assert result.success
    senators[0].refresh_from_db()
    senators[1].refresh_from_db()
    assert senators[0].knights == 0
    assert senators[0].talents == 10 + 6
    assert senators[1].knights == 0
    assert senators[1].talents == 20 + 3 + 4
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.SPONSOR_GAMES


@pytest.mark.django_db
def test_pressure_knights_without_current_initiative_still_succeeds(forum_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = forum_game
    faction: Faction = game.factions.get(position=1)
    # Intentionally omit CURRENT_INITIATIVE — protection currently only lives in is_allowed()
    senator = faction.senators.first()
    assert senator is not None
    senator.knights = 2
    senator.talents = 0
    senator.save()

    execute_effects_and_manage_actions(game.id)

    resolver.dice_rolls = [3]

    # Act
    result = PressureKnightAction().execute(
        game.id,
        faction.id,
        {"Pressures": {str(senator.id): 1}},
        resolver,
    )

    # Assert
    assert result.success
    senator.refresh_from_db()
    assert senator.knights == 1
    assert senator.talents == 3
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.SPONSOR_GAMES


@pytest.mark.django_db
def test_pressure_knights_rejected_when_targeting_another_factions_senator(forum_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = forum_game
    faction1: Faction = game.factions.get(position=1)
    faction2: Faction = game.factions.get(position=2)
    faction1.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction1.save()

    senator_from_faction2 = faction2.senators.first()
    assert senator_from_faction2 is not None
    senator_from_faction2.knights = 1
    senator_from_faction2.save()

    execute_effects_and_manage_actions(game.id)

    # Act
    result = PressureKnightAction().execute(
        game.id,
        faction1.id,
        {"Pressures": {str(senator_from_faction2.id): 1}},
        resolver,
    )

    # Assert
    assert not result.success
    assert "not in your faction" in (result.message or "").lower()
    senator_from_faction2.refresh_from_db()
    assert senator_from_faction2.knights == 1


@pytest.mark.django_db
def test_pressure_knights_rejected_when_pressures_is_not_a_dict(forum_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = forum_game
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()

    senator = faction.senators.first()
    senator.knights = 1
    senator.save()

    execute_effects_and_manage_actions(game.id)

    # Act
    result = PressureKnightAction().execute(
        game.id,
        faction.id,
        {"Pressures": [1, 2, 3]},
        resolver,
    )

    # Assert
    assert not result.success
    assert "invalid pressure selection data" in (result.message or "").lower()


@pytest.mark.django_db
def test_pressure_knights_rejected_with_unrecognized_selection_key(forum_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = forum_game
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()

    senator = faction.senators.first()
    senator.knights = 1
    senator.save()

    execute_effects_and_manage_actions(game.id)

    # Act
    result = PressureKnightAction().execute(
        game.id,
        faction.id,
        {"wrong_key": {str(senator.id): 1}},
        resolver,
    )

    # Assert
    assert not result.success
    assert "invalid pressure selection data" in (result.message or "").lower()


@pytest.mark.django_db
def test_pressure_knights_in_wrong_sub_phase_still_executes(forum_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = forum_game
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()

    senator = faction.senators.first()
    assert senator is not None
    senator.knights = 2
    senator.talents = 0
    senator.save()

    # Force the game into a later sub-phase (protection currently only exists in is_allowed + view)
    game.sub_phase = Game.SubPhase.SPONSOR_GAMES
    game.save()

    resolver.dice_rolls = [4]

    # Act
    result = PressureKnightAction().execute(
        game.id,
        faction.id,
        {"Pressures": {str(senator.id): 1}},
        resolver,
    )

    # Assert
    assert result.success
    senator.refresh_from_db()
    assert senator.knights == 1
    assert senator.talents == 4
    game.refresh_from_db()
    # Currently forces the phase forward even from the wrong sub-phase
    assert game.sub_phase == Game.SubPhase.SPONSOR_GAMES


@pytest.mark.django_db
def test_pressure_knights_get_schema_returns_per_senator_number_field(forum_game: Game):
    # Arrange
    game = forum_game
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()

    senators = list(faction.senators.all()[:2])
    senators[0].knights = 3
    senators[0].save()
    senators[1].knights = 0  # should be excluded from schema
    senators[1].save()

    # Senator in another faction with knights should also be excluded
    other_faction: Faction = game.factions.get(position=2)
    other_senator = other_faction.senators.first()
    assert other_senator is not None
    other_senator.knights = 5
    other_senator.save()

    snapshot = GameStateSnapshot(game.id)

    # Act
    result = PressureKnightAction().get_schema(snapshot, faction.id)

    # Assert
    assert len(result) == 1
    schema = result[0].schema
    assert len(schema) == 1

    field = schema[0]
    assert field["type"] == "per_senator_number"
    assert field["name"] == "Pressures"

    entries = field["entries"]
    assert len(entries) == 1  # only senators[0] has knights > 0

    entry = entries[0]
    assert entry["senator_id"] == senators[0].id
    assert entry["name"] == senators[0].display_name
    assert entry["max"] == 3
