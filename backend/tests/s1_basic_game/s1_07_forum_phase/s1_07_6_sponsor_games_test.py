import pytest
from rorapp.actions.sponsor_games import SponsorGamesAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Game, Senator, War


def _setup_captive_with_seven_talents(game: Game) -> Senator:
    war = War.objects.create(
        game=game,
        name="1st Punic War",
        series_name="Punic",
        index=0,
        land_strength=10,
        fleet_support=5,
        naval_strength=10,
        spoils=35,
        location="Sicilia",
        status=War.Status.ACTIVE,
    )
    captive = Senator.objects.get(game=game, family_name="Fabius")
    captive.captor = war
    captive.location = war.location
    captive.talents = 7
    captive.save()
    return captive


@pytest.mark.django_db
def test_captive_cannot_spend_frozen_talents_on_games(
    forum_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = forum_game
    game.sub_phase = Game.SubPhase.SPONSOR_GAMES
    game.save()
    faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()
    captive = _setup_captive_with_seven_talents(game)

    # Act
    result = SponsorGamesAction().execute(
        game.id,
        faction.id,
        {"Sponsor": captive.id, "Type": "Slice and dice"},
        resolver,
    )

    # Assert
    assert not result.success
    captive.refresh_from_db()
    assert captive.talents == 7


@pytest.mark.django_db
def test_games_step_is_skipped_when_only_captive_has_seven_talents(
    forum_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = forum_game
    game.sub_phase = Game.SubPhase.SPONSOR_GAMES
    game.save()
    faction = game.factions.get(position=1)
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()
    _setup_captive_with_seven_talents(game)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.FACTION_LEADER
