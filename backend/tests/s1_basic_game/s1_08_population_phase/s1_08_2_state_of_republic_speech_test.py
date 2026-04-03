import pytest
from rorapp.actions.give_speech import GiveSpeechAction
from rorapp.classes.game_effect_item import GameEffect
from rorapp.models import Game, Senator


def _get_hrao(game: Game) -> Senator:
    senator = Senator.objects.filter(
        game=game, titles__contains=[Senator.Title.HRAO.value]
    ).first()
    assert senator
    return senator


@pytest.mark.django_db
@pytest.mark.parametrize(
    "initial_unrest,popularity,dice_roll,expected_unrest,expect_game_over",
    [
        (0, 0, 12, 0, False),  # result 12 → no change
        (0, 0, 9, 2, False),  # result 9  → +2
        (0, 0, 8, 3, False),  # result 8  → +3
        (0, 0, 6, 4, False),  # result 6  → +4
        (0, 0, 4, 5, False),  # result 4  → +5
        (3, 0, 3, 9, False),  # result 0  → +6
        (5, 3, 18, 4, False),  # result 16 → -1
        (5, 4, 18, 3, False),  # result 17 → -2
        (5, 5, 18, 2, False),  # result 18 → -3
        (5, 0, 3, 0, True),  # result -2 → People Revolt
    ],
)
def test_speech_unrest_outcome(
    population_game,
    resolver,
    initial_unrest,
    popularity,
    dice_roll,
    expected_unrest,
    expect_game_over,
):
    # Arrange
    game = population_game
    game.unrest = initial_unrest
    game.save()
    hrao = _get_hrao(game)
    hrao.popularity = popularity
    hrao.save()
    resolver.dice_rolls = [dice_roll]

    # Act
    GiveSpeechAction().execute(game.id, hrao.faction_id, {}, resolver)

    # Assert
    game.refresh_from_db()
    if expect_game_over:
        assert game.finished_on is not None
        assert game.phase == Game.Phase.POPULATION
    else:
        assert game.finished_on is None
        assert game.unrest == expected_unrest
        assert game.phase == Game.Phase.SENATE


@pytest.mark.django_db
def test_speech_adds_no_recruitment(population_game, resolver):
    # Arrange — result 2 triggers NR (+5 unrest, no mob)
    resolver.dice_rolls = [2]  # result = 2 - 0 + 0 = 2

    # Act
    hrao = _get_hrao(population_game)
    GiveSpeechAction().execute(population_game.id, hrao.faction_id, {}, resolver)

    # Assert
    population_game.refresh_from_db()
    assert population_game.has_effect(GameEffect.NO_RECRUITMENT)


@pytest.mark.django_db
def test_speech_adds_manpower_shortage(population_game, resolver):
    # Arrange — result 3 triggers MS (+5 unrest)
    resolver.dice_rolls = [3]  # result = 3 - 0 + 0 = 3

    # Act
    hrao = _get_hrao(population_game)
    GiveSpeechAction().execute(population_game.id, hrao.faction_id, {}, resolver)

    # Assert
    population_game.refresh_from_db()
    assert population_game.has_effect(GameEffect.MANPOWER_SHORTAGE)


@pytest.mark.django_db
def test_speech_mob_kills_senator_in_rome(population_game, resolver):
    # Arrange — result 1 triggers mob (+5 unrest, NR)
    hrao = _get_hrao(population_game)
    target = (
        Senator.objects.filter(game=population_game, alive=True, faction__isnull=False)
        .exclude(id=hrao.id)
        .first()
    )
    target.location = "Rome"
    target.save()
    resolver.dice_rolls = [1]  # result = 1 - 0 + 0 = 1 → mob
    resolver.mortality_chits = [target.code]

    # Act
    GiveSpeechAction().execute(population_game.id, hrao.faction_id, {}, resolver)

    # Assert
    target.refresh_from_db()
    assert not target.alive


@pytest.mark.django_db
def test_speech_mob_spares_senator_not_in_rome(population_game, resolver):
    # Arrange — result 1 triggers mob, but target senator is not in Rome
    hrao = _get_hrao(population_game)
    target = (
        Senator.objects.filter(game=population_game, alive=True, faction__isnull=False)
        .exclude(id=hrao.id)
        .first()
    )
    target.location = "Sicilia"
    target.save()
    resolver.dice_rolls = [1]  # result = 1 → mob
    resolver.mortality_chits = [target.code]

    # Act
    GiveSpeechAction().execute(population_game.id, hrao.faction_id, {}, resolver)

    # Assert
    target.refresh_from_db()
    assert target.alive
