import pytest
from rorapp.actions.pressure_knight import PressureKnightAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import AvailableAction, Faction, Game, Senator
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Log


def _setup_pressure_knight_scenario(
    game: Game,
    faction: Faction,
    senator_knights: dict[Senator, int],
    give_initiative: bool = True,
) -> None:
    """Common setup for pressure knight tests."""
    if give_initiative:
        faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
        faction.save()

    for senator, knights in senator_knights.items():
        senator.knights = knights
        senator.save()

    execute_effects_and_manage_actions(game.id)


@pytest.mark.django_db
def test_pressure_one_knight_adds_roll_to_talents_and_removes_knight(forum_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = forum_game
    faction: Faction = game.factions.get(position=1)
    senator = faction.senators.first()
    assert senator is not None

    _setup_pressure_knight_scenario(game, faction, {senator: 2})
    senator.talents = 5
    senator.save()

    resolver.dice_rolls = [4]
    pre_knights = senator.knights

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
    assert senator.votes == senator.oratory + pre_knights - 1
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.SPONSOR_GAMES

@pytest.mark.django_db
def test_pressure_multiple_knights_rolls_separate_dice_for_each(forum_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = forum_game
    faction: Faction = game.factions.get(position=1)
    senator = faction.senators.first()
    assert senator is not None

    _setup_pressure_knight_scenario(game, faction, {senator: 3})

    resolver.dice_rolls = [2, 5, 1]
    pre_knights = senator.knights

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
    assert senator.votes == senator.oratory + pre_knights - 3

    # Verify logging (integration-style check)
    logs = Log.objects.filter(game=game)
    assert any("pressured 3 knights for 8T" in log.text for log in logs)

    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.SPONSOR_GAMES

@pytest.mark.django_db
def test_pressure_knights_from_two_senators_affects_each_correctly(forum_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = forum_game
    faction: Faction = game.factions.get(position=1)
    senators = list(faction.senators.all()[:2])

    _setup_pressure_knight_scenario(game, faction, {senators[0]: 1, senators[1]: 2})
    senators[0].talents = 10
    senators[1].talents = 20
    senators[0].save()
    senators[1].save()

    resolver.dice_rolls = [6, 3, 4]
    pre_knights0 = senators[0].knights
    pre_knights1 = senators[1].knights

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
    assert senators[0].votes == senators[0].oratory + pre_knights0 - 1
    assert senators[1].knights == 0
    assert senators[1].talents == 20 + 3 + 4
    assert senators[1].votes == senators[1].oratory + pre_knights1 - 2

    # Check that both senators appear in the log
    logs = Log.objects.filter(game=game)
    log_text = "; ".join(log.text for log in logs)
    assert senators[0].display_name in log_text
    assert senators[1].display_name in log_text

    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.SPONSOR_GAMES


@pytest.mark.django_db
def test_pressure_zero_knights_advances_subphase_without_log_or_senator_changes(forum_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = forum_game
    faction: Faction = game.factions.get(position=1)
    senator = faction.senators.first()
    assert senator is not None

    _setup_pressure_knight_scenario(game, faction, {senator: 2})
    initial_knights = senator.knights
    initial_talents = senator.talents
    initial_log_count = Log.objects.filter(game=game).count()

    # No rolls should be consumed for zero pressure
    resolver.dice_rolls = [99]

    # Act
    result = PressureKnightAction().execute(
        game.id,
        faction.id,
        {"Pressures": {str(senator.id): 0}},
        resolver,
    )

    # Assert
    assert result.success
    senator.refresh_from_db()
    assert senator.knights == initial_knights
    assert senator.talents == initial_talents
    assert senator.votes == senator.oratory + initial_knights

    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.SPONSOR_GAMES

    # No pressure-related log entry should have been created
    logs = Log.objects.filter(game=game)
    assert len(logs) == initial_log_count
    assert not any("pressured" in log.text for log in logs)


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
    assert senator is not None
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
    assert senator is not None
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
def test_pressure_knights_get_schema_is_empty(forum_game: Game):
    # Arrange
    game = forum_game
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()

    senator = faction.senators.first()
    assert senator is not None
    senator.knights = 2
    senator.save()

    snapshot = GameStateSnapshot(game.id)

    # Act
    result = PressureKnightAction().get_schema(snapshot, faction.id)

    # Assert - with custom form approach, schema is empty
    assert len(result) == 1
    assert len(result[0].schema) == 0  # empty schema for custom form


@pytest.mark.django_db
def test_is_allowed_returns_faction_when_conditions_met(forum_game: Game):
    # Arrange
    game = forum_game
    faction: Faction = game.factions.get(position=1)
    senator = faction.senators.first()
    assert senator is not None
    senator.knights = 1
    senator.save()
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()

    snapshot = GameStateSnapshot(game.id)
    action = PressureKnightAction()

    # Act
    result = action.is_allowed(snapshot, faction.id)

    # Assert
    assert result == faction


@pytest.mark.django_db
def test_is_allowed_returns_none_without_knights(forum_game: Game):
    # Arrange
    game = forum_game
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()

    snapshot = GameStateSnapshot(game.id)
    action = PressureKnightAction()

    # Act
    result = action.is_allowed(snapshot, faction.id)

    # Assert
    assert result is None


@pytest.mark.django_db
def test_pressure_knights_get_schema_is_empty_when_no_knights(forum_game: Game):
    # Arrange
    game = forum_game
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()

    senator = faction.senators.first()
    assert senator is not None
    senator.knights = 0
    senator.save()

    snapshot = GameStateSnapshot(game.id)

    # Act
    result = PressureKnightAction().get_schema(snapshot, faction.id)

    # Assert
    assert len(result) == 0  # No AvailableAction should be created


@pytest.mark.django_db
def test_pressure_knights_available_action_is_created_when_reaching_phase(forum_game: Game):
    # Arrange
    game = forum_game
    faction: Faction = game.factions.get(position=1)
    senator = faction.senators.first()
    assert senator is not None
    senator.knights = 2
    senator.save()

    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()

    # Act - drive through the normal effect executor
    execute_effects_and_manage_actions(game.id)

    # Assert - custom form approach means schema is empty
    available_actions = AvailableAction.objects.filter(game=game, base_name="Pressure knight")
    assert available_actions.count() == 1

    action = available_actions.first()
    assert action is not None
    assert action.faction == faction
    assert len(action.schema) == 0  # empty schema for custom form
