import pytest

from rorapp.actions.fight_land_battle import FightLandBattleAction
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Campaign, Fleet, Game, Legion, Log, Province, Senator, War


def _victory_resolver() -> FakeRandomResolver:
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [18]
    resolver.casualty_order = []
    resolver.mortality_chits = []
    return resolver


def _stalemate_resolver() -> FakeRandomResolver:
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [5]
    resolver.casualty_order = []
    resolver.mortality_chits = []
    return resolver


def _create_second_punic_campaign(game: Game) -> Campaign:
    war = War.objects.create(
        game=game,
        name="2nd Punic War",
        series_name="Punic",
        index=1,
        land_strength=15,
        fleet_support=5,
        naval_strength=0,
        disaster_numbers=[10],
        standoff_numbers=[11, 15],
        spoils=25,
        location="Italia",
        status=War.Status.ACTIVE,
    )
    commander = Senator.objects.get(game=game, family_name="Cornelius")
    commander.add_title(Senator.Title.FIELD_CONSUL)
    commander.location = war.location
    commander.save()
    return Campaign.objects.create(game=game, war=war, commander=commander)


@pytest.mark.django_db
def test_land_victory_awards_province_created_by_war(land_campaign: Campaign):
    # Arrange
    game = land_campaign.game
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)

    # Act
    execute_effects_and_manage_actions(game.id, _victory_resolver())

    # Assert
    assert Province.objects.filter(game=game).count() == 1
    province = Province.objects.get(game=game)
    assert province.name == "Gallia Cisalpina"
    assert province.developed is False
    log_texts = list(Log.objects.filter(game=game).values_list("text", flat=True))
    assert "Gallia Cisalpina was established as a province." in log_texts


@pytest.mark.django_db
def test_second_punic_land_victory_awards_both_hispania_provinces(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.START
    game.save()
    campaign = _create_second_punic_campaign(game)
    for i in range(1, 16):
        Legion.objects.create(game=game, number=i, campaign=campaign)

    # Act
    execute_effects_and_manage_actions(game.id, _victory_resolver())

    # Assert
    assert {p.name for p in Province.objects.filter(game=game)} == {
        "Hispania Citerior",
        "Hispania Ulterior",
    }


@pytest.mark.django_db
def test_naval_victory_alone_does_not_award_provinces(naval_campaign: Campaign):
    # Arrange
    game = naval_campaign.game
    for i in range(1, 11):
        Fleet.objects.create(game=game, number=i, campaign=naval_campaign)

    # Act
    execute_effects_and_manage_actions(game.id, _victory_resolver())

    # Assert
    assert Province.objects.filter(game=game).count() == 0
    assert War.objects.filter(game=game, name="1st Punic War").exists()


@pytest.mark.django_db
def test_full_punic_victory_awards_sicilia_and_sardinia(naval_campaign: Campaign):
    # Arrange
    game = naval_campaign.game
    commander = naval_campaign.commander
    assert commander is not None
    for i in range(1, 11):
        Fleet.objects.create(game=game, number=i, campaign=naval_campaign)
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=naval_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [18, 18]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)
    faction = commander.faction
    assert faction is not None
    FightLandBattleAction().execute(game.id, faction.id, {}, resolver)
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert {p.name for p in Province.objects.filter(game=game)} == {
        "Sicilia",
        "Sardinia et Corsica",
    }
    assert not War.objects.filter(game=game).exists()


@pytest.mark.django_db
def test_stalemate_does_not_award_provinces(land_campaign: Campaign):
    # Arrange
    game = land_campaign.game
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)

    # Act
    execute_effects_and_manage_actions(game.id, _stalemate_resolver())

    # Assert
    assert Province.objects.filter(game=game).count() == 0
    assert War.objects.filter(game=game, name="1st Gallic War").exists()


@pytest.mark.django_db
def test_province_award_skips_provinces_already_in_play(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.START
    game.save()
    Province.objects.create(
        game=game, name="Hispania Citerior", developed=False
    )
    campaign = _create_second_punic_campaign(game)
    for i in range(1, 16):
        Legion.objects.create(game=game, number=i, campaign=campaign)

    # Act
    execute_effects_and_manage_actions(game.id, _victory_resolver())

    # Assert
    assert {p.name for p in Province.objects.filter(game=game)} == {
        "Hispania Citerior",
        "Hispania Ulterior",
    }
    assert Province.objects.filter(game=game).count() == 2
