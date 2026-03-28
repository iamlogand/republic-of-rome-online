import pytest
from rorapp.actions.veto_with_tribune import VetoWithTribuneAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Faction, Game, Senator


@pytest.mark.django_db
def test_proposer_faction_can_veto_own_proposal(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.current_proposal = "Elect consuls Julius and Cornelius"
    game.save()
    pm_faction = next(
        f
        for f in Faction.objects.filter(game=game)
        if any(
            s.has_title(Senator.Title.PRESIDING_MAGISTRATE) for s in f.senators.all()
        )
    )
    pm_faction.cards = ["tribune"]
    pm_faction.save()

    from rorapp.game_state.game_state_snapshot import GameStateSnapshot

    snapshot = GameStateSnapshot(game.id)

    # Act
    allowed = VetoWithTribuneAction().is_allowed(snapshot, pm_faction.id)

    # Assert
    assert allowed is not None


@pytest.mark.django_db
def test_pm_faction_can_veto_tribune_proposal(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.current_proposal = "Elect consuls Julius and Cornelius"
    game.save()
    factions = list(Faction.objects.filter(game=game))
    pm_faction = next(
        f
        for f in factions
        if any(
            s.has_title(Senator.Title.PRESIDING_MAGISTRATE) for s in f.senators.all()
        )
    )
    pm_faction.cards = ["tribune"]
    pm_faction.save()

    from rorapp.game_state.game_state_snapshot import GameStateSnapshot

    snapshot = GameStateSnapshot(game.id)

    # Act
    allowed = VetoWithTribuneAction().is_allowed(snapshot, pm_faction.id)

    # Assert
    assert allowed is not None


@pytest.mark.django_db
def test_faction_with_tribune_can_veto_proposal(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.current_proposal = "Elect consuls Julius and Cornelius"
    game.save()
    non_pm_faction = next(
        f
        for f in Faction.objects.filter(game=game)
        if not any(
            s.has_title(Senator.Title.PRESIDING_MAGISTRATE) for s in f.senators.all()
        )
    )
    non_pm_faction.cards = ["tribune"]
    non_pm_faction.save()

    # Act
    result = VetoWithTribuneAction().execute(game.id, non_pm_faction.id, {}, resolver)

    # Assert
    assert result.success
    game.refresh_from_db()
    assert game.current_proposal is None
    assert game.votes_yea == 0
    assert game.votes_nay == 0


@pytest.mark.django_db
def test_faction_without_tribune_cannot_veto(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.current_proposal = "Elect consuls Julius and Cornelius"
    game.save()
    non_pm_faction = next(
        f
        for f in Faction.objects.filter(game=game)
        if not any(
            s.has_title(Senator.Title.PRESIDING_MAGISTRATE) for s in f.senators.all()
        )
    )
    non_pm_faction.cards = []
    non_pm_faction.save()

    from rorapp.game_state.game_state_snapshot import GameStateSnapshot

    snapshot = GameStateSnapshot(game.id)

    # Act
    allowed = VetoWithTribuneAction().is_allowed(snapshot, non_pm_faction.id)

    # Assert
    assert allowed is None


@pytest.mark.django_db
def test_faction_that_is_done_cannot_veto(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.current_proposal = "Elect consuls Julius and Cornelius"
    game.save()
    non_pm_faction = next(
        f
        for f in Faction.objects.filter(game=game)
        if not any(
            s.has_title(Senator.Title.PRESIDING_MAGISTRATE) for s in f.senators.all()
        )
    )
    non_pm_faction.cards = ["tribune"]
    non_pm_faction.add_status_item(FactionStatusItem.DONE)
    non_pm_faction.save()

    from rorapp.game_state.game_state_snapshot import GameStateSnapshot

    snapshot = GameStateSnapshot(game.id)

    # Act
    allowed = VetoWithTribuneAction().is_allowed(snapshot, non_pm_faction.id)

    # Assert
    assert allowed is None


@pytest.mark.django_db
def test_veto_adds_proposal_to_defeated_proposals(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    proposal = "Elect consuls Julius and Cornelius"
    game.current_proposal = proposal
    game.save()
    non_pm_faction = next(
        f
        for f in Faction.objects.filter(game=game)
        if not any(
            s.has_title(Senator.Title.PRESIDING_MAGISTRATE) for s in f.senators.all()
        )
    )
    non_pm_faction.cards = ["tribune"]
    non_pm_faction.save()

    # Act
    result = VetoWithTribuneAction().execute(game.id, non_pm_faction.id, {}, resolver)

    # Assert
    assert result.success
    game.refresh_from_db()
    assert proposal in game.defeated_proposals


@pytest.mark.django_db
def test_veto_removes_tribune_from_hand(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.current_proposal = "Elect consuls Julius and Cornelius"
    game.save()
    non_pm_faction = next(
        f
        for f in Faction.objects.filter(game=game)
        if not any(
            s.has_title(Senator.Title.PRESIDING_MAGISTRATE) for s in f.senators.all()
        )
    )
    non_pm_faction.cards = ["tribune"]
    non_pm_faction.save()

    # Act
    VetoWithTribuneAction().execute(game.id, non_pm_faction.id, {}, resolver)

    # Assert
    non_pm_faction.refresh_from_db()
    assert "tribune" not in non_pm_faction.cards


@pytest.mark.django_db
def test_veto_clears_faction_done_and_called_to_vote_statuses(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.current_proposal = "Elect consuls Julius and Cornelius"
    game.votes_yea = 5
    game.save()
    factions = list(Faction.objects.filter(game=game))
    pm_faction = next(
        f
        for f in factions
        if any(
            s.has_title(Senator.Title.PRESIDING_MAGISTRATE) for s in f.senators.all()
        )
    )
    pm_faction.add_status_item(FactionStatusItem.DONE)
    pm_faction.save()
    non_pm_faction = next(f for f in factions if f.id != pm_faction.id)
    non_pm_faction.cards = ["tribune"]
    non_pm_faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    non_pm_faction.save()

    # Act
    VetoWithTribuneAction().execute(game.id, non_pm_faction.id, {}, resolver)

    # Assert
    pm_faction.refresh_from_db()
    non_pm_faction.refresh_from_db()
    assert not pm_faction.has_status_item(FactionStatusItem.DONE)
    assert not non_pm_faction.has_status_item(FactionStatusItem.CALLED_TO_VOTE)


@pytest.mark.django_db
def test_faction_can_veto_while_called_to_vote(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    game.current_proposal = "Elect consuls Julius and Cornelius"
    game.save()
    non_pm_faction = next(
        f
        for f in Faction.objects.filter(game=game)
        if not any(
            s.has_title(Senator.Title.PRESIDING_MAGISTRATE) for s in f.senators.all()
        )
    )
    non_pm_faction.cards = ["tribune"]
    non_pm_faction.add_status_item(FactionStatusItem.CALLED_TO_VOTE)
    non_pm_faction.save()

    from rorapp.game_state.game_state_snapshot import GameStateSnapshot

    snapshot = GameStateSnapshot(game.id)

    # Act
    allowed = VetoWithTribuneAction().is_allowed(snapshot, non_pm_faction.id)

    # Assert
    assert allowed is not None
