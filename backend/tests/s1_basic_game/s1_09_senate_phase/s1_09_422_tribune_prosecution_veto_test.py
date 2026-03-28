import pytest
from rorapp.actions.veto_with_tribune import VetoWithTribuneAction
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Faction, Game, Senator


@pytest.mark.django_db
def test_faction_with_tribune_can_veto_prosecution(
    senate_prosecution_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_prosecution_game
    accused = next(
        s
        for s in Senator.objects.filter(game=game, alive=True)
        if s.has_status_item(Senator.StatusItem.CORRUPT)
    )
    game.current_proposal = f"Prosecute {accused.display_name} for minor corruption"
    game.prosecutions_remaining = 2
    game.save()
    accused.add_status_item(Senator.StatusItem.ACCUSED)
    accused.save()
    non_censor_faction = next(
        f
        for f in Faction.objects.filter(game=game)
        if not any(s.has_title(Senator.Title.CENSOR) for s in f.senators.all())
    )
    non_censor_faction.cards = ["tribune"]
    non_censor_faction.save()

    # Act
    result = VetoWithTribuneAction().execute(
        game.id, non_censor_faction.id, {}, resolver
    )

    # Assert
    assert result.success
    game.refresh_from_db()
    assert game.current_proposal is None


@pytest.mark.django_db
def test_vetoed_prosecution_added_to_defeated_proposals(
    senate_prosecution_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_prosecution_game
    accused = next(
        s
        for s in Senator.objects.filter(game=game, alive=True)
        if s.has_status_item(Senator.StatusItem.CORRUPT)
    )
    prosecution = f"Prosecute {accused.display_name} for minor corruption"
    game.current_proposal = prosecution
    game.prosecutions_remaining = 2
    game.save()
    accused.add_status_item(Senator.StatusItem.ACCUSED)
    accused.save()
    non_censor_faction = next(
        f
        for f in Faction.objects.filter(game=game)
        if not any(s.has_title(Senator.Title.CENSOR) for s in f.senators.all())
    )
    non_censor_faction.cards = ["tribune"]
    non_censor_faction.save()

    # Act
    VetoWithTribuneAction().execute(game.id, non_censor_faction.id, {}, resolver)

    # Assert
    game.refresh_from_db()
    assert prosecution in game.defeated_proposals


@pytest.mark.django_db
def test_vetoed_minor_prosecution_decrements_prosecutions_remaining(
    senate_prosecution_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_prosecution_game
    accused = next(
        s
        for s in Senator.objects.filter(game=game, alive=True)
        if s.has_status_item(Senator.StatusItem.CORRUPT)
    )
    game.current_proposal = f"Prosecute {accused.display_name} for minor corruption"
    game.prosecutions_remaining = 2
    game.save()
    accused.add_status_item(Senator.StatusItem.ACCUSED)
    accused.save()
    non_censor_faction = next(
        f
        for f in Faction.objects.filter(game=game)
        if not any(s.has_title(Senator.Title.CENSOR) for s in f.senators.all())
    )
    non_censor_faction.cards = ["tribune"]
    non_censor_faction.save()

    # Act
    VetoWithTribuneAction().execute(game.id, non_censor_faction.id, {}, resolver)

    # Assert
    game.refresh_from_db()
    assert game.prosecutions_remaining == 1


@pytest.mark.django_db
def test_vetoed_prosecution_clears_accused_status(
    senate_prosecution_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_prosecution_game
    accused = next(
        s
        for s in Senator.objects.filter(game=game, alive=True)
        if s.has_status_item(Senator.StatusItem.CORRUPT)
    )
    game.current_proposal = f"Prosecute {accused.display_name} for minor corruption"
    game.prosecutions_remaining = 2
    game.save()
    accused.add_status_item(Senator.StatusItem.ACCUSED)
    accused.save()
    non_censor_faction = next(
        f
        for f in Faction.objects.filter(game=game)
        if not any(s.has_title(Senator.Title.CENSOR) for s in f.senators.all())
    )
    non_censor_faction.cards = ["tribune"]
    non_censor_faction.save()

    # Act
    VetoWithTribuneAction().execute(game.id, non_censor_faction.id, {}, resolver)

    # Assert
    accused.refresh_from_db()
    assert not accused.has_status_item(Senator.StatusItem.ACCUSED)


@pytest.mark.django_db
def test_veto_of_last_prosecution_ends_prosecution_phase(
    senate_prosecution_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_prosecution_game
    accused = next(
        s
        for s in Senator.objects.filter(game=game, alive=True)
        if s.has_status_item(Senator.StatusItem.CORRUPT)
    )
    game.current_proposal = f"Prosecute {accused.display_name} for minor corruption"
    game.prosecutions_remaining = 1
    game.save()
    accused.add_status_item(Senator.StatusItem.ACCUSED)
    accused.save()
    non_censor_faction = next(
        f
        for f in Faction.objects.filter(game=game)
        if not any(s.has_title(Senator.Title.CENSOR) for s in f.senators.all())
    )
    non_censor_faction.cards = ["tribune"]
    non_censor_faction.save()

    # Act
    VetoWithTribuneAction().execute(game.id, non_censor_faction.id, {}, resolver)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS
