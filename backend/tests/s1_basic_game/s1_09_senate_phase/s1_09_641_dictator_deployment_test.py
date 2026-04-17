import pytest
from rorapp.actions.propose_deploying_forces import ProposeDeployingForcesAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Campaign, Game, Legion, Senator, War


def _setup_dictator_deploy(game: Game) -> tuple:
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    julius = Senator.objects.get(game=game, family_name="Julius")
    julius.add_title(Senator.Title.DICTATOR)
    julius.save()
    valerius = Senator.objects.get(game=game, family_name="Valerius")
    valerius.add_title(Senator.Title.MASTER_OF_HORSE)
    valerius.save()
    for i in range(1, 5):
        Legion.objects.create(game=game, number=i)
    war = War.objects.create(
        game=game,
        name="1st Gallic War",
        series_name="Gallic",
        index=0,
        land_strength=5,
        fleet_support=0,
        naval_strength=0,
        disaster_numbers=[13],
        standoff_numbers=[15],
        spoils=20,
        location="Cisalpine Gaul",
        status=War.Status.INACTIVE,
    )
    return julius, valerius, war


def _pass_proposal(game: Game, proposal: str, resolver: FakeRandomResolver):
    game.refresh_from_db()
    game.current_proposal = proposal
    game.votes_yea = 15
    game.votes_nay = 0
    game.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()
    execute_effects_and_manage_actions(game.id, resolver)


@pytest.mark.django_db
def test_dictator_can_be_deployed_to_war(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    julius, valerius, war = _setup_dictator_deploy(game)

    # Act
    _pass_proposal(
        game,
        f"Deploy {julius.display_name} and {valerius.display_name} with command of 4 legions (I\u2013IV) to the {war.name}",
        resolver,
    )

    # Assert
    julius.refresh_from_db()
    assert julius.location == war.location


@pytest.mark.django_db
def test_moh_deployed_alongside_dictator(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    julius, valerius, war = _setup_dictator_deploy(game)

    # Act
    _pass_proposal(
        game,
        f"Deploy {julius.display_name} and {valerius.display_name} with command of 4 legions (I\u2013IV) to the {war.name}",
        resolver,
    )

    # Assert
    valerius.refresh_from_db()
    assert valerius.location == war.location


@pytest.mark.django_db
def test_campaign_master_of_horse_set_on_deployment(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    julius, valerius, war = _setup_dictator_deploy(game)

    # Act
    _pass_proposal(
        game,
        f"Deploy {julius.display_name} and {valerius.display_name} with command of 4 legions (I\u2013IV) to the {war.name}",
        resolver,
    )

    # Assert
    campaign = Campaign.objects.get(game=game, commander=julius)
    assert campaign.master_of_horse_id == valerius.id


@pytest.mark.django_db
def test_dictator_cannot_deploy_without_moh(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    julius = Senator.objects.get(game=game, family_name="Julius")
    julius.add_title(Senator.Title.DICTATOR)
    julius.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    julius.add_title(Senator.Title.HRAO)
    julius.save()
    Legion.objects.create(game=game, number=1)
    War.objects.create(
        game=game,
        name="1st Gallic War",
        series_name="Gallic",
        index=0,
        land_strength=5,
        fleet_support=0,
        naval_strength=0,
        disaster_numbers=[13],
        standoff_numbers=[15],
        spoils=20,
        location="Cisalpine Gaul",
        status=War.Status.INACTIVE,
    )
    faction = julius.faction
    assert faction is not None
    snapshot = GameStateSnapshot(game.id)

    # Act
    allowed = ProposeDeployingForcesAction().is_allowed(snapshot, faction.id)

    # Assert
    assert allowed is None
