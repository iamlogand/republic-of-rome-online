import pytest
from rorapp.actions.play_concession import PlayConcessionAction
from rorapp.actions.play_statesman import PlayStatesmanAction
from rorapp.classes.concession import Concession
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Senator
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


def _setup_play_phase(game: Game, faction: Faction, cards: list):
    game.phase = Game.Phase.REVOLUTION
    game.sub_phase = Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
    game.save()
    faction.cards = cards
    faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
    faction.save()


@pytest.mark.django_db
def test_revolution_start_enters_card_trading(revolution_game: Game):
    # Arrange
    game = revolution_game

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.CARD_TRADING
    for faction in game.factions.all():
        assert not faction.has_status_item(FactionStatusItem.AWAITING_DECISION)


@pytest.mark.django_db
def test_concession_played_to_senator_during_revolution(basic_game: Game):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_play_phase(game, faction, [f"concession:{Concession.MINING.value}"])
    senator = Senator.objects.filter(game=game, faction=faction).first()
    assert senator is not None

    # Act
    result = PlayConcessionAction().execute(
        game.id,
        faction.id,
        {
            "Senator": str(senator.id),
            "Concession": f"concession:{Concession.MINING.value}",
        },
        FakeRandomResolver(),
    )

    # Assert
    assert result.success
    senator.refresh_from_db()
    assert Concession.MINING.value in senator.concessions
    faction.refresh_from_db()
    assert f"concession:{Concession.MINING.value}" not in faction.cards


@pytest.mark.django_db
def test_concession_not_playable_without_concession_cards(basic_game: Game):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_play_phase(game, faction, [])
    snapshot = GameStateSnapshot(game.id)

    # Act
    result = PlayConcessionAction().get_schema(snapshot, faction.id)

    # Assert
    assert result == []


@pytest.mark.django_db
def test_play_statesman_action_available_with_statesman_card(basic_game: Game):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_play_phase(game, faction, ["statesman:1a"])
    snapshot = GameStateSnapshot(game.id)

    # Act
    result = PlayStatesmanAction().get_schema(snapshot, faction.id)

    # Assert
    assert len(result) == 1


@pytest.mark.django_db
def test_play_statesman_upgrades_family_senator(basic_game: Game):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_play_phase(game, faction, ["statesman:1a"])
    family_senator = Senator.objects.get(
        game=game, faction=faction, family_name="Cornelius"
    )
    original_generation = family_senator.generation
    original_id = family_senator.id

    # Act
    result = PlayStatesmanAction().execute(
        game.id, faction.id, {"Statesman": "statesman:1a"}, FakeRandomResolver()
    )

    # Assert
    assert result.success
    family_senator.refresh_from_db()
    assert family_senator.id == original_id
    assert family_senator.code == "1a"
    assert family_senator.statesman_name == "P. Cornelius Scipio Africanus"
    assert family_senator.family is True
    assert family_senator.military == 5
    assert family_senator.oratory == 5
    assert family_senator.generation == original_generation


@pytest.mark.django_db
def test_play_statesman_removes_card_from_faction(basic_game: Game):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_play_phase(game, faction, ["statesman:1a"])

    # Act
    PlayStatesmanAction().execute(
        game.id, faction.id, {"Statesman": "statesman:1a"}, FakeRandomResolver()
    )

    # Assert
    faction.refresh_from_db()
    assert "statesman:1a" not in faction.cards


@pytest.mark.django_db
def test_play_statesman_blocked_when_opponent_controls_family_senator(basic_game: Game):
    # Arrange
    game = basic_game
    faction1: Faction = game.factions.get(position=1)
    faction2: Faction = game.factions.get(position=2)
    _setup_play_phase(game, faction2, ["statesman:1a"])
    assert Senator.objects.filter(
        game=game, faction=faction1, family_name="Cornelius"
    ).exists()
    snapshot = GameStateSnapshot(game.id)

    # Act
    result = PlayStatesmanAction().get_schema(snapshot, faction2.id)

    # Assert
    assert result == []


@pytest.mark.django_db
def test_play_statesman_independently_when_no_family_senator_exists(basic_game: Game):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_play_phase(game, faction, ["statesman:18a"])
    Senator.objects.filter(game=game, code="18").delete()

    # Act
    result = PlayStatesmanAction().execute(
        game.id, faction.id, {"Statesman": "statesman:18a"}, FakeRandomResolver()
    )

    # Assert
    assert result.success
    statesman = Senator.objects.get(game=game, code="18a")
    assert statesman.family is False
    assert statesman.statesman_name == "T. Quinctius Flamininus"
    assert statesman.faction == faction


@pytest.mark.django_db
def test_play_statesman_blocked_when_same_statesman_already_in_play(basic_game: Game):
    # Arrange
    game = basic_game
    faction1: Faction = game.factions.get(position=1)
    faction2: Faction = game.factions.get(position=2)
    _setup_play_phase(game, faction2, ["statesman:18a"])
    Senator.objects.create(
        game=game,
        faction=faction1,
        family_name="Flamininus",
        family=False,
        code="18a",
        statesman_name="T. Quinctius Flamininus",
        military=5,
        oratory=4,
        loyalty=7,
        influence=4,
    )
    snapshot = GameStateSnapshot(game.id)

    # Act
    result = PlayStatesmanAction().get_schema(snapshot, faction2.id)

    # Assert
    assert result == []


@pytest.mark.django_db
def test_play_statesman_upgrades_unaligned_family_senator_in_forum(basic_game: Game):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_play_phase(game, faction, ["statesman:1a"])
    family_senator = Senator.objects.get(game=game, code="1", family=True)
    family_senator.faction = None
    family_senator.save()

    # Act
    result = PlayStatesmanAction().execute(
        game.id, faction.id, {"Statesman": "statesman:1a"}, FakeRandomResolver()
    )

    # Assert
    assert result.success
    family_senator.refresh_from_db()
    assert family_senator.code == "1a"
    assert family_senator.faction == faction
    assert family_senator.statesman_name == "P. Cornelius Scipio Africanus"


@pytest.mark.django_db
def test_play_statesman_blocked_when_unaligned_senator_in_opponents_faction(
    basic_game: Game,
):
    # Arrange
    game = basic_game
    faction1: Faction = game.factions.get(position=1)
    faction2: Faction = game.factions.get(position=2)
    _setup_play_phase(game, faction2, ["statesman:1a"])
    assert Senator.objects.filter(
        game=game, code="1", faction=faction1, alive=True
    ).exists()
    snapshot = GameStateSnapshot(game.id)

    # Act
    result = PlayStatesmanAction().get_schema(snapshot, faction2.id)

    # Assert
    assert result == []


@pytest.mark.django_db
def test_play_statesman_available_when_family_senator_is_unaligned(basic_game: Game):
    # Arrange
    game = basic_game
    faction1: Faction = game.factions.get(position=1)
    faction2: Faction = game.factions.get(position=2)
    _setup_play_phase(game, faction2, ["statesman:1a"])
    family_senator = Senator.objects.get(game=game, code="1", family=True)
    family_senator.faction = None
    family_senator.save()
    snapshot = GameStateSnapshot(game.id)

    # Act
    result = PlayStatesmanAction().get_schema(snapshot, faction2.id)

    # Assert
    assert len(result) == 1
