import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.models import Campaign, Game, Legion, Senator


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

    campaign = Campaign.objects.create(
        game=game, war=None, commander=commander, land_victory=True
    )
    for i in range(1, 6):
        Legion.objects.create(game=game, number=i, campaign=campaign)
    return campaign
