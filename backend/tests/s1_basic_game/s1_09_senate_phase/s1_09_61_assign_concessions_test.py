import pytest
from rorapp.classes.concession import Concession
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Game, Senator


@pytest.mark.django_db
def test_award_concession_vote_passes(senate_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = senate_game
    game.add_concession(Concession.MINING)
    game.save()

    senator = Senator.objects.get(game=game, family_name="Julius")
    game.current_proposal = f"Award the mining concession to {senator.display_name}"
    game.votes_yea = 15
    game.votes_nay = 0
    game.save()

    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    senator.refresh_from_db()
    assert senator.has_concession(Concession.MINING)
    game.refresh_from_db()
    assert Concession.MINING.value not in game.concessions


@pytest.mark.django_db
def test_award_concession_vote_fails(senate_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = senate_game
    game.add_concession(Concession.MINING)
    game.save()

    senator = Senator.objects.get(game=game, family_name="Julius")
    game.current_proposal = f"Award the mining concession to {senator.display_name}"
    game.votes_yea = 0
    game.votes_nay = 15
    game.save()

    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    senator.refresh_from_db()
    assert not senator.has_concession(Concession.MINING)
    game.refresh_from_db()
    assert Concession.MINING.value in game.concessions
