from typing import List
import pytest
from rorapp.models import Campaign, Faction, Game, Legion, Senator, War
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_deploy_field_consul(basic_game: Game):

    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.current_proposal = "Deploy Julius with command of 5 legions (I, II, III, IV, V) to the 1st Punic War"
    game.votes_yea = 15
    game.save()

    for faction in game.factions.all():
        faction.add_status_item(Faction.StatusItem.DONE)
        faction.save()

    rome_consul = Senator.objects.get(game=game, name="Cornelius")
    rome_consul.add_title(Senator.Title.ROME_CONSUL)
    rome_consul.save()
    field_consul = Senator.objects.get(game=game, name="Julius")
    field_consul.add_title(Senator.Title.FIELD_CONSUL)
    field_consul.save()

    legions: List[Legion] = []
    for i in range(1, 6):
        legions.append(Legion.objects.create(game=game, number=i))

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
    )

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.phase == Game.Phase.SENATE
    assert game.current_proposal == None
    field_consul.refresh_from_db()
    assert field_consul.location == war.location

    campaigns: List[Campaign] = game.campaigns.all()
    assert len(campaigns) == 1
    campaign: Campaign = campaigns.first()
    assert campaign.display_name == "Julius' campaign"
    assert campaign.war_id == war.id

    for legion in legions:
        legion.refresh_from_db()
        assert legion.campaign_id == campaign.id

@pytest.mark.django_db
def test_deploy_rome_consul(basic_game: Game):

    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.current_proposal = "Deploy Cornelius with command of 5 legions (I, II, III, IV, V) to the 1st Punic War"
    game.votes_yea = 15
    game.save()

    for faction in game.factions.all():
        faction.add_status_item(Faction.StatusItem.DONE)
        faction.save()

    rome_consul = Senator.objects.get(game=game, name="Cornelius")
    rome_consul.add_title(Senator.Title.ROME_CONSUL)
    rome_consul.save()
    field_consul = Senator.objects.get(game=game, name="Julius")
    field_consul.add_title(Senator.Title.FIELD_CONSUL)
    field_consul.location = "Macedonia"
    field_consul.save()

    legions: List[Legion] = []
    for i in range(1, 6):
        legions.append(Legion.objects.create(game=game, number=i))

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
    )

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.phase == Game.Phase.SENATE
    assert game.current_proposal == None
    rome_consul.refresh_from_db()
    assert rome_consul.location == war.location

    campaigns: List[Campaign] = game.campaigns.all()
    assert len(campaigns) == 1
    campaign: Campaign = campaigns.first()
    assert campaign.display_name == "Cornelius' campaign"
    assert campaign.war_id == war.id

    for legion in legions:
        legion.refresh_from_db()
        assert legion.campaign_id == campaign.id