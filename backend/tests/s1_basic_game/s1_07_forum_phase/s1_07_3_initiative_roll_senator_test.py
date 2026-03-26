import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Faction, Game, Senator


def _setup_initiative_roll(game: Game, faction: Faction, deck: list) -> None:
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.INITIATIVE_ROLL
    game.deck = deck
    game.save()
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()


@pytest.mark.django_db
def test_drawing_senator_card_creates_unaligned_senator_when_none_in_play(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    Senator.objects.filter(game=game, code="18").delete()
    _setup_initiative_roll(game, faction, ["senator:18"])

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    new_senator = Senator.objects.filter(game=game, code="18", family=True).first()
    assert new_senator is not None
    assert new_senator.faction is None
    assert new_senator.alive is True
    assert new_senator.family_name == "Quinctius"


@pytest.mark.django_db
def test_drawing_senator_card_gives_statesman_family_support(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    statesman = Senator.objects.create(
        game=game,
        faction=faction,
        family_name="Cornelius",
        statesman_name="P. Cornelius Scipio Africanus",
        family=False,
        code="1a",
        military=5,
        oratory=5,
        loyalty=9,
        influence=5,
    )
    Senator.objects.filter(game=game, code="1", family=True).delete()
    _setup_initiative_roll(game, faction, ["senator:1"])

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    statesman.refresh_from_db()
    assert statesman.family is True


@pytest.mark.django_db
def test_drawing_senator_card_does_not_create_duplicate_when_statesman_in_play(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    Senator.objects.create(
        game=game,
        faction=faction,
        family_name="Cornelius",
        statesman_name="P. Cornelius Scipio Africanus",
        family=False,
        code="1a",
        military=5,
        oratory=5,
        loyalty=9,
        influence=5,
    )
    Senator.objects.filter(game=game, code="1", family=True).delete()
    _setup_initiative_roll(game, faction, ["senator:1"])

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Senator.objects.filter(game=game, code="1").count() == 0
    assert Senator.objects.filter(game=game, code="1a").count() == 1


@pytest.mark.django_db
def test_drawing_senator_card_uses_correct_stats_from_game_data(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    Senator.objects.filter(game=game, code="18").delete()
    _setup_initiative_roll(game, faction, ["senator:18"])

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    new_senator = Senator.objects.get(game=game, code="18", family=True)
    assert new_senator.military == 3
    assert new_senator.oratory == 2
    assert new_senator.loyalty == 6
    assert new_senator.influence == 1
