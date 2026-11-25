from typing import List
import pytest
from rorapp.actions.propose_recalling_forces import ProposeRecallingForcesAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import AvailableAction, Campaign, Fleet, Game, Legion, Log, Senator, War
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
@pytest.mark.parametrize(
    "recall_commander,unit_type,success",
    [(True, None, True), (False, None, False), (True, Legion, False), (True, Fleet, False)],
)
def test_empty_recall_selection_only_accepts_commander_without_units(
    proconsul_campaign: Game,
    resolver: FakeRandomResolver,
    recall_commander: bool,
    unit_type: type[Legion] | type[Fleet] | None,
    success: bool,
):
    # Arrange
    game = proconsul_campaign
    campaign = Campaign.objects.get(game=game)
    proconsul = Senator.objects.get(game=game, family_name="Julius")
    faction = game.factions.get(position=1)
    if unit_type:
        unit_type.objects.create(game=game, number=1, campaign=campaign)

    # Act
    result = ProposeRecallingForcesAction().execute(
        game_id=game.id,
        faction_id=faction.id,
        selection={
            "Campaign": str(campaign.id),
            "Recall commander": recall_commander,
        },
        random_resolver=resolver,
    )

    # Assert
    assert result.success == success
    if success:
        game.refresh_from_db()
        assert game.current_proposal == (
            f"Recall {proconsul.display_name} from {campaign.display_name} in the {campaign.war.name}"
        )
    else:
        assert result.message == "No legions or fleets selected."


@pytest.mark.django_db
def test_voted_recall_returns_proconsul_without_units_to_rome(
    proconsul_campaign: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = proconsul_campaign
    campaign = Campaign.objects.get(game=game)
    proconsul = Senator.objects.get(game=game, family_name="Julius")
    game.current_proposal = (
        f"Recall {proconsul.display_name} from {campaign.display_name} in the {campaign.war.name}"
    )
    game.votes_yea = 15
    game.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    proconsul.refresh_from_db()
    assert proconsul.location == "Rome"
    assert not proconsul.has_title(Senator.Title.PROCONSUL)
    assert not Campaign.objects.filter(id=campaign.id).exists()
    assert Log.objects.filter(
        game=game, text=f"{proconsul.display_name} returned to Rome."
    ).exists()


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
