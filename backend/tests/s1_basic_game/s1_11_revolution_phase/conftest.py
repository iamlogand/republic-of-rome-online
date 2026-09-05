from typing import Callable, Optional, Sequence

import pytest
from rorapp.actions.remain_loyal import RemainLoyalAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.helpers.civil_war import undecided_secondary_rebels
from rorapp.models import Campaign, Fleet, Game, Legion, Senator


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
