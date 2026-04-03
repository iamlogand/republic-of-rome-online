import pytest
from rorapp.actions.close_prosecutions import CloseProsecutionsAction
from rorapp.classes.concession import Concession
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.helpers.end_prosecutions import end_prosecutions
from rorapp.models import Faction, Game, Senator


def _setup_all_factions_done(game: Game):
    for f in Faction.objects.filter(game=game):
        f.remove_status_item(FactionStatusItem.CALLED_TO_VOTE)
        f.add_status_item(FactionStatusItem.DONE)
        f.save()


@pytest.mark.django_db
def test_prosecution_advances_to_other_business_after_all_prosecutions_used(
    prosecution_setup, resolver: FakeRandomResolver
):
    # Arrange
    game, julius, cornelius, scipio = prosecution_setup
    senators = list(Senator.objects.filter(game=game, alive=True))

    def run_prosecution(accused, prosecutor, proposal_suffix):
        game_fresh = Game.objects.get(id=game.id)
        game_fresh.current_proposal = (
            f"Prosecute {accused.display_name} for {proposal_suffix}"
        )
        game_fresh.votes_yea = 20
        game_fresh.votes_nay = 0
        game_fresh.save()
        accused_db = Senator.objects.get(id=accused.id)
        accused_db.add_status_item(Senator.StatusItem.ACCUSED)
        accused_db.save()
        prosecutor_db = Senator.objects.get(id=prosecutor.id)
        prosecutor_db.add_status_item(Senator.StatusItem.PROSECUTOR)
        prosecutor_db.save()
        _setup_all_factions_done(game)
        execute_effects_and_manage_actions(game.id, resolver)

    # Act
    run_prosecution(cornelius, scipio, "corruption in office")

    fourth = senators[3] if len(senators) > 3 else senators[2]
    fourth.refresh_from_db()
    fourth.add_status_item(Senator.StatusItem.CORRUPT)
    fourth.save()

    game.refresh_from_db()
    if game.sub_phase == Game.SubPhase.PROSECUTION:
        run_prosecution(fourth, senators[0], "corruption in office")

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS


@pytest.mark.django_db
def test_skip_prosecution_advances_to_other_business(prosecution_setup):
    # Arrange
    game, julius, cornelius, scipio = prosecution_setup
    faction = Faction.objects.get(id=julius.faction.id)

    # Act
    result = CloseProsecutionsAction().execute(
        game.id, faction.id, {}, FakeRandomResolver()
    )

    # Assert
    assert result.success
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS


@pytest.mark.django_db
def test_minor_concession_corruption_cleared_after_prosecutions(prosecution_setup):
    # Arrange
    game, julius, cornelius, scipio = prosecution_setup
    cornelius.add_corrupt_concession(Concession.AEGYPTIAN_GRAIN)
    cornelius.location = "Rome"
    cornelius.save()

    # Act
    end_prosecutions(game.id)

    # Assert
    cornelius.refresh_from_db()
    assert len(cornelius.get_corrupt_concessions()) == 0


@pytest.mark.django_db
def test_corrupt_markers_cleared_after_prosecutions(prosecution_setup):
    # Arrange
    game, julius, cornelius, scipio = prosecution_setup

    cornelius.add_status_item(Senator.StatusItem.MAJOR_CORRUPT)
    cornelius.location = "Rome"
    cornelius.save()

    # Act
    end_prosecutions(game.id)

    # Assert
    cornelius.refresh_from_db()
    assert not cornelius.has_status_item(Senator.StatusItem.CORRUPT)
    assert not cornelius.has_status_item(Senator.StatusItem.MAJOR_CORRUPT)
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS
