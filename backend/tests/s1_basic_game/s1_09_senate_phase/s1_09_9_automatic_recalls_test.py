import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Campaign, Game, Legion, War
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_commanderless_campaign_recalled_at_senate_close(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.END
    game.save()

    war = War.objects.create(
        game=game,
        name="1st Punic War",
        series_name="Punic",
        index=0,
        land_strength=10,
        fleet_support=0,
        naval_strength=0,
        disaster_numbers=[],
        standoff_numbers=[],
        spoils=35,
        location="Sicilia",
        status=War.Status.ACTIVE,
    )
    campaign = Campaign.objects.create(game=game, war=war, commander=None)
    for i in range(1, 5):
        Legion.objects.create(game=game, number=i, campaign=campaign)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Campaign.objects.filter(game=game).count() == 0
    assert Legion.objects.filter(game=game, campaign__isnull=False).count() == 0
