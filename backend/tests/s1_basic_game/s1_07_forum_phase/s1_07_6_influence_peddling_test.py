import pytest
from rorapp.actions.play_influence_peddling import PlayInfluencePeddlingAction
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.models import Faction, Game


@pytest.mark.django_db
def test_influence_peddling_transfers_card_from_opponent(
    forum_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = forum_game
    faction: Faction = game.factions.get(position=1)
    faction.cards = ["influence peddling"]
    faction.save()

    opponent: Faction = game.factions.get(position=2)
    opponent.cards = ["tribune"]
    opponent.save()

    # Act
    result = PlayInfluencePeddlingAction().execute(
        game.id,
        faction.id,
        {"Opponent": f"faction:{opponent.id}"},
        resolver,
    )

    # Assert
    assert result.success
    faction.refresh_from_db()
    opponent.refresh_from_db()
    assert "influence peddling" not in faction.cards
    assert "tribune" in faction.cards
    assert "tribune" not in opponent.cards


@pytest.mark.django_db
def test_influence_peddling_not_allowed_during_revolution_phase(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.REVOLUTION
    game.sub_phase = Game.SubPhase.CARD_TRADING
    game.save()

    faction: Faction = game.factions.get(position=1)
    faction.cards = ["influence peddling"]
    faction.save()

    opponent: Faction = game.factions.get(position=2)
    opponent.cards = ["tribune"]
    opponent.save()

    # Act / Assert
    game_state = GameStateLive(game.id)
    assert PlayInfluencePeddlingAction().is_allowed(game_state, faction.id) is None


@pytest.mark.django_db
def test_influence_peddling_allowed_during_senate_phase(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()

    faction: Faction = game.factions.get(position=1)
    faction.cards = ["influence peddling"]
    faction.save()

    opponent: Faction = game.factions.get(position=2)
    opponent.cards = ["tribune"]
    opponent.save()

    # Act / Assert
    game_state = GameStateLive(game.id)
    assert PlayInfluencePeddlingAction().is_allowed(game_state, faction.id) is not None
