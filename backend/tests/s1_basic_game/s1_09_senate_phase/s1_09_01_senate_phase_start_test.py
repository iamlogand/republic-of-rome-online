import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.senate_phase_start import SenatePhaseStartEffect
from rorapp.models import Faction, Game, Senator


@pytest.mark.django_db
def test_statesman_with_free_tribune_gets_status_at_senate_start(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.START
    game.save()
    senator = Senator.objects.filter(game=game, alive=True).first()
    assert senator is not None
    senator.code = "22a"
    senator.statesman_name = "M. Porcius Cato the Elder"
    senator.location = "Rome"
    senator.save()

    # Act
    SenatePhaseStartEffect().execute(game.id, resolver)

    # Assert
    senator.refresh_from_db()
    assert senator.has_status_item(Senator.StatusItem.FREE_TRIBUNE)


@pytest.mark.django_db
def test_assassination_tracking_reset_at_senate_start(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.START
    game.save()
    faction_a = Faction.objects.filter(game=game, position=1).first()
    faction_b = Faction.objects.filter(game=game, position=2).first()
    faction_a.add_status_item(FactionStatusItem.ATTEMPTED_ASSASSINATION)
    faction_a.save()
    faction_b.add_status_item(FactionStatusItem.ASSASSINATION_TARGETED)
    faction_b.save()

    # Act
    SenatePhaseStartEffect().execute(game.id, resolver)

    # Assert
    faction_a.refresh_from_db()
    faction_b.refresh_from_db()
    assert not faction_a.has_status_item(FactionStatusItem.ATTEMPTED_ASSASSINATION)
    assert not faction_b.has_status_item(FactionStatusItem.ASSASSINATION_TARGETED)
