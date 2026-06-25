import pytest
from rorapp.actions.attract_knight import AttractKnightAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Faction, Game
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.game_state_snapshot import GameStateSnapshot


@pytest.mark.django_db
def test_knight_not_attracted_on_low_roll(forum_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = forum_game
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()

    senator = faction.senators.first()
    assert senator is not None
    senator.talents = 10
    senator.save()

    execute_effects_and_manage_actions(game.id)

    resolver.dice_rolls = [2]

    # Act
    result = AttractKnightAction().execute(
        game.id,
        faction.id,
        {"Senator": str(senator.id), "Talents": 3},
        resolver,
    )

    # Assert
    assert result.success
    senator.refresh_from_db()
    assert senator.knights == 0


@pytest.mark.django_db
def test_attract_knight_autoskipped_when_all_senators_lack_talents_for_evil_omens(
    forum_game: Game,
):
    # Arrange
    game = forum_game
    game.add_effect(GameEffect.EVIL_OMENS)
    game.save()
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()
    for senator in faction.senators.filter(alive=True):
        senator.talents = 0
        senator.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase != Game.SubPhase.ATTRACT_KNIGHT


@pytest.mark.django_db
def test_attract_knight_not_autoskipped_when_any_senator_has_enough_talents(
    forum_game: Game,
):
    # Arrange
    game = forum_game
    game.add_effect(GameEffect.EVIL_OMENS)
    game.save()
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()
    senators = list(faction.senators.filter(alive=True))
    for senator in senators[:-1]:
        senator.talents = 0
        senator.save()
    senators[-1].talents = 1
    senators[-1].save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.ATTRACT_KNIGHT


@pytest.mark.django_db
def test_attract_knight_not_autoskipped_when_faction_has_knights_to_pressure(
    forum_game: Game,
):
    # Arrange
    game = forum_game
    game.add_effect(GameEffect.EVIL_OMENS)
    game.save()
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()
    senator = faction.senators.filter(alive=True).first()
    senator.talents = 0
    senator.knights = 1
    senator.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.ATTRACT_KNIGHT


@pytest.mark.django_db
def test_get_schema_excludes_senators_with_insufficient_talents_under_evil_omens(
    forum_game: Game,
):
    # Arrange
    game = forum_game
    game.add_effect(GameEffect.EVIL_OMENS)
    game.save()
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()
    senators = list(faction.senators.filter(alive=True))
    poor_senator = senators[0]
    poor_senator.talents = 0
    poor_senator.save()
    rich_senator = senators[1]
    rich_senator.talents = 2
    rich_senator.save()

    # Act
    actions = AttractKnightAction().get_schema(GameStateSnapshot(game.id), faction.id)

    # Assert
    assert len(actions) == 1
    senator_options = actions[0].field_descriptors[0]["options"]
    option_ids = [o["id"] for o in senator_options]
    assert poor_senator.id not in option_ids
    assert rich_senator.id in option_ids


@pytest.mark.django_db
def test_get_schema_sets_min_talents_to_evil_omens_level(
    forum_game: Game,
):
    # Arrange
    game = forum_game
    game.add_effect(GameEffect.EVIL_OMENS)
    game.add_effect(GameEffect.EVIL_OMENS)
    game.save()
    faction: Faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()
    for senator in faction.senators.filter(alive=True):
        senator.talents = 5
        senator.save()

    # Act
    actions = AttractKnightAction().get_schema(GameStateSnapshot(game.id), faction.id)

    # Assert
    assert len(actions) == 1
    talents_descriptor = actions[0].field_descriptors[1]
    assert talents_descriptor["min"] == [2]
