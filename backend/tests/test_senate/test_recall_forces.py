from typing import Any, Dict, List
import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Campaign, Faction, Fleet, Game, Legion, Senator, War
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


@pytest.mark.django_db
def test_cannot_recall_recently_deployed_campaign(senate_session_with_proconsul: Dict[str, Any]):
    # Arrange
    game = senate_session_with_proconsul["game"]
    proconsul = senate_session_with_proconsul["proconsul"]
    war = senate_session_with_proconsul["war"]

    deployed_legions: List[Legion] = []
    for i in range(1, 6):
        legion = Legion.objects.create(game=game, number=i)
        deployed_legions.append(legion)

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

    game.refresh_from_db()
    game.current_proposal = f"Recall {proconsul.display_name} and 5 legions (I, II, III, IV, V) from {campaign.display_name} in the {war.name}"
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

    for legion in deployed_legions:
        legion.refresh_from_db()
        assert legion.campaign_id == campaign.id


@pytest.mark.django_db
def test_cannot_recall_recently_reinforced_campaign(senate_session_with_proconsul: Dict[str, Any]):
    # Arrange
    game = senate_session_with_proconsul["game"]
    proconsul = senate_session_with_proconsul["proconsul"]
    war = senate_session_with_proconsul["war"]

    deployed_legions: List[Legion] = []
    for i in range(1, 6):
        legion = Legion.objects.create(game=game, number=i)
        deployed_legions.append(legion)

    campaign = Campaign.objects.create(
        game=game,
        commander=proconsul,
        war=war,
        recently_deployed=False,
        recently_reinforced=True,
    )

    for legion in deployed_legions:
        legion.campaign = campaign
        legion.save()

    game.refresh_from_db()
    game.current_proposal = f"Recall {proconsul.display_name} and 5 legions (I, II, III, IV, V) from {campaign.display_name} in the {war.name}"
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

    for legion in deployed_legions:
        legion.refresh_from_db()
        assert legion.campaign_id == campaign.id


@pytest.mark.django_db
def test_recall_land_battle_below_minimum_sets_consent_required(senate_session_with_proconsul):
    """Recalling forces that leave less than minimum strength should set CONSENT_REQUIRED."""
    from rorapp.actions.propose_recalling_forces import ProposeRecallingForcesAction

    game = senate_session_with_proconsul["game"]
    proconsul = senate_session_with_proconsul["proconsul"]
    war = senate_session_with_proconsul["war"]

    # fleet_support=0 so the fleet check doesn't block the recall
    war.fleet_support = 0
    war.save()

    # 5 legions; recalling 2 leaves 3; Julius military=4, effective=3, force=6 < land_strength=10
    legions: List[Legion] = []
    for i in range(1, 6):
        legions.append(Legion.objects.create(game=game, number=i))

    campaign = Campaign.objects.create(
        game=game,
        commander=proconsul,
        war=war,
        recently_deployed=False,
        recently_reinforced=False,
    )
    for legion in legions:
        legion.campaign = campaign
        legion.save()

    faction = proconsul.faction
    assert faction is not None

    action = ProposeRecallingForcesAction()
    result = action.execute(
        game_id=game.id,
        faction_id=faction.id,
        selection={
            "Campaign": str(campaign.id),
            "Legions": [str(l.id) for l in legions[:2]],
            "Recall commander": False,
        },
        random_resolver=FakeRandomResolver(),
    )

    assert result.success == True
    proconsul.refresh_from_db()
    assert proconsul.has_status_item(Senator.StatusItem.CONSENT_REQUIRED)
