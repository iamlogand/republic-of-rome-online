from typing import Callable, Optional, Sequence

import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.helpers.force_strength import force_strength
from rorapp.models import Campaign, Fleet, Game, Legion, Senator, War


@pytest.fixture
def revolution_game(basic_game: Game) -> Game:
    game = basic_game
    game.phase = Game.Phase.REVOLUTION
    game.sub_phase = Game.SubPhase.START
    game.save()
    return game


@pytest.fixture
def declaration_game(revolution_game: Game) -> Game:
    game = revolution_game
    game.sub_phase = Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
    game.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()
    return game


@pytest.fixture
def add_land_victor(
    declaration_game: Game,
) -> Callable[..., Campaign]:
    def add(
        family_name: str,
        legion_numbers: Sequence[int],
        fleet_numbers: Sequence[int] = (),
        master_of_horse_name: Optional[str] = None,
    ) -> Campaign:
        game = declaration_game
        commander = Senator.objects.get(game=game, family_name=family_name)
        commander.location = "Cisalpine Gaul"
        commander.save()

        master_of_horse = None
        if master_of_horse_name:
            master_of_horse = Senator.objects.get(
                game=game, family_name=master_of_horse_name
            )
            master_of_horse.add_title(Senator.Title.MASTER_OF_HORSE)
            master_of_horse.location = "Cisalpine Gaul"
            master_of_horse.save()

        war = War.objects.create(
            game=game,
            name=f"{family_name} War",
            index=0,
            land_strength=10,
            fleet_support=0,
            naval_strength=0,
            spoils=20,
            location="Cisalpine Gaul",
            status=War.Status.DEFEATED,
        )
        campaign = Campaign.objects.create(
            game=game,
            war=war,
            commander=commander,
            master_of_horse=master_of_horse,
        )
        for number in legion_numbers:
            Legion.objects.create(game=game, number=number, campaign=campaign)
        for number in fleet_numbers:
            Fleet.objects.create(game=game, number=number, campaign=campaign)
        return campaign

    return add


@pytest.fixture
def land_victor(add_land_victor: Callable[..., Campaign]) -> Campaign:
    return add_land_victor("Cornelius", [1, 2, 3, 4, 5])


@pytest.fixture
def civil_war_flag(settings) -> None:
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, "civil_war": True}


@pytest.fixture
def revolt_battle(basic_game: Game) -> Callable[..., Campaign]:
    """A Senate army facing the Primary Rebel in the Combat Phase."""

    def build(
        rebel_legions: Sequence[int],
        senate_legions: Sequence[int],
        other_senate_legions: Sequence[int] = (),
    ) -> Campaign:
        game = basic_game
        game.phase = Game.Phase.COMBAT
        game.unrest = 3
        game.save()

        rebel = Senator.objects.get(game=game, family_name="Cornelius")
        rebel.rebel = True
        rebel.location = "Italia"
        rebel.save()
        revolt = War.objects.create(
            game=game,
            name="Revolt",
            index=0,
            land_strength=force_strength(len(rebel_legions), rebel.military),
            fleet_support=0,
            naval_strength=0,
            spoils=0,
            location="Italia",
            status=War.Status.ACTIVE,
            primary_rebel=rebel,
        )
        rebel_army = Campaign.objects.create(game=game, war=revolt, commander=rebel)
        for number in rebel_legions:
            Legion.objects.create(game=game, number=number, campaign=rebel_army)

        armies = []
        for name, legions in [
            ("Manlius", senate_legions),
            ("Fabius", other_senate_legions),
        ]:
            if not legions:
                continue
            commander = Senator.objects.get(game=game, family_name=name)
            commander.location = "Italia"
            commander.add_title(Senator.Title.PROCONSUL)
            commander.save()
            army = Campaign.objects.create(game=game, war=revolt, commander=commander)
            for number in legions:
                Legion.objects.create(game=game, number=number, campaign=army)
            armies.append(army)
        return armies[0]

    return build
