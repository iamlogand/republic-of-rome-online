import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.models import Campaign, Game, Legion, Senator, War


@pytest.fixture
def revolution_game(basic_game: Game) -> Game:
    game = basic_game
    game.phase = Game.Phase.REVOLUTION
    game.sub_phase = Game.SubPhase.START
    game.save()
    return game


@pytest.fixture
def land_victor(revolution_game: Game) -> Campaign:
    game = revolution_game
    game.sub_phase = Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
    game.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    commander = Senator.objects.get(game=game, family_name="Cornelius")
    commander.add_title(Senator.Title.FIELD_CONSUL)
    commander.location = "Cisalpine Gaul"
    commander.save()

    war = War.objects.create(
        game=game,
        name="1st Gallic War",
        series_name="Gallic",
        index=0,
        land_strength=10,
        fleet_support=0,
        naval_strength=0,
        spoils=20,
        location="Cisalpine Gaul",
        status=War.Status.DEFEATED,
    )
    campaign = Campaign.objects.create(game=game, war=war, commander=commander)
    for i in range(1, 6):
        Legion.objects.create(game=game, number=i, campaign=campaign)
    return campaign
