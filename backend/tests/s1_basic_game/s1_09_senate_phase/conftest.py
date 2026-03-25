import pytest
from rorapp.classes.concession import Concession
from rorapp.models import Campaign, Game, Senator, War


@pytest.fixture
def senate_game(basic_game: Game) -> Game:
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    senator = Senator.objects.filter(game=game, alive=True).first()
    assert senator is not None
    senator.add_title(Senator.Title.ROME_CONSUL)
    senator.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    senator.add_title(Senator.Title.HRAO)
    senator.save()
    return game


@pytest.fixture
def senate_censor_game(basic_game: Game) -> Game:
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.CENSOR_ELECTION
    game.save()
    senators = list(Senator.objects.filter(game=game, alive=True))
    senators[0].add_title(Senator.Title.ROME_CONSUL)
    senators[0].add_title(Senator.Title.HRAO)
    senators[0].add_title(Senator.Title.PRESIDING_MAGISTRATE)
    senators[0].save()
    return game


@pytest.fixture
def senate_prosecution_game(basic_game: Game) -> Game:
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.PROSECUTION
    game.prosecutions_remaining = 2
    game.save()
    senators = list(Senator.objects.filter(game=game, alive=True))
    senators[0].add_title(Senator.Title.CENSOR)
    senators[0].add_title(Senator.Title.PRESIDING_MAGISTRATE)
    senators[0].save()
    senators[1].add_status_item(Senator.StatusItem.CORRUPT)
    senators[1].save()
    return game


@pytest.fixture
def prosecution_setup(senate_prosecution_game: Game):
    senators = list(Senator.objects.filter(game=senate_prosecution_game, alive=True))
    julius = senators[0]
    cornelius = senators[1]
    scipio = senators[2]

    julius.add_title(Senator.Title.ROME_CONSUL)
    julius.add_title(Senator.Title.HRAO)
    julius.add_title(Senator.Title.CENSOR)
    julius.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    julius.save()

    cornelius.add_status_item(Senator.StatusItem.CORRUPT)
    cornelius.influence = 7
    cornelius.add_title(Senator.Title.PRIOR_CONSUL)
    cornelius.add_concession(Concession.AEGYPTIAN_GRAIN)
    cornelius.save()

    return senate_prosecution_game, julius, cornelius, scipio


@pytest.fixture
def proconsul_campaign(senate_game: Game) -> Game:
    game = senate_game
    julius = Senator.objects.get(game=game, family_name="Julius")
    julius.add_title(Senator.Title.PROCONSUL)
    julius.location = "Sicilia"
    julius.save()
    war = War.objects.create(
        game=game,
        name="1st Punic War",
        series_name="Punic",
        index=0,
        land_strength=10,
        fleet_support=5,
        naval_strength=0,
        disaster_numbers=[13],
        standoff_numbers=[11, 14],
        spoils=35,
        location="Sicilia",
        status=War.Status.ACTIVE,
    )
    Campaign.objects.create(
        game=game,
        commander=julius,
        war=war,
        recently_deployed=False,
        recently_reinforced=False,
    )
    return game
