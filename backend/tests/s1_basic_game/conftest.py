from typing import Callable, Optional, Sequence

import pytest
from rorapp.models import Campaign, Game, Legion, Senator, War


@pytest.fixture
def rebel_army(basic_game: Game) -> Callable[..., Campaign]:
    """Put a Primary Rebel in the field with an active Civil War."""

    def build(
        legion_numbers: Sequence[int] = (1, 2, 3),
        rebel_name: str = "Cornelius",
        master_of_horse_name: Optional[str] = None,
        other_wars: int = 0,
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
        campaign = Campaign.objects.create(
            game=game, war=None, commander=rebel, recently_deployed=False
        )
        if master_of_horse_name:
            master_of_horse = Senator.objects.get(
                game=game, family_name=master_of_horse_name
            )
            master_of_horse.rebel = True
            master_of_horse.location = "Italia"
            master_of_horse.save()
            campaign.master_of_horse = master_of_horse
            campaign.save()
        for number in legion_numbers:
            Legion.objects.create(game=game, number=number, campaign=campaign)

        War.objects.create(
            game=game,
            name="Civil War",
            index=0,
            land_strength=len(legion_numbers)
            + min(rebel.military, len(legion_numbers)),
            fleet_support=0,
            naval_strength=0,
            spoils=0,
            location="Italia",
            status=War.Status.ACTIVE,
            primary_rebel=rebel,
        )
        ordinals = ["1st", "2nd", "3rd", "4th", "5th"]
        for index in range(other_wars):
            War.objects.create(
                game=game,
                name=f"{ordinals[index]} Gallic War",
                index=index,
                land_strength=10,
                fleet_support=0,
                naval_strength=0,
                disaster_numbers=[13],
                standoff_numbers=[15],
                spoils=20,
                location="Cisalpine Gaul",
                status=War.Status.ACTIVE,
            )
        return campaign

    return build


@pytest.fixture
def civil_war(rebel_army: Callable[..., Campaign]) -> Callable[..., Campaign]:
    """Set up a Combat Phase battle between a Senate army and a Primary Rebel."""

    def build(
        rebel_legions: Sequence[int],
        senate_legions: Sequence[int],
        rebel_name: str = "Cornelius",
        commander_name: str = "Manlius",
        master_of_horse_name: Optional[str] = None,
        rebel_master_of_horse_name: Optional[str] = None,
    ) -> Campaign:
        rebel_campaign = rebel_army(
            legion_numbers=rebel_legions,
            rebel_name=rebel_name,
            master_of_horse_name=rebel_master_of_horse_name,
        )
        game = rebel_campaign.game
        war = War.objects.get(game=game, primary_rebel__isnull=False)

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
