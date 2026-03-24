import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Campaign, Fleet, Game, Legion, Senator, War
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_naval_victory_with_all_fleets_lost_not_unprosecuted(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.END
    game.save()

    war = War.objects.create(
        game=game,
        name="1st Punic War",
        series_name="Punic",
        index=0,
        land_strength=10,
        fleet_support=5,
        naval_strength=0,
        fought_naval_battle=True,
        disaster_numbers=[13],
        standoff_numbers=[11, 14],
        spoils=35,
        location="Sicilia",
        status=War.Status.ACTIVE,
    )

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    war.refresh_from_db()
    assert war.unprosecuted == False


@pytest.mark.django_db
def test_land_battle_with_insufficient_fleet_support_is_unprosecuted(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.END
    game.save()

    war = War.objects.create(
        game=game,
        name="1st Punic War",
        series_name="Punic",
        index=0,
        land_strength=10,
        fleet_support=2,
        naval_strength=0,
        fought_land_battle=True,
        disaster_numbers=[13],
        standoff_numbers=[11, 14],
        spoils=35,
        location="Sicilia",
        status=War.Status.ACTIVE,
    )

    senator = Senator.objects.get(game=game, family_name="Cornelius")
    campaign = Campaign.objects.create(game=game, war=war, commander=senator)
    Legion.objects.create(game=game, number=1, campaign=campaign)
    Fleet.objects.create(game=game, number=1, campaign=campaign)  # 1 fleet, below fleet_support=2

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    war.refresh_from_db()
    assert war.unprosecuted == True


@pytest.mark.django_db
def test_land_battle_with_sufficient_fleet_support_not_unprosecuted(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.END
    game.save()

    war = War.objects.create(
        game=game,
        name="1st Punic War",
        series_name="Punic",
        index=0,
        land_strength=10,
        fleet_support=2,
        naval_strength=0,
        fought_land_battle=True,
        disaster_numbers=[13],
        standoff_numbers=[11, 14],
        spoils=35,
        location="Sicilia",
        status=War.Status.ACTIVE,
    )

    senator = Senator.objects.get(game=game, family_name="Cornelius")
    campaign = Campaign.objects.create(game=game, war=war, commander=senator)
    Legion.objects.create(game=game, number=1, campaign=campaign)
    Fleet.objects.create(game=game, number=1, campaign=campaign)
    Fleet.objects.create(game=game, number=2, campaign=campaign)  # 2 fleets meet fleet_support=2

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    war.refresh_from_db()
    assert war.unprosecuted == False


@pytest.mark.django_db
def test_prosecuted_war_clears_unprosecuted_flag(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.END
    game.save()

    war = War.objects.create(
        game=game,
        name="1st Gallic War",
        series_name="Gallic",
        index=0,
        land_strength=10,
        fleet_support=0,
        naval_strength=0,
        fought_land_battle=True,
        unprosecuted=True,
        disaster_numbers=[13],
        standoff_numbers=[15],
        spoils=20,
        location="Cisalpine Gaul",
        status=War.Status.ACTIVE,
    )

    senator = Senator.objects.get(game=game, family_name="Cornelius")
    campaign = Campaign.objects.create(game=game, war=war, commander=senator)
    Legion.objects.create(game=game, number=1, campaign=campaign)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    war.refresh_from_db()
    assert war.unprosecuted == False
