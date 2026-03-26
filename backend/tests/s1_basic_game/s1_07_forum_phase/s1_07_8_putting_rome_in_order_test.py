import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Game, Senator
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_major_corrupt_marker_assigned_at_senate_start(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.START
    game.save()

    senators = list(Senator.objects.filter(game=game, alive=True))
    julius = senators[0]
    julius.add_title(Senator.Title.ROME_CONSUL)
    julius.add_title(Senator.Title.HRAO)
    julius.location = "Rome"
    julius.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    julius.refresh_from_db()
    assert julius.has_status_item(Senator.StatusItem.MAJOR_CORRUPT)


def _setup_putting_rome_in_order(game: Game) -> Game:
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.PUTTING_ROME_IN_ORDER
    game.save()
    return game


@pytest.mark.django_db
def test_dead_senator_revived_on_high_roll(basic_game: Game):
    # Arrange
    game = _setup_putting_rome_in_order(basic_game)
    dead_senator = Senator.objects.filter(game=game, family=True).first()
    assert dead_senator is not None
    dead_senator.alive = False
    dead_senator.faction = None
    dead_senator.save()
    original_generation = dead_senator.generation
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [5]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    dead_senator.refresh_from_db()
    assert dead_senator.alive is True
    assert dead_senator.faction is None
    assert dead_senator.generation == original_generation + 1


@pytest.mark.django_db
def test_dead_senator_stays_dead_on_low_roll(basic_game: Game):
    # Arrange
    game = _setup_putting_rome_in_order(basic_game)
    dead_senator = Senator.objects.filter(game=game, family=True).first()
    assert dead_senator is not None
    dead_senator.alive = False
    dead_senator.faction = None
    dead_senator.save()
    original_generation = dead_senator.generation
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [4]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    dead_senator.refresh_from_db()
    assert dead_senator.alive is False
    assert dead_senator.generation == original_generation


@pytest.mark.django_db
def test_putting_rome_in_order_advances_past_forum_phase(basic_game: Game):
    # Arrange
    game = _setup_putting_rome_in_order(basic_game)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = []
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert — the effect must advance the game out of FORUM/PUTTING_ROME_IN_ORDER
    game.refresh_from_db()
    assert not (
        game.phase == Game.Phase.FORUM
        and game.sub_phase == Game.SubPhase.PUTTING_ROME_IN_ORDER
    )


@pytest.mark.django_db
def test_putting_rome_in_order_with_multiple_dead_senators_uses_separate_rolls(
    basic_game: Game,
):
    # Arrange
    game = _setup_putting_rome_in_order(basic_game)
    senators = list(Senator.objects.filter(game=game, family=True)[:2])
    assert len(senators) == 2
    for s in senators:
        s.alive = False
        s.faction = None
        s.save()
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [6, 3]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    senators[0].refresh_from_db()
    senators[1].refresh_from_db()
    alive_states = sorted([senators[0].alive, senators[1].alive])
    assert alive_states == [False, True]
