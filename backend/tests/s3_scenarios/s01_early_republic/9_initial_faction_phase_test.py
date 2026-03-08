import pytest
from rorapp.actions.done import DoneAction
from rorapp.actions.play_concession import PlayConcessionAction
from rorapp.classes.concession import Concession
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Senator


def _setup_initial_play_cards(basic_game: Game):
    game = basic_game
    game.phase = Game.Phase.INITIAL
    game.sub_phase = Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
    game.save()

    senators = list(Senator.objects.filter(game=game, alive=True))
    julius = senators[0]
    julius.add_title(Senator.Title.ROME_CONSUL)
    julius.add_title(Senator.Title.HRAO)
    julius.save()

    assert julius.faction_id is not None
    hrao_faction = Faction.objects.get(id=julius.faction_id)
    hrao_faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
    hrao_faction.save()

    return game, julius, hrao_faction


@pytest.mark.django_db
def test_play_concession_during_initial_play_cards_phase(basic_game: Game):
    # Arrange
    game, julius, hrao_faction = _setup_initial_play_cards(basic_game)
    hrao_faction.cards = [f"concession:{Concession.MINING.value}"]
    hrao_faction.save()

    # Act
    result = PlayConcessionAction().execute(
        game.id,
        hrao_faction.id,
        {"Senator": str(julius.id), "Concession": f"concession:{Concession.MINING.value}"},
        FakeRandomResolver(),
    )

    # Assert
    assert result.success
    julius.refresh_from_db()
    assert Concession.MINING.value in julius.concessions
    hrao_faction.refresh_from_db()
    assert f"concession:{Concession.MINING.value}" not in hrao_faction.cards


@pytest.mark.django_db
def test_play_concession_not_available_without_awaiting_decision(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.INITIAL
    game.sub_phase = Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
    game.save()

    faction: Faction = game.factions.get(position=1)
    faction.cards = [f"concession:{Concession.MINING.value}"]
    faction.save()

    snapshot = GameStateSnapshot(game.id)

    # Act
    result = PlayConcessionAction().get_schema(snapshot, faction.id)

    # Assert
    assert result == []


@pytest.mark.django_db
def test_done_passes_awaiting_decision_to_next_faction(basic_game: Game):
    # Arrange
    game, julius, hrao_faction = _setup_initial_play_cards(basic_game)
    other_factions = list(
        Faction.objects.filter(game=game).exclude(id=hrao_faction.id).order_by("position")
    )
    next_faction = other_factions[0]

    # Act
    DoneAction().execute(game.id, hrao_faction.id, {}, FakeRandomResolver())

    # Assert
    hrao_faction.refresh_from_db()
    next_faction.refresh_from_db()
    assert hrao_faction.has_status_item(FactionStatusItem.DONE)
    assert not hrao_faction.has_status_item(FactionStatusItem.AWAITING_DECISION)
    assert next_faction.has_status_item(FactionStatusItem.AWAITING_DECISION)


@pytest.mark.django_db
def test_initial_play_cards_done_advances_to_mortality(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game, julius, hrao_faction = _setup_initial_play_cards(basic_game)
    for faction in Faction.objects.filter(game=game):
        faction.remove_status_item(FactionStatusItem.AWAITING_DECISION)
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.phase != Game.Phase.INITIAL


@pytest.mark.django_db
def test_initial_phase_done_advances_to_play_cards(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.INITIAL
    game.sub_phase = Game.SubPhase.FACTION_LEADER
    game.save()

    senators = list(Senator.objects.filter(game=game, alive=True))
    julius = senators[0]
    julius.add_title(Senator.Title.HRAO)
    julius.save()

    for faction in Faction.objects.filter(game=game):
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.phase == Game.Phase.INITIAL
    assert game.sub_phase == Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
    assert julius.faction_id is not None
    hrao_faction = Faction.objects.get(id=julius.faction_id)
    assert hrao_faction.has_status_item(FactionStatusItem.AWAITING_DECISION)


@pytest.mark.django_db
def test_tribune_in_faction_cards_not_playable_as_concession(basic_game: Game):
    # Arrange
    game, julius, hrao_faction = _setup_initial_play_cards(basic_game)
    hrao_faction.cards = ["tribune", "tribune"]
    hrao_faction.save()

    snapshot = GameStateSnapshot(game.id)

    # Act
    result = PlayConcessionAction().get_schema(snapshot, hrao_faction.id)

    # Assert
    assert result == []
