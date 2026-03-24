import pytest
from rorapp.models import Campaign, Game, Senator, War


@pytest.fixture
def land_campaign(basic_game: Game):
    game = basic_game
    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.START
    game.unrest = 3
    game.save()

    war = War.objects.create(
        game=game,
        name="1st Gallic War",
        series_name="Gallic",
        index=0,
        land_strength=10,
        fleet_support=0,
        naval_strength=0,
        disaster_numbers=[13],
        standoff_numbers=[15],
        spoils=20,
        location="Cisalpine Gaul",
        status=War.Status.ACTIVE,
    )

    commander = Senator.objects.get(game=game, family_name="Cornelius")
    commander.add_title(Senator.Title.FIELD_CONSUL)
    commander.location = war.location
    commander.save()

    return Campaign.objects.create(game=game, war=war, commander=commander)


@pytest.fixture
def naval_campaign(basic_game: Game):
    game = basic_game
    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.START
    game.unrest = 3
    game.save()

    war = War.objects.create(
        game=game,
        name="1st Punic War",
        series_name="Punic",
        index=0,
        land_strength=10,
        fleet_support=5,
        naval_strength=10,
        disaster_numbers=[13],
        standoff_numbers=[11, 14],
        spoils=35,
        location="Sicilia",
        status=War.Status.ACTIVE,
    )

    commander = Senator.objects.get(game=game, family_name="Cornelius")
    commander.add_title(Senator.Title.FIELD_CONSUL)
    commander.location = war.location
    commander.save()

    return Campaign.objects.create(game=game, war=war, commander=commander)


@pytest.fixture
def two_campaigns(basic_game: Game):
    game = basic_game
    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.RESOLUTION
    game.unrest = 3
    game.save()

    war = War.objects.create(
        game=game,
        name="1st Gallic War",
        series_name="Gallic",
        index=0,
        land_strength=10,
        fleet_support=0,
        naval_strength=0,
        disaster_numbers=[13],
        standoff_numbers=[15],
        spoils=20,
        location="Cisalpine Gaul",
        status=War.Status.ACTIVE,
    )

    commander1 = Senator.objects.get(game=game, family_name="Cornelius")
    commander1.add_title(Senator.Title.FIELD_CONSUL)
    commander1.location = war.location
    commander1.save()

    commander2 = Senator.objects.get(game=game, family_name="Julius")
    commander2.add_title(Senator.Title.ROME_CONSUL)
    commander2.location = war.location
    commander2.save()

    campaign1 = Campaign.objects.create(game=game, war=war, commander=commander1, imminent=True)
    campaign2 = Campaign.objects.create(game=game, war=war, commander=commander2, imminent=True)

    return (campaign1, campaign2)
