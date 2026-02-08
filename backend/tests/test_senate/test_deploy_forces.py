from typing import List
import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Campaign, Fleet, Game, Legion, Senator, War
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_deploy_field_consul(basic_game: Game):

    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()

    rome_consul = Senator.objects.get(game=game, name="Cornelius")
    rome_consul.add_title(Senator.Title.ROME_CONSUL)
    rome_consul.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    rome_consul.save()

    field_consul = Senator.objects.get(game=game, name="Julius")
    field_consul.add_title(Senator.Title.FIELD_CONSUL)
    field_consul.save()

    legions: List[Legion] = []
    for i in range(1, 11):
        legions.append(Legion.objects.create(game=game, number=i))

    fleets: List[Fleet] = []
    for i in range(1, 11):
        fleets.append(Fleet.objects.create(game=game, number=i))

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

    game.refresh_from_db()
    game.current_proposal = "Deploy Julius with command of 10 legions (I, II, III, IV, V, VI, VII, VIII, IX, X) and 10 fleets (I, II, III, IV, V, VI, VII, VIII, IX, X) to the 1st Punic War"
    game.votes_yea = 15
    game.save()

    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    random_resolver = FakeRandomResolver()
    random_resolver.dice_rolls = [18]
    random_resolver.casualty_order = []
    random_resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, random_resolver)

    # Assert
    game.refresh_from_db()
    assert game.phase == Game.Phase.SENATE
    assert game.current_proposal == None
    field_consul.refresh_from_db()
    assert field_consul.location == war.location

    campaigns = game.campaigns.all()
    assert len(campaigns) == 1
    campaign = campaigns.first()
    assert campaign is not None
    assert campaign.display_name == "Julius' campaign"
    assert campaign.war_id == war.id

    for legion in legions:
        legion.refresh_from_db()
        assert legion.campaign_id == campaign.id

    for fleet in fleets:
        fleet.refresh_from_db()
        assert fleet.campaign_id == campaign.id


@pytest.mark.django_db
def test_deploy_rome_consul(basic_game: Game):

    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()

    rome_consul = Senator.objects.get(game=game, name="Cornelius")
    rome_consul.add_title(Senator.Title.ROME_CONSUL)
    rome_consul.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    rome_consul.save()

    field_consul = Senator.objects.get(game=game, name="Julius")
    field_consul.add_title(Senator.Title.FIELD_CONSUL)
    field_consul.location = "Macedonia"
    field_consul.save()

    legions: List[Legion] = []
    for i in range(1, 11):
        legions.append(Legion.objects.create(game=game, number=i))

    fleets: List[Fleet] = []
    for i in range(1, 11):
        fleets.append(Fleet.objects.create(game=game, number=i))

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

    game.refresh_from_db()
    game.current_proposal = "Deploy Cornelius with command of 10 legions (I, II, III, IV, V, VI, VII, VIII, IX, X) and 10 fleets (I, II, III, IV, V, VI, VII, VIII, IX, X) to the 1st Punic War"
    game.votes_yea = 15
    game.save()

    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    random_resolver = FakeRandomResolver()
    random_resolver.dice_rolls = [18]
    random_resolver.casualty_order = []
    random_resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, random_resolver)

    # Assert
    game.refresh_from_db()
    assert game.phase == Game.Phase.REVOLUTION
    assert game.current_proposal == None
    rome_consul.refresh_from_db()
    assert rome_consul.location == war.location

    campaigns = game.campaigns.all()
    assert len(campaigns) == 1
    campaign = campaigns.first()
    assert campaign is not None
    assert campaign.display_name == "Cornelius' campaign"
    assert campaign.war_id == war.id

    for legion in legions:
        legion.refresh_from_db()
        assert legion.campaign_id == campaign.id

    for fleet in fleets:
        fleet.refresh_from_db()
        assert fleet.campaign_id == campaign.id


@pytest.mark.django_db
def test_deploy_both_consuls(basic_game: Game):

    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()

    rome_consul = Senator.objects.get(game=game, name="Cornelius")
    rome_consul.add_title(Senator.Title.ROME_CONSUL)
    rome_consul.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    rome_consul.save()

    field_consul = Senator.objects.get(game=game, name="Julius")
    field_consul.add_title(Senator.Title.FIELD_CONSUL)
    field_consul.save()

    legions: List[Legion] = []
    for i in range(1, 21):
        legions.append(Legion.objects.create(game=game, number=i))

    fleets: List[Fleet] = []
    for i in range(1, 21):
        fleets.append(Fleet.objects.create(game=game, number=i))

    punic_war = War.objects.create(
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

    macedonian_war = War.objects.create(
        game=game,
        name="1st Macedonian War",
        series_name="Macedonian",
        index=0,
        land_strength=12,
        fleet_support=10,
        naval_strength=0,
        disaster_numbers=[12],
        standoff_numbers=[11, 18],
        spoils=25,
        location="Macedonia",
        status=War.Status.ACTIVE,
    )

    game.refresh_from_db()
    game.current_proposal = "Deploy Julius with command of 10 legions (I, II, III, IV, V, VI, VII, VIII, IX, X) and 10 fleets (I, II, III, IV, V, VI, VII, VIII, IX, X) to the 1st Punic War"
    game.votes_yea = 15
    game.save()

    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    execute_effects_and_manage_actions(game.id)

    game.refresh_from_db()
    game.current_proposal = "Deploy Cornelius with command of 10 legions (XI, XII, XIII, XIV, XV, XVI, XVII, XVIII, XIX, XX) and 10 fleets (XI, XII, XIII, XIV, XV, XVI, XVII, XVIII, XIX, XX) to the 1st Macedonian War"
    game.votes_yea = 15
    game.save()

    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    random_resolver = FakeRandomResolver()
    random_resolver.dice_rolls = [15, 18]
    random_resolver.casualty_order = ["II", "XVIII", "XIX", "XX"]
    random_resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, random_resolver)

    # Assert
    game.refresh_from_db()
    assert game.phase == Game.Phase.REVOLUTION
    assert game.current_proposal == None
    field_consul.refresh_from_db()
    assert field_consul.location == punic_war.location
    rome_consul.refresh_from_db()
    assert rome_consul.location == macedonian_war.location

    campaigns = game.campaigns.all()
    assert len(campaigns) == 2
    punic_campaign: Campaign = campaigns.get(war=punic_war)
    assert punic_campaign.display_name == "Julius' campaign"
    macedonian_campaign: Campaign = campaigns.get(war=macedonian_war)
    assert macedonian_campaign.display_name == "Cornelius' campaign"
