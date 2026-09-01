import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Faction, Game, Senator


def _senators(game: Game) -> list:
    return list(Senator.objects.filter(game=game, alive=True).order_by("id"))


@pytest.mark.django_db
def test_senator_with_35_influence_becomes_consul_for_life(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    senator = _senators(game)[0]
    senator.influence = 35
    senator.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    senator.refresh_from_db()
    game.refresh_from_db()
    assert senator.has_title(Senator.Title.CONSUL_FOR_LIFE)
    assert game.consul_for_life_appointed


@pytest.mark.django_db
def test_senator_with_34_influence_is_not_appointed(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    senator = _senators(game)[0]
    senator.influence = 34
    senator.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    senator.refresh_from_db()
    assert not senator.has_title(Senator.Title.CONSUL_FOR_LIFE)


@pytest.mark.django_db
def test_appointment_happens_outside_the_senate_phase(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.REVENUE
    game.sub_phase = Game.SubPhase.REDISTRIBUTION
    game.save()
    senator = _senators(game)[0]
    senator.influence = 35
    senator.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    senator.refresh_from_db()
    assert senator.has_title(Senator.Title.CONSUL_FOR_LIFE)


@pytest.mark.django_db
def test_senator_outside_rome_is_not_appointed(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    senator = _senators(game)[0]
    senator.influence = 40
    senator.location = "Sicilia"
    senator.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    senator.refresh_from_db()
    assert not senator.has_title(Senator.Title.CONSUL_FOR_LIFE)


@pytest.mark.django_db
def test_unaligned_senator_is_not_appointed(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    senator = _senators(game)[0]
    senator.influence = 40
    senator.faction = None
    senator.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    senator.refresh_from_db()
    assert not senator.has_title(Senator.Title.CONSUL_FOR_LIFE)


@pytest.mark.django_db
def test_highest_influence_wins_when_two_senators_qualify(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    senators = _senators(game)
    senators[0].influence = 36
    senators[0].save()
    senators[1].influence = 40
    senators[1].save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    senators[0].refresh_from_db()
    senators[1].refresh_from_db()
    assert not senators[0].has_title(Senator.Title.CONSUL_FOR_LIFE)
    assert senators[1].has_title(Senator.Title.CONSUL_FOR_LIFE)


@pytest.mark.django_db
def test_influence_tie_broken_by_combined_faction_influence(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    faction1: Faction = game.factions.get(position=1)
    faction2: Faction = game.factions.get(position=2)
    Senator.objects.filter(game=game, faction=faction1).update(influence=1)
    Senator.objects.filter(game=game, faction=faction2).update(influence=10)
    weaker = Senator.objects.filter(game=game, faction=faction1).order_by("id").first()
    stronger = Senator.objects.filter(game=game, faction=faction2).order_by("id").first()
    assert weaker is not None and stronger is not None
    weaker.influence = 35
    weaker.save()
    stronger.influence = 35
    stronger.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    weaker.refresh_from_db()
    stronger.refresh_from_db()
    assert not weaker.has_title(Senator.Title.CONSUL_FOR_LIFE)
    assert stronger.has_title(Senator.Title.CONSUL_FOR_LIFE)


@pytest.mark.django_db
def test_appointment_supersedes_an_elected_consul_for_life(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    senators = _senators(game)
    elected = senators[0]
    elected.add_title(Senator.Title.CONSUL_FOR_LIFE)
    elected.save()
    appointee = senators[1]
    appointee.influence = 35
    appointee.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    elected.refresh_from_db()
    appointee.refresh_from_db()
    assert not elected.has_title(Senator.Title.CONSUL_FOR_LIFE)
    assert appointee.has_title(Senator.Title.CONSUL_FOR_LIFE)


@pytest.mark.django_db
def test_appointed_consul_for_life_is_not_displaced_by_a_later_qualifier(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    senators = _senators(game)
    senators[0].influence = 35
    senators[0].save()
    execute_effects_and_manage_actions(game.id, resolver)
    senators[1].influence = 50
    senators[1].save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    senators[0].refresh_from_db()
    senators[1].refresh_from_db()
    assert senators[0].has_title(Senator.Title.CONSUL_FOR_LIFE)
    assert not senators[1].has_title(Senator.Title.CONSUL_FOR_LIFE)


@pytest.mark.django_db
def test_appointment_grants_no_influence_and_no_offices(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    senator = _senators(game)[1]
    senator.influence = 35
    senator.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    senator.refresh_from_db()
    assert senator.influence == 35
    assert not senator.has_title(Senator.Title.PRESIDING_MAGISTRATE)
    assert not senator.has_title(Senator.Title.HRAO)
