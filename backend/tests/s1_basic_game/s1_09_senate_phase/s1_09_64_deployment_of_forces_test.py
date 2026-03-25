from typing import List
import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Campaign, Fleet, Game, Legion, Senator, War
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


def _setup_deploy(game: Game):
    rome_consul = Senator.objects.get(game=game, family_name="Cornelius")
    rome_consul.add_title(Senator.Title.ROME_CONSUL)
    rome_consul.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    rome_consul.save()

    field_consul = Senator.objects.get(game=game, family_name="Julius")
    field_consul.add_title(Senator.Title.FIELD_CONSUL)
    field_consul.save()

    legions = [Legion.objects.create(game=game, number=i) for i in range(1, 11)]
    fleets = [Fleet.objects.create(game=game, number=i) for i in range(1, 11)]

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
        status=War.Status.INACTIVE,
    )
    return rome_consul, field_consul, legions, fleets, war


def _setup_pass_proposal(game: Game, proposal: str, dice_rolls: List[int]):
    game.refresh_from_db()
    game.current_proposal = proposal
    game.votes_yea = 15
    game.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()
    resolver = FakeRandomResolver()
    resolver.dice_rolls = dice_rolls
    resolver.casualty_order = []
    resolver.mortality_chits = []
    execute_effects_and_manage_actions(game.id, resolver)


@pytest.mark.django_db
def test_field_consul_deployed_to_war_location(senate_game: Game):
    # Arrange
    game = senate_game
    _, field_consul, legions, fleets, war = _setup_deploy(game)
    legion_ids = ", ".join(["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"])
    fleet_ids = ", ".join(["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"])

    # Act
    _setup_pass_proposal(
        game,
        f"Deploy Julius with command of 10 legions ({legion_ids}) and 10 fleets ({fleet_ids}) to the 1st Punic War",
        [18],
    )

    # Assert
    field_consul.refresh_from_db()
    assert field_consul.location == war.location


@pytest.mark.django_db
def test_campaign_created_on_deployment(senate_game: Game):
    # Arrange
    game = senate_game
    _, field_consul, legions, fleets, war = _setup_deploy(game)
    legion_ids = ", ".join(["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"])
    fleet_ids = ", ".join(["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"])

    # Act
    _setup_pass_proposal(
        game,
        f"Deploy Julius with command of 10 legions ({legion_ids}) and 10 fleets ({fleet_ids}) to the 1st Punic War",
        [18],
    )

    # Assert
    campaigns = Campaign.objects.filter(game=game)
    assert campaigns.count() == 1
    campaign = campaigns.first()
    assert campaign is not None
    assert campaign.war_id == war.id


@pytest.mark.django_db
def test_forces_assigned_to_campaign_on_deployment(senate_game: Game):
    # Arrange
    game = senate_game
    _, field_consul, legions, fleets, war = _setup_deploy(game)
    legion_ids = ", ".join(["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"])
    fleet_ids = ", ".join(["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"])

    # Act
    _setup_pass_proposal(
        game,
        f"Deploy Julius with command of 10 legions ({legion_ids}) and 10 fleets ({fleet_ids}) to the 1st Punic War",
        [18],
    )

    # Assert
    campaign = Campaign.objects.get(game=game)
    for legion in legions:
        legion.refresh_from_db()
        assert legion.campaign_id == campaign.id
    for fleet in fleets:
        fleet.refresh_from_db()
        assert fleet.campaign_id == campaign.id


@pytest.mark.django_db
def test_rome_consul_becomes_proconsul_on_deployment(senate_game: Game):
    # Arrange
    game = senate_game
    rome_consul = Senator.objects.get(game=game, family_name="Cornelius")
    rome_consul.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    rome_consul.save()

    field_consul = Senator.objects.get(game=game, family_name="Julius")
    field_consul.add_title(Senator.Title.FIELD_CONSUL)
    field_consul.location = "Macedonia"
    field_consul.save()

    legions = [Legion.objects.create(game=game, number=i) for i in range(1, 11)]
    fleets = [Fleet.objects.create(game=game, number=i) for i in range(1, 11)]

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
        status=War.Status.INACTIVE,
    )

    legion_ids = ", ".join(["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"])
    fleet_ids = ", ".join(["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"])

    # Act
    _setup_pass_proposal(
        game,
        f"Deploy Cornelius with command of 10 legions ({legion_ids}) and 10 fleets ({fleet_ids}) to the 1st Punic War",
        [18],
    )

    # Assert
    rome_consul.refresh_from_db()
    assert rome_consul.has_title(Senator.Title.PROCONSUL)
