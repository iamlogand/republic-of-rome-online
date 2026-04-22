import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Game, Senator


def _setup_caught_assassin(
    game: Game,
    assassin: Senator,
    target: Senator,
    roll_result: int = 1,
):
    """Set up game for ResolveAssassinationEffect with a caught assassin."""
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.ASSASSINATION_RESOLUTION
    game.assassination_roll_result = roll_result
    game.assassination_roll_modifier = 0
    game.bodyguard_rerolls_remaining = 0
    game.interrupted_sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    assassin.add_status_item(Senator.StatusItem.ASSASSIN)
    assassin.add_status_item(Senator.StatusItem.CAUGHT)
    assassin.save()
    target.add_status_item(Senator.StatusItem.ASSASSINATION_TARGET)
    target.save()


@pytest.mark.django_db
def test_caught_assassin_is_killed(senate_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    _setup_caught_assassin(game, cornelius, claudius)
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    cornelius.refresh_from_db()
    assert not cornelius.alive


@pytest.mark.django_db
def test_faction_leader_loses_5_influence_when_assassin_is_not_fl(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    fabius = Senator.objects.get(game=game, family_name="Fabius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")

    fabius.add_title(Senator.Title.FACTION_LEADER)
    fabius.influence = 10
    fabius.save()
    _setup_caught_assassin(game, cornelius, claudius)
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    fabius.refresh_from_db()
    assert fabius.influence == 5


@pytest.mark.django_db
def test_faction_leader_influence_capped_at_zero(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    fabius = Senator.objects.get(game=game, family_name="Fabius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")

    fabius.add_title(Senator.Title.FACTION_LEADER)
    fabius.influence = 3
    fabius.save()
    _setup_caught_assassin(game, cornelius, claudius)
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    fabius.refresh_from_db()
    assert fabius.influence == 0


@pytest.mark.django_db
def test_chit_draws_equal_target_popularity_when_positive(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    fabius = Senator.objects.get(game=game, family_name="Fabius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    valerius = Senator.objects.get(game=game, family_name="Valerius")

    fabius.add_title(Senator.Title.FACTION_LEADER)
    fabius.influence = 10
    fabius.save()
    claudius.popularity = 2
    claudius.save()
    _setup_caught_assassin(game, cornelius, claudius)
    resolver.mortality_chits = ["3", "99"]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    valerius.refresh_from_db()
    assert not valerius.alive
    fabius.refresh_from_db()
    assert fabius.alive


@pytest.mark.django_db
def test_no_chit_draws_when_target_popularity_is_zero(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    fabius = Senator.objects.get(game=game, family_name="Fabius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")

    fabius.add_title(Senator.Title.FACTION_LEADER)
    fabius.save()
    claudius.popularity = 0
    claudius.save()
    _setup_caught_assassin(game, cornelius, claudius)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    fabius.refresh_from_db()
    assert fabius.alive


@pytest.mark.django_db
def test_caught_assassin_who_is_faction_leader_is_killed_automatically(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")

    cornelius.add_title(Senator.Title.FACTION_LEADER)
    cornelius.save()
    _setup_caught_assassin(game, cornelius, claudius)
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    cornelius.refresh_from_db()
    assert not cornelius.alive or cornelius.generation > 1


@pytest.mark.django_db
def test_no_other_fl_influence_loss_when_fl_was_the_assassin(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    fabius = Senator.objects.get(game=game, family_name="Fabius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")

    cornelius.add_title(Senator.Title.FACTION_LEADER)
    cornelius.save()
    fabius.influence = 10
    fabius.save()
    _setup_caught_assassin(game, cornelius, claudius)
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    fabius.refresh_from_db()
    assert fabius.influence == 10
