import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rorapp.models import Faction, Game


@pytest.fixture
def three_player_game() -> Game:
    host = User.objects.create_user(username="host", password="password")
    game = Game.objects.create(name="Test Game", host=host)
    for i in range(1, 4):
        player = User.objects.create_user(username=f"player{i}", password="password")
        Faction.objects.create(game=game, player=player, position=i)
    return game


def _start_game(game: Game):
    client = APIClient()
    client.force_authenticate(user=game.host)
    return client.post(f"/api/games/{game.id}/start-game/")


@pytest.mark.django_db
def test_initial_deal_gives_each_faction_3_cards(three_player_game: Game):
    # Arrange
    game = three_player_game

    # Act
    response = _start_game(game)

    # Assert
    assert response.status_code == 200
    for faction in Faction.objects.filter(game=game):
        assert len(faction.cards) == 3
        for card in faction.cards:
            assert not card.startswith("war:")


@pytest.mark.django_db
def test_initial_deal_war_cards_stay_in_deck(three_player_game: Game):
    # Arrange
    game = three_player_game

    # Act
    response = _start_game(game)

    # Assert
    assert response.status_code == 200
    game.refresh_from_db()
    for faction in Faction.objects.filter(game=game):
        assert all(not c.startswith("war:") for c in faction.cards)



@pytest.mark.django_db
def test_statesman_cards_in_initial_deck_or_hands(three_player_game: Game):
    # Arrange
    game = three_player_game

    # Act
    response = _start_game(game)

    # Assert
    assert response.status_code == 200
    game.refresh_from_db()
    all_cards = list(game.deck)
    for faction in Faction.objects.filter(game=game):
        all_cards.extend(faction.cards)
    statesman_cards = [c for c in all_cards if c.startswith("statesman:")]
    statesman_codes = {c.split(":")[1] for c in statesman_cards}
    assert statesman_codes == {"1a", "2a", "18a", "19a", "22a"}


@pytest.mark.django_db
def test_senator_cards_for_unassigned_senators_are_in_deck(three_player_game: Game):
    # Arrange
    game = three_player_game

    # Act
    response = _start_game(game)

    # Assert
    assert response.status_code == 200
    game.refresh_from_db()
    senator_cards = [c for c in game.deck if c.startswith("senator:")]
    assert len(senator_cards) > 0
    assigned_codes = {
        str(s.code)
        for faction in Faction.objects.filter(game=game)
        for s in faction.senators.all()
    }
    deck_senator_codes = {c.split(":")[1] for c in senator_cards}
    assert deck_senator_codes.isdisjoint(assigned_codes)


@pytest.mark.django_db
def test_intrigue_cards_in_initial_deck_or_hands(three_player_game: Game):
    # Arrange
    game = three_player_game

    # Act
    response = _start_game(game)

    # Assert
    assert response.status_code == 200
    game.refresh_from_db()
    all_cards = list(game.deck)
    for faction in Faction.objects.filter(game=game):
        all_cards.extend(faction.cards)
    assert all_cards.count("tribune") == 7
    assert all_cards.count("assassin") == 1
    assert all_cards.count("blackmail") == 1
    assert all_cards.count("influence peddling") == 1
    assert all_cards.count("secret bodyguard") == 1
    assert all_cards.count("seduction") == 1


@pytest.mark.django_db
def test_senator_cards_in_deck_have_no_duplicates(three_player_game: Game):
    # Arrange
    game = three_player_game

    # Act
    response = _start_game(game)

    # Assert
    assert response.status_code == 200
    game.refresh_from_db()
    senator_cards = [c for c in game.deck if c.startswith("senator:")]
    assert len(senator_cards) == len(set(senator_cards))
