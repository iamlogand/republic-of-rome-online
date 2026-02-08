from typing import List
import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Campaign, Faction, Fleet, Game, Legion, Senator, War
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.fixture
def senate_session_with_proconsul_and_replacement(basic_game: Game):
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()

    rome_consul = Senator.objects.get(game=game, name="Cornelius")
    rome_consul.add_title(Senator.Title.ROME_CONSUL)
    rome_consul.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    rome_consul.location = "Rome"
    rome_consul.save()

    proconsul = Senator.objects.get(game=game, name="Julius")
    proconsul.add_title(Senator.Title.PROCONSUL)
    proconsul.location = "Sicilia"
    proconsul.save()

    field_consul = Senator.objects.get(game=game, name="Fabius")
    field_consul.add_title(Senator.Title.FIELD_CONSUL)
    field_consul.location = "Rome"
    field_consul.save()

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

    return {
        "game": game,
        "proconsul": proconsul,
        "field_consul": field_consul,
        "war": war,
    }


@pytest.mark.django_db
def test_replace_proconsul(senate_session_with_proconsul_and_replacement):
    # Arrange
    game = senate_session_with_proconsul_and_replacement["game"]
    proconsul = senate_session_with_proconsul_and_replacement["proconsul"]
    field_consul = senate_session_with_proconsul_and_replacement["field_consul"]
    war = senate_session_with_proconsul_and_replacement["war"]

    campaign = Campaign.objects.create(
        game=game,
        commander=proconsul,
        war=war,
        recently_deployed=False,
        recently_reinforced=False,
    )

    legions: List[Legion] = []
    for i in range(1, 6):
        legion = Legion.objects.create(game=game, number=i)
        legion.campaign = campaign
        legion.save()
        legions.append(legion)

    fleets: List[Fleet] = []
    for i in range(1, 6):
        fleet = Fleet.objects.create(game=game, number=i)
        fleet.campaign = campaign
        fleet.save()
        fleets.append(fleet)

    game.refresh_from_db()
    game.current_proposal = f"Replace {proconsul.display_name} with {field_consul.display_name} in the {war.name}"
    game.votes_yea = 15
    game.save()

    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    # Act
    execute_effects_and_manage_actions(game.id, FakeRandomResolver())

    # Assert
    game.refresh_from_db()
    assert game.current_proposal == None

    campaign.refresh_from_db()
    assert campaign.commander_id == field_consul.id

    proconsul.refresh_from_db()
    assert proconsul.location == "Rome"
    assert not proconsul.has_title(Senator.Title.PROCONSUL)

    field_consul.refresh_from_db()
    assert field_consul.location == war.location

    for legion in legions:
        legion.refresh_from_db()
        assert legion.campaign_id == campaign.id

    for fleet in fleets:
        fleet.refresh_from_db()
        assert fleet.campaign_id == campaign.id


@pytest.mark.django_db
def test_cannot_replace_proconsul_recently_deployed(
    senate_session_with_proconsul_and_replacement,
):
    # Arrange
    game = senate_session_with_proconsul_and_replacement["game"]
    proconsul = senate_session_with_proconsul_and_replacement["proconsul"]
    field_consul = senate_session_with_proconsul_and_replacement["field_consul"]
    war = senate_session_with_proconsul_and_replacement["war"]

    campaign = Campaign.objects.create(
        game=game,
        commander=proconsul,
        war=war,
        recently_deployed=True,
        recently_reinforced=False,
    )

    game.refresh_from_db()
    game.current_proposal = f"Replace {proconsul.display_name} with {field_consul.display_name} in the {war.name}"
    game.votes_yea = 15
    game.save()

    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    # Act
    execute_effects_and_manage_actions(game.id, FakeRandomResolver())

    # Assert
    game.refresh_from_db()
    assert game.current_proposal == None
    assert game.votes_yea == 0
    assert game.votes_nay == 0

    campaign.refresh_from_db()
    assert campaign.commander_id == proconsul.id

    proconsul.refresh_from_db()
    assert proconsul.location == "Sicilia"
    assert proconsul.has_title(Senator.Title.PROCONSUL)


@pytest.mark.django_db
def test_cannot_replace_proconsul_recently_reinforced(
    senate_session_with_proconsul_and_replacement,
):
    # Arrange
    game = senate_session_with_proconsul_and_replacement["game"]
    proconsul = senate_session_with_proconsul_and_replacement["proconsul"]
    field_consul = senate_session_with_proconsul_and_replacement["field_consul"]
    war = senate_session_with_proconsul_and_replacement["war"]

    campaign = Campaign.objects.create(
        game=game,
        commander=proconsul,
        war=war,
        recently_deployed=False,
        recently_reinforced=True,
    )

    game.refresh_from_db()
    game.current_proposal = f"Replace {proconsul.display_name} with {field_consul.display_name} in the {war.name}"
    game.votes_yea = 15
    game.save()

    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    # Act
    execute_effects_and_manage_actions(game.id, FakeRandomResolver())

    # Assert
    game.refresh_from_db()
    assert game.current_proposal == None
    assert game.votes_yea == 0
    assert game.votes_nay == 0

    campaign.refresh_from_db()
    assert campaign.commander_id == proconsul.id

    proconsul.refresh_from_db()
    assert proconsul.location == "Sicilia"
    assert proconsul.has_title(Senator.Title.PROCONSUL)
