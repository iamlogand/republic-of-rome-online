import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Campaign, Game, Legion, Senator, War
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


def _setup_land_campaign(basic_game: Game, extra_matching_war: bool) -> Campaign:
    game = basic_game
    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.START
    game.save()

    war = War.objects.create(
        game=game,
        name="1st Gallic War",
        series_name="Gallic",
        index=0,
        land_strength=3,
        fleet_support=0,
        naval_strength=0,
        disaster_numbers=[],
        standoff_numbers=[],
        spoils=20,
        location="Cisalpine Gaul",
        status=War.Status.ACTIVE,
    )

    if extra_matching_war:
        War.objects.create(
            game=game,
            name="2nd Gallic War",
            series_name="Gallic",
            index=1,
            land_strength=3,
            fleet_support=0,
            naval_strength=0,
            disaster_numbers=[],
            standoff_numbers=[],
            spoils=20,
            location="Transalpine Gaul",
            status=War.Status.ACTIVE,
        )

    commander = Senator.objects.get(game=game, family_name="Cornelius")
    commander.add_title(Senator.Title.FIELD_CONSUL)
    commander.location = war.location
    commander.save()

    return Campaign.objects.create(game=game, war=war, commander=commander)


def _setup_naval_campaign(basic_game: Game, extra_matching_war: bool) -> Campaign:
    game = basic_game
    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.START
    game.save()

    war = War.objects.create(
        game=game,
        name="1st Punic War",
        series_name="Punic",
        index=0,
        land_strength=3,
        fleet_support=0,
        naval_strength=3,
        disaster_numbers=[],
        standoff_numbers=[],
        spoils=35,
        location="Sicilia",
        status=War.Status.ACTIVE,
    )

    if extra_matching_war:
        War.objects.create(
            game=game,
            name="2nd Punic War",
            series_name="Punic",
            index=1,
            land_strength=3,
            fleet_support=0,
            naval_strength=3,
            disaster_numbers=[],
            standoff_numbers=[],
            spoils=35,
            location="Africa",
            status=War.Status.ACTIVE,
        )

    commander = Senator.objects.get(game=game, family_name="Cornelius")
    commander.add_title(Senator.Title.FIELD_CONSUL)
    commander.location = war.location
    commander.save()

    return Campaign.objects.create(game=game, war=war, commander=commander)


@pytest.mark.django_db
def test_single_active_war_uses_base_land_strength(basic_game: Game):
    # Arrange
    campaign = _setup_land_campaign(basic_game, extra_matching_war=False)
    game = campaign.game
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [3]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert not War.objects.filter(game=game, series_name="Gallic").exists()


@pytest.mark.django_db
def test_two_matching_active_wars_double_land_strength(basic_game: Game):
    # Arrange
    campaign = _setup_land_campaign(basic_game, extra_matching_war=True)
    game = campaign.game
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [3]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert War.objects.filter(game=game, name="1st Gallic War").exists()


@pytest.mark.django_db
def test_single_active_war_uses_base_naval_strength(basic_game: Game):
    # Arrange
    campaign = _setup_naval_campaign(basic_game, extra_matching_war=False)
    game = campaign.game
    for i in range(1, 11):
        from rorapp.models.fleet import Fleet

        Fleet.objects.create(game=game, number=i, campaign=campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [3]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert War.objects.filter(
        game=game, name="1st Punic War", naval_strength=0
    ).exists()


@pytest.mark.django_db
def test_two_matching_active_wars_double_naval_strength(basic_game: Game):
    # Arrange
    campaign = _setup_naval_campaign(basic_game, extra_matching_war=True)
    game = campaign.game
    for i in range(1, 11):
        from rorapp.models.fleet import Fleet

        Fleet.objects.create(game=game, number=i, campaign=campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [3]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert War.objects.filter(
        game=game, name="1st Punic War", naval_strength=3
    ).exists()
