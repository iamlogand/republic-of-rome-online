from typing import Callable, Optional, Sequence

import pytest
from rorapp.actions.remain_loyal import RemainLoyalAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.helpers.civil_war import undecided_secondary_rebels
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
        location: str = "Cisalpine Gaul",
    ) -> Campaign:
        game = declaration_game
        commander = Senator.objects.get(game=game, family_name=family_name)
        commander.location = location
        commander.save()

        master_of_horse = None
        if master_of_horse_name:
            master_of_horse = Senator.objects.get(
                game=game, family_name=master_of_horse_name
            )
            master_of_horse.add_title(Senator.Title.MASTER_OF_HORSE)
            master_of_horse.location = location
            master_of_horse.save()

        campaign = Campaign.objects.create(
            game=game,
            war=None,
            commander=commander,
            master_of_horse=master_of_horse,
            land_victory=True,
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
def civil_war(basic_game: Game) -> Callable[..., Campaign]:
    """Set up a Combat Phase battle between a Senate army and a Primary Rebel."""

    def build(
        rebel_legions: Sequence[int],
        senate_legions: Sequence[int],
        rebel_name: str = "Cornelius",
        commander_name: str = "Manlius",
        master_of_horse_name: Optional[str] = None,
        rebel_master_of_horse_name: Optional[str] = None,
    ) -> Campaign:
        game = basic_game
        game.phase = Game.Phase.COMBAT
        game.sub_phase = Game.SubPhase.START
        game.unrest = 3
        game.save()

        rebel = Senator.objects.get(game=game, family_name=rebel_name)
        rebel.rebel = True
        rebel.location = "Italia"
        rebel.save()
        rebel_campaign = Campaign.objects.create(
            game=game, war=None, commander=rebel, recently_deployed=False
        )
        if rebel_master_of_horse_name:
            rebel_moh = Senator.objects.get(
                game=game, family_name=rebel_master_of_horse_name
            )
            rebel_moh.rebel = True
            rebel_moh.location = "Italia"
            rebel_moh.save()
            rebel_campaign.master_of_horse = rebel_moh
            rebel_campaign.save()
        for number in rebel_legions:
            Legion.objects.create(game=game, number=number, campaign=rebel_campaign)

        war = War.objects.create(
            game=game,
            name="Civil War",
            index=0,
            land_strength=len(rebel_legions) + min(rebel.military, len(rebel_legions)),
            fleet_support=0,
            naval_strength=0,
            spoils=0,
            location="Italia",
            status=War.Status.ACTIVE,
            primary_rebel=rebel,
        )

        commander = Senator.objects.get(game=game, family_name=commander_name)
        commander.add_title(Senator.Title.FIELD_CONSUL)
        commander.location = "Italia"
        commander.save()
        master_of_horse = None
        if master_of_horse_name:
            master_of_horse = Senator.objects.get(
                game=game, family_name=master_of_horse_name
            )
            master_of_horse.add_title(Senator.Title.MASTER_OF_HORSE)
            master_of_horse.location = "Italia"
            master_of_horse.save()
        senate_campaign = Campaign.objects.create(
            game=game,
            war=war,
            commander=commander,
            master_of_horse=master_of_horse,
            recently_deployed=False,
        )
        for number in senate_legions:
            Legion.objects.create(game=game, number=number, campaign=senate_campaign)
        return senate_campaign

    return build


@pytest.fixture
def settle_secondary_rebels(
    resolver: FakeRandomResolver,
) -> Callable[[Game], None]:
    def settle(game: Game) -> None:
        execute_effects_and_manage_actions(game.id, resolver)
        while True:
            undecided = undecided_secondary_rebels(game.id)
            if not undecided:
                break
            senator = undecided[0]
            assert senator.faction_id is not None
            RemainLoyalAction().execute(game.id, senator.faction_id, {}, resolver)
        execute_effects_and_manage_actions(game.id, resolver)

    return settle
