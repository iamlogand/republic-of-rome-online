from typing import List
import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Campaign, Fleet, Game, Legion, Senator, War
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.fixture
def senate_session_with_proconsul(basic_game: Game):
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()

    rome_consul = Senator.objects.get(game=game, name="Cornelius")
    rome_consul.add_title(Senator.Title.ROME_CONSUL)
    rome_consul.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    rome_consul.save()

    proconsul = Senator.objects.get(game=game, name="Julius")
    proconsul.add_title(Senator.Title.PROCONSUL)
    proconsul.location = "Sicilia"
    proconsul.save()

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

    return {"game": game, "proconsul": proconsul, "war": war}


def create_legions(game: Game, start: int, end: int) -> List[Legion]:
    return [Legion.objects.create(game=game, number=i) for i in range(start, end)]


def create_fleets(game: Game, start: int, end: int) -> List[Fleet]:
    return [Fleet.objects.create(game=game, number=i) for i in range(start, end)]


def pass_proposal(game: Game, proposal: str):
    game.refresh_from_db()
    game.current_proposal = proposal
    game.votes_yea = 15
    game.save()

    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()


@pytest.mark.django_db
def test_reinforce_campaign_with_legions_and_fleets(senate_session_with_proconsul):
    # Arrange
    game = senate_session_with_proconsul["game"]
    proconsul = senate_session_with_proconsul["proconsul"]
    war = senate_session_with_proconsul["war"]

    deployed_legions = create_legions(game, 1, 6)
    reserve_legions = create_legions(game, 6, 11)
    deployed_fleets = create_fleets(game, 1, 6)
    reserve_fleets = create_fleets(game, 6, 11)

    campaign = Campaign.objects.create(
        game=game,
        commander=proconsul,
        war=war,
        recently_deployed=False,
        recently_reinforced=False,
    )

    for legion in deployed_legions:
        legion.campaign = campaign
        legion.save()

    for fleet in deployed_fleets:
        fleet.campaign = campaign
        fleet.save()

    pass_proposal(
        game,
        "Reinforce Julius' campaign with 5 legions (VI, VII, VIII, IX, X) and 5 fleets (VI, VII, VIII, IX, X) in the 1st Punic War",
    )

    # Act
    execute_effects_and_manage_actions(game.id, FakeRandomResolver())

    # Assert
    game.refresh_from_db()
    assert game.current_proposal == None
    campaign.refresh_from_db()
    assert campaign.recently_reinforced == True

    for legion in deployed_legions + reserve_legions:
        legion.refresh_from_db()
        assert legion.campaign_id == campaign.id

    for fleet in deployed_fleets + reserve_fleets:
        fleet.refresh_from_db()
        assert fleet.campaign_id == campaign.id


@pytest.mark.django_db
def test_cannot_reinforce_recently_deployed_campaign(senate_session_with_proconsul):
    # Arrange
    game = senate_session_with_proconsul["game"]
    proconsul = senate_session_with_proconsul["proconsul"]
    war = senate_session_with_proconsul["war"]

    deployed_legions = create_legions(game, 1, 6)
    reserve_legions = create_legions(game, 6, 11)

    campaign = Campaign.objects.create(
        game=game,
        commander=proconsul,
        war=war,
        recently_deployed=True,
        recently_reinforced=False,
    )

    for legion in deployed_legions:
        legion.campaign = campaign
        legion.save()

    pass_proposal(
        game, "Reinforce Julius' campaign with 5 legions (VI, VII, VIII, IX, X) in the 1st Punic War"
    )

    # Act
    execute_effects_and_manage_actions(game.id, FakeRandomResolver())

    # Assert
    game.refresh_from_db()
    assert game.current_proposal == None
    assert game.votes_yea == 0
    assert game.votes_nay == 0

    for legion in reserve_legions:
        legion.refresh_from_db()
        assert legion.campaign_id == None


@pytest.mark.django_db
def test_can_reinforce_recently_reinforced_campaign(senate_session_with_proconsul):
    # Arrange
    game = senate_session_with_proconsul["game"]
    proconsul = senate_session_with_proconsul["proconsul"]
    war = senate_session_with_proconsul["war"]

    first_batch_legions = create_legions(game, 1, 6)
    second_batch_legions = create_legions(game, 6, 11)
    third_batch_legions = create_legions(game, 11, 16)

    campaign = Campaign.objects.create(
        game=game,
        commander=proconsul,
        war=war,
        recently_deployed=False,
        recently_reinforced=True,
    )

    for legion in first_batch_legions:
        legion.campaign = campaign
        legion.save()

    pass_proposal(
        game, "Reinforce Julius' campaign with 5 legions (VI, VII, VIII, IX, X) in the 1st Punic War"
    )
    execute_effects_and_manage_actions(game.id)

    pass_proposal(
        game,
        "Reinforce Julius' campaign with 5 legions (XI, XII, XIII, XIV, XV) in the 1st Punic War",
    )

    # Act
    execute_effects_and_manage_actions(game.id, FakeRandomResolver())

    # Assert
    game.refresh_from_db()
    assert game.current_proposal == None
    campaign.refresh_from_db()
    assert campaign.recently_reinforced == True

    for legion in first_batch_legions + second_batch_legions + third_batch_legions:
        legion.refresh_from_db()
        assert legion.campaign_id == campaign.id


@pytest.mark.django_db
def test_cannot_reinforce_uncommanded_campaign(senate_session_with_proconsul):
    # Arrange
    game = senate_session_with_proconsul["game"]
    war = senate_session_with_proconsul["war"]

    deployed_legions = create_legions(game, 1, 6)
    reserve_legions = create_legions(game, 6, 11)

    campaign = Campaign.objects.create(
        game=game,
        commander=None,
        war=war,
        recently_deployed=False,
        recently_reinforced=False,
    )

    for legion in deployed_legions:
        legion.campaign = campaign
        legion.save()

    pass_proposal(
        game,
        "Reinforce uncommanded campaign with 5 legions (VI, VII, VIII, IX, X) in the 1st Punic War",
    )

    # Act
    execute_effects_and_manage_actions(game.id, FakeRandomResolver())

    # Assert
    game.refresh_from_db()
    assert game.current_proposal == None
    assert game.votes_yea == 0
    assert game.votes_nay == 0

    for legion in reserve_legions:
        legion.refresh_from_db()
        assert legion.campaign_id == None
