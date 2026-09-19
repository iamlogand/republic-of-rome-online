import pytest
from rorapp.actions.propose_deploying_forces import ProposeDeployingForcesAction
from rorapp.actions.propose_recalling_forces import ProposeRecallingForcesAction
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Campaign, EnemyLeader, Fleet, Game, Legion, Senator, War


@pytest.mark.django_db
def test_individual_war_leader_strength_counts_toward_minimum_force(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    field_consul = Senator.objects.get(game=game, family_name="Julius")
    field_consul.add_title(Senator.Title.FIELD_CONSUL)
    field_consul.save()

    legions = [Legion.objects.create(game=game, number=i) for i in range(1, 4)]
    fleets = [Fleet.objects.create(game=game, number=i) for i in range(1, 3)]
    war = War.objects.create(
        game=game,
        name="Syrian War",
        index=0,
        land_strength=6,
        fleet_support=2,
        naval_strength=0,
        spoils=45,
        location="Asia Minor",
        status=War.Status.ACTIVE,
    )
    EnemyLeader.objects.create(
        game=game,
        name="Antiochus III",
        war_name="Syrian War",
        strength=5,
        disaster_number=14,
        standoff_number=17,
        active=True,
    )

    faction = field_consul.faction
    assert faction is not None

    # Act
    result = ProposeDeployingForcesAction().execute(
        game_id=game.id,
        faction_id=faction.id,
        selection={
            "Commander": str(field_consul.id),
            "Target war": str(war.id),
            "Legions": [str(l.id) for l in legions],
            "Fleets": [str(f.id) for f in fleets],
        },
        random_resolver=resolver,
    )

    # Assert
    assert result.success
    field_consul.refresh_from_db()
    assert field_consul.has_status_item(Senator.StatusItem.CONSENT_REQUIRED)


@pytest.mark.django_db
def test_recall_below_minimum_sets_consent_required(proconsul_campaign: Game, resolver: FakeRandomResolver):
    # Arrange
    game = proconsul_campaign
    proconsul = Senator.objects.get(game=game, family_name="Julius")
    war = War.objects.get(game=game, name="1st Punic War")
    war.fleet_support = 0
    war.save()

    legions = [Legion.objects.create(game=game, number=i) for i in range(1, 6)]
    campaign = Campaign.objects.get(game=game)
    for legion in legions:
        legion.campaign = campaign
        legion.save()

    faction = proconsul.faction
    assert faction is not None

    # Act
    result = ProposeRecallingForcesAction().execute(
        game_id=game.id,
        faction_id=faction.id,
        selection={
            "Campaign": str(campaign.id),
            "Legions": [str(l.id) for l in legions[:2]],
            "Recall commander": False,
        },
        random_resolver=resolver,
    )

    # Assert
    assert result.success
    proconsul.refresh_from_db()
    assert proconsul.has_status_item(Senator.StatusItem.CONSENT_REQUIRED)
