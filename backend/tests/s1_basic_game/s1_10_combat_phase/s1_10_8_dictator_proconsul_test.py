import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.helpers.transfer_power_consuls import transfer_power_consuls
from rorapp.models import Campaign, Game, Senator, War


def _setup_dictator_on_campaign(game: Game) -> tuple:
    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.END
    game.save()

    war = War.objects.create(
        game=game,
        name="1st Gallic War",
        series_name="Gallic",
        index=0,
        land_strength=8,
        fleet_support=0,
        naval_strength=0,
        disaster_numbers=[13],
        standoff_numbers=[15],
        spoils=20,
        location="Cisalpine Gaul",
        status=War.Status.ACTIVE,
    )

    dictator = Senator.objects.get(game=game, family_name="Julius")
    dictator.add_title(Senator.Title.DICTATOR)
    dictator.location = war.location
    dictator.save()

    moh = Senator.objects.get(game=game, family_name="Valerius")
    moh.add_title(Senator.Title.MASTER_OF_HORSE)
    moh.location = war.location
    moh.save()

    campaign = Campaign.objects.create(game=game, war=war, commander=dictator, master_of_horse=moh)
    return dictator, moh, campaign


@pytest.mark.django_db
def test_dictator_loses_dictator_title_becomes_proconsul(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    dictator, moh, campaign = _setup_dictator_on_campaign(game)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    dictator.refresh_from_db()
    assert not dictator.has_title(Senator.Title.DICTATOR)
    assert dictator.has_title(Senator.Title.PROCONSUL)
    assert dictator.has_title(Senator.Title.PRIOR_CONSUL)


@pytest.mark.django_db
def test_moh_returns_to_rome_when_dictator_becomes_proconsul(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    dictator, moh, campaign = _setup_dictator_on_campaign(game)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    moh.refresh_from_db()
    assert moh.location == "Rome"


@pytest.mark.django_db
def test_moh_keeps_title_when_dictator_becomes_proconsul(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    dictator, moh, campaign = _setup_dictator_on_campaign(game)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    moh.refresh_from_db()
    assert moh.has_title(Senator.Title.MASTER_OF_HORSE)


@pytest.mark.django_db
def test_campaign_moh_cleared_when_dictator_becomes_proconsul(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    dictator, moh, campaign = _setup_dictator_on_campaign(game)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    campaign.refresh_from_db()
    assert campaign.master_of_horse is None


@pytest.mark.django_db
def test_moh_title_cleared_at_consular_elections_after_proconsul(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    dictator, moh, campaign = _setup_dictator_on_campaign(game)
    execute_effects_and_manage_actions(game.id, resolver)
    moh.refresh_from_db()
    assert moh.has_title(Senator.Title.MASTER_OF_HORSE)  # still has it after combat phase end
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    fabius = Senator.objects.get(game=game, family_name="Fabius")

    # Act
    transfer_power_consuls(game.id, cornelius.id, fabius.id)

    # Assert
    moh.refresh_from_db()
    assert not moh.has_title(Senator.Title.MASTER_OF_HORSE)
