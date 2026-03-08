import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Faction, Game, Senator


def _setup_all_factions_done(game: Game):
    for f in Faction.objects.filter(game=game):
        f.remove_status_item(FactionStatusItem.CALLED_TO_VOTE)
        f.add_status_item(FactionStatusItem.DONE)
        f.save()


@pytest.mark.django_db
def test_major_prosecution_guilty_kills_senator(prosecution_setup, resolver: FakeRandomResolver):
    # Arrange
    game, julius, cornelius, scipio = prosecution_setup

    cornelius.add_status_item(Senator.StatusItem.MAJOR_CORRUPT)
    cornelius.save()

    game.current_proposal = f"Prosecute {cornelius.display_name} for major corruption in office"
    game.votes_yea = 20
    game.votes_nay = 5
    game.save()

    cornelius.add_status_item(Senator.StatusItem.ACCUSED)
    cornelius.save()
    scipio.add_status_item(Senator.StatusItem.PROSECUTOR)
    scipio.save()
    _setup_all_factions_done(game)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    cornelius.refresh_from_db()
    is_dead = not cornelius.alive or cornelius.generation > 1
    assert is_dead
