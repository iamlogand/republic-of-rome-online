import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Faction, Game, Log, Senator


def _setup_revolution_end(game: Game) -> None:
    game.phase = Game.Phase.REVOLUTION
    game.sub_phase = Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
    game.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()


def _make_consul_for_life(game: Game, faction: Faction) -> Senator:
    senator = Senator.objects.filter(game=game, faction=faction).order_by("id").first()
    assert senator is not None
    senator.add_title(Senator.Title.CONSUL_FOR_LIFE)
    senator.save()
    return senator


@pytest.mark.django_db
def test_consul_for_life_surviving_the_revolution_phase_wins(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction2: Faction = game.factions.get(position=2)
    _make_consul_for_life(game, faction2)
    _setup_revolution_end(game)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    logs = Log.objects.filter(game=game)
    assert game.finished_on is not None
    assert any(faction2.display_name in log.text for log in logs)


@pytest.mark.django_db
def test_consul_for_life_win_does_not_advance_the_turn(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction2: Faction = game.factions.get(position=2)
    _make_consul_for_life(game, faction2)
    _setup_revolution_end(game)
    starting_turn = game.turn

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.turn == starting_turn
    assert game.phase == Game.Phase.REVOLUTION


@pytest.mark.django_db
def test_game_continues_when_the_consul_for_life_died_earlier_in_the_turn(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction2: Faction = game.factions.get(position=2)
    consul_for_life = _make_consul_for_life(game, faction2)
    consul_for_life.alive = False
    consul_for_life.save()
    _setup_revolution_end(game)
    starting_turn = game.turn

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.finished_on is None
    assert game.turn == starting_turn + 1


@pytest.mark.django_db
def test_consul_for_life_wins_the_era_ends_check_despite_lower_influence(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction1: Faction = game.factions.get(position=1)
    faction2: Faction = game.factions.get(position=2)
    Senator.objects.filter(game=game, faction=faction1).update(influence=20)
    Senator.objects.filter(game=game, faction=faction2).update(influence=1)
    _make_consul_for_life(game, faction2)
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.ERA_ENDS
    game.era_ends = True
    game.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    logs = Log.objects.filter(game=game)
    assert game.finished_on is not None
    assert any(faction2.display_name in log.text for log in logs)
    assert not any(faction1.display_name in log.text for log in logs)
