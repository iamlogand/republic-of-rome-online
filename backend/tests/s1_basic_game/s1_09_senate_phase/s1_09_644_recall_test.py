from typing import List
import pytest
from rorapp.actions.propose_recalling_forces import ProposeRecallingForcesAction
from rorapp.actions.propose_replacing_proconsul import ProposeReplacingProconsulAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import AvailableAction, Campaign, Fleet, Game, Legion, Senator, War
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


def _setup_pass_recall_proposal(game: Game, proconsul: Senator, campaign: Campaign, war: War, legions: List[Legion]):
    legion_numerals = ["I", "II", "III", "IV", "V"]
    game.refresh_from_db()
    game.current_proposal = (
        f"Recall {proconsul.display_name} and {len(legions)} legions "
        f"({', '.join(legion_numerals[:len(legions)])}) from {campaign.display_name} in the {war.name}"
    )
    game.votes_yea = 15
    game.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()
    execute_effects_and_manage_actions(game.id, FakeRandomResolver())


def _setup_replace(game: Game):
    proconsul = Senator.objects.get(game=game, family_name="Julius")
    proconsul.add_title(Senator.Title.PROCONSUL)
    proconsul.location = "Sicilia"
    proconsul.save()

    field_consul = Senator.objects.get(game=game, family_name="Fabius")
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
    return proconsul, field_consul, war


def _setup_pass_replace_proposal(game: Game, proconsul: Senator, field_consul: Senator, war: War, recently_deployed: bool = False, recently_reinforced: bool = False) -> Campaign:
    campaign = Campaign.objects.create(
        game=game,
        commander=proconsul,
        war=war,
        recently_deployed=recently_deployed,
        recently_reinforced=recently_reinforced,
    )
    game.refresh_from_db()
    game.current_proposal = f"Replace {proconsul.display_name} with {field_consul.display_name} in the {war.name}"
    game.votes_yea = 15
    game.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()
    resolver = FakeRandomResolver()
    execute_effects_and_manage_actions(game.id, resolver)
    return campaign


@pytest.mark.django_db
def test_fleet_only_proconsul_cannot_be_left_without_fleets(
    proconsul_campaign: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = proconsul_campaign
    campaign = Campaign.objects.get(game=game)
    war = campaign.war
    war.naval_strength = 10
    war.save()
    fleet = Fleet.objects.create(game=game, number=1, campaign=campaign)
    faction = game.factions.get(position=1)

    # Act
    result = ProposeRecallingForcesAction().execute(
        game_id=game.id,
        faction_id=faction.id,
        selection={
            "Campaign": str(campaign.id),
            "Fleets": [str(fleet.id)],
            "Recall commander": False,
        },
        random_resolver=resolver,
    )

    # Assert
    assert not result.success
    assert result.message == (
        "A minimum of 1 fleet must remain for the naval battle. "
        "Leave at least 1 fleet or recall all forces."
    )


@pytest.mark.django_db
def test_recently_deployed_campaign_cannot_be_recalled(proconsul_campaign: Game):
    # Arrange
    game = proconsul_campaign
    proconsul = Senator.objects.get(game=game, family_name="Julius")
    war = War.objects.get(game=game, name="1st Punic War")

    legions = [Legion.objects.create(game=game, number=i) for i in range(1, 6)]
    campaign = Campaign.objects.get(game=game)
    campaign.recently_deployed = True
    campaign.save()
    for legion in legions:
        legion.campaign = campaign
        legion.save()

    # Act
    _setup_pass_recall_proposal(game, proconsul, campaign, war, legions)

    # Assert
    campaign.refresh_from_db()
    assert campaign.commander_id == proconsul.id


@pytest.mark.django_db
def test_recently_reinforced_campaign_cannot_be_recalled(proconsul_campaign: Game):
    # Arrange
    game = proconsul_campaign
    proconsul = Senator.objects.get(game=game, family_name="Julius")
    war = War.objects.get(game=game, name="1st Punic War")

    legions = [Legion.objects.create(game=game, number=i) for i in range(1, 6)]
    campaign = Campaign.objects.get(game=game)
    campaign.recently_reinforced = True
    campaign.save()
    for legion in legions:
        legion.campaign = campaign
        legion.save()

    # Act
    _setup_pass_recall_proposal(game, proconsul, campaign, war, legions)

    # Assert
    campaign.refresh_from_db()
    assert campaign.commander_id == proconsul.id


@pytest.mark.django_db
def test_new_commander_takes_over_campaign(senate_game: Game):
    # Arrange
    game = senate_game
    proconsul, field_consul, war = _setup_replace(game)

    # Act
    campaign = _setup_pass_replace_proposal(game, proconsul, field_consul, war)

    # Assert
    campaign.refresh_from_db()
    assert campaign.commander_id == field_consul.id


@pytest.mark.django_db
def test_senate_ends_when_presiding_magistrate_replaces_proconsul(proconsul_campaign: Game):
    # Arrange
    game = proconsul_campaign
    campaign = Campaign.objects.get(game=game)
    proconsul = Senator.objects.get(game=game, family_name="Julius")
    proconsul.add_title(Senator.Title.PRIOR_CONSUL)
    proconsul.save()
    presiding_magistrate = Senator.objects.get(game=game, family_name="Cornelius")
    game.current_proposal = (
        f"Replace {proconsul.display_name} with {presiding_magistrate.display_name} "
        f"in the {campaign.war.name}"
    )
    game.votes_yea = 15
    game.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    # Act
    execute_effects_and_manage_actions(game.id, FakeRandomResolver())

    # Assert
    game.refresh_from_db()
    presiding_magistrate.refresh_from_db()
    assert game.phase != Game.Phase.SENATE
    assert not presiding_magistrate.has_title(Senator.Title.PRESIDING_MAGISTRATE)


@pytest.mark.django_db
def test_replaced_proconsul_returns_to_rome(senate_game: Game):
    # Arrange
    game = senate_game
    proconsul, field_consul, war = _setup_replace(game)

    # Act
    _setup_pass_replace_proposal(game, proconsul, field_consul, war)

    # Assert
    proconsul.refresh_from_db()
    assert proconsul.location == "Rome"
    assert not proconsul.has_title(Senator.Title.PROCONSUL)


@pytest.mark.django_db
def test_recently_deployed_proconsul_cannot_be_replaced(senate_game: Game):
    # Arrange
    game = senate_game
    proconsul, field_consul, war = _setup_replace(game)

    # Act
    campaign = _setup_pass_replace_proposal(game, proconsul, field_consul, war, recently_deployed=True)

    # Assert
    campaign.refresh_from_db()
    assert campaign.commander_id == proconsul.id


@pytest.mark.django_db
def test_recently_reinforced_proconsul_cannot_be_replaced(senate_game: Game):
    # Arrange
    game = senate_game
    proconsul, field_consul, war = _setup_replace(game)

    # Act
    campaign = _setup_pass_replace_proposal(game, proconsul, field_consul, war, recently_reinforced=True)

    # Assert
    campaign.refresh_from_db()
    assert campaign.commander_id == proconsul.id


@pytest.mark.django_db
def test_replace_proconsul_not_available_when_commander_is_not_proconsul(senate_game: Game):
    # Arrange
    game = senate_game
    field_consul = Senator.objects.get(game=game, family_name="Fabius")
    field_consul.add_title(Senator.Title.FIELD_CONSUL)
    field_consul.location = "Sicilia"
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
    Campaign.objects.create(
        game=game,
        commander=field_consul,
        war=war,
        recently_deployed=False,
        recently_reinforced=False,
    )

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    action_names = [a.base_name for a in AvailableAction.objects.filter(game=game)]
    assert "Propose replacing proconsul" not in action_names


@pytest.mark.django_db
@pytest.mark.parametrize(
    "legion_count,fleet_count,naval_strength,message",
    [
        (0, 5, 0, "A minimum of 1 legion is required for the land battle."),
        (
            1, 4, 0,
            "Insufficient fleet support: at least 5 fleets are required to support the land battle.",
        ),
        (1, 0, 10, "A minimum of 1 fleet is required for the naval battle."),
    ],
)
def test_replacement_rejects_missing_battle_units_or_fleet_support(
    senate_game: Game, resolver: FakeRandomResolver,
    legion_count: int, fleet_count: int, naval_strength: int, message: str,
):
    # Arrange
    game = senate_game
    proconsul, field_consul, war = _setup_replace(game)
    war.naval_strength = naval_strength
    war.save()
    campaign = Campaign.objects.create(
        game=game, war=war, commander=proconsul, recently_deployed=False,
    )
    for i in range(1, legion_count + 1):
        Legion.objects.create(game=game, number=i, campaign=campaign, recently_raised=False)
    for i in range(1, fleet_count + 1):
        Fleet.objects.create(game=game, number=i, campaign=campaign, recently_raised=False)
    faction = field_consul.faction
    assert faction is not None

    # Act
    result = ProposeReplacingProconsulAction().execute(
        game_id=game.id,
        faction_id=faction.id,
        selection={
            "Campaign": str(campaign.id),
            "Replacement commander": str(field_consul.id),
        },
        random_resolver=resolver,
    )

    # Assert
    assert not result.success
    assert result.message == message


@pytest.mark.django_db
@pytest.mark.parametrize(
    "legion_count,veteran,fleet_count,naval_strength,dictator,consent_required",
    [
        (1, False, 5, 0, False, True),
        (4, True, 5, 0, False, False),
        (6, False, 5, 0, False, False),
        (6, False, 5, 10, False, True),
        (1, False, 6, 10, False, False),
        (5, False, 5, 0, True, False),
        (4, False, 5, 0, True, True),
    ],
)
def test_replacement_requests_consent_only_below_minimum_force(
    senate_game: Game, resolver: FakeRandomResolver,
    legion_count: int, veteran: bool, fleet_count: int, naval_strength: int,
    dictator: bool, consent_required: bool,
):
    # Arrange
    game = senate_game
    proconsul, commander, war = _setup_replace(game)
    war.naval_strength = naval_strength
    war.save()
    if dictator:
        presiding_magistrate = Senator.objects.get(game=game, family_name="Cornelius")
        presiding_magistrate.remove_title(Senator.Title.PRESIDING_MAGISTRATE)
        presiding_magistrate.remove_title(Senator.Title.HRAO)
        presiding_magistrate.save()
        commander.remove_title(Senator.Title.FIELD_CONSUL)
        commander.add_title(Senator.Title.DICTATOR)
        commander.add_title(Senator.Title.PRESIDING_MAGISTRATE)
        commander.add_title(Senator.Title.HRAO)
        commander.save()
        master_of_horse = Senator.objects.get(game=game, family_name="Claudius")
        master_of_horse.add_title(Senator.Title.MASTER_OF_HORSE)
        master_of_horse.save()
    campaign = Campaign.objects.create(
        game=game, war=war, commander=proconsul, recently_deployed=False,
    )
    for i in range(1, legion_count + 1):
        Legion.objects.create(
            game=game, number=i, campaign=campaign, veteran=veteran, recently_raised=False,
        )
    for i in range(1, fleet_count + 1):
        Fleet.objects.create(game=game, number=i, campaign=campaign, recently_raised=False)
    faction = commander.faction
    assert faction is not None

    # Act
    result = ProposeReplacingProconsulAction().execute(
        game_id=game.id,
        faction_id=faction.id,
        selection={
            "Campaign": str(campaign.id),
            "Replacement commander": str(commander.id),
        },
        random_resolver=resolver,
    )
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert result.success
    commander.refresh_from_db()
    assert commander.has_status_item(Senator.StatusItem.CONSENT_REQUIRED) == consent_required
    action_names = set(
        AvailableAction.objects.filter(game=game, faction=faction).values_list("base_name", flat=True)
    )
    assert ("Accept risky command" in action_names) == consent_required
    assert ("Refuse risky command" in action_names) == consent_required
    assert game.logs.filter(
        text__endswith=f" {commander.display_name} must consent to the risky command."
    ).exists() == consent_required


@pytest.mark.django_db
def test_defeated_risky_replacement_does_not_require_consent(
    senate_game: Game, resolver: FakeRandomResolver,
):
    # Arrange
    game = senate_game
    proconsul, field_consul, war = _setup_replace(game)
    campaign = Campaign.objects.create(
        game=game, war=war, commander=proconsul, recently_deployed=False,
    )
    Legion.objects.create(game=game, number=1, campaign=campaign, recently_raised=False)
    for i in range(1, 6):
        Fleet.objects.create(game=game, number=i, campaign=campaign, recently_raised=False)
    game.add_defeated_proposal(
        f"Replace {proconsul.display_name} with {field_consul.display_name} in the {war.name}"
    )
    game.save()
    faction = field_consul.faction
    assert faction is not None

    # Act
    result = ProposeReplacingProconsulAction().execute(
        game_id=game.id,
        faction_id=faction.id,
        selection={
            "Campaign": str(campaign.id),
            "Replacement commander": str(field_consul.id),
        },
        random_resolver=resolver,
    )

    # Assert
    assert not result.success
    assert result.message == "This proposal was previously rejected"
    field_consul.refresh_from_db()
    assert not field_consul.has_status_item(Senator.StatusItem.CONSENT_REQUIRED)
