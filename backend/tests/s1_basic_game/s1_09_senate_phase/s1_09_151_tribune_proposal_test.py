import pytest
from rorapp.actions.close_senate import CloseSenateAction
from rorapp.actions.elect_consuls import ElectConsulsAction
from rorapp.actions.play_tribune import PlayTribuneAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Senator


@pytest.mark.django_db
def test_non_pm_faction_with_tribune_can_play_it(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.CONSULAR_ELECTION
    game.save()
    senators = list(Senator.objects.filter(game=game, alive=True))
    senators[0].add_title(Senator.Title.HRAO)
    senators[0].add_title(Senator.Title.ROME_CONSUL)
    senators[0].add_title(Senator.Title.PRESIDING_MAGISTRATE)
    senators[0].save()
    non_pm_faction = senators[0].faction
    assert non_pm_faction is not None
    other_faction = next(
        f for f in Faction.objects.filter(game=game) if f.id != non_pm_faction.id
    )
    other_faction.cards = ["tribune"]
    other_faction.save()

    # Act
    result = PlayTribuneAction().execute(game.id, other_faction.id, {}, resolver)

    # Assert
    assert result.success
    other_faction.refresh_from_db()
    assert other_faction.has_status_item(FactionStatusItem.PLAYED_TRIBUNE)
    assert "tribune" not in other_faction.cards


@pytest.mark.django_db
def test_tribune_active_blocks_pm_proposal_actions(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.CONSULAR_ELECTION
    game.save()
    senators = list(Senator.objects.filter(game=game, alive=True))
    senators[0].add_title(Senator.Title.PRESIDING_MAGISTRATE)
    senators[0].add_title(Senator.Title.HRAO)
    senators[0].add_title(Senator.Title.ROME_CONSUL)
    senators[0].save()
    pm_faction = senators[0].faction
    assert pm_faction is not None
    other_faction = next(
        f for f in Faction.objects.filter(game=game) if f.id != pm_faction.id
    )
    other_faction.add_status_item(FactionStatusItem.PLAYED_TRIBUNE)
    other_faction.save()

    snapshot = GameStateSnapshot(game.id)

    # Act
    allowed = ElectConsulsAction().is_allowed(snapshot, pm_faction.id)

    # Assert
    assert allowed is None


@pytest.mark.django_db
def test_faction_with_tribune_active_can_make_consular_proposal(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.CONSULAR_ELECTION
    game.save()
    senators = list(Senator.objects.filter(game=game, alive=True))
    senators[0].add_title(Senator.Title.PRESIDING_MAGISTRATE)
    senators[0].add_title(Senator.Title.HRAO)
    senators[0].add_title(Senator.Title.ROME_CONSUL)
    senators[0].save()
    pm_faction = senators[0].faction
    assert pm_faction is not None
    other_faction = next(
        f for f in Faction.objects.filter(game=game) if f.id != pm_faction.id
    )
    other_faction.add_status_item(FactionStatusItem.PLAYED_TRIBUNE)
    other_faction.save()

    snapshot = GameStateSnapshot(game.id)

    # Act
    allowed = ElectConsulsAction().is_allowed(snapshot, other_faction.id)

    # Assert
    assert allowed is not None


@pytest.mark.django_db
def test_tribune_active_cleared_after_making_proposal(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.CONSULAR_ELECTION
    game.save()
    senators = list(Senator.objects.filter(game=game, alive=True))
    senators[0].add_title(Senator.Title.PRESIDING_MAGISTRATE)
    senators[0].add_title(Senator.Title.HRAO)
    senators[0].add_title(Senator.Title.ROME_CONSUL)
    senators[0].save()
    pm_faction = senators[0].faction
    assert pm_faction is not None
    other_faction = next(
        f for f in Faction.objects.filter(game=game) if f.id != pm_faction.id
    )
    other_faction.add_status_item(FactionStatusItem.PLAYED_TRIBUNE)
    other_faction.save()
    candidate_senators = [
        s for s in senators if not s.has_title(Senator.Title.ROME_CONSUL)
    ]

    # Act
    result = ElectConsulsAction().execute(
        game.id,
        other_faction.id,
        {"Consul 1": candidate_senators[0].id, "Consul 2": candidate_senators[1].id},
        resolver,
    )

    # Assert
    assert result.success
    other_faction.refresh_from_db()
    assert not other_faction.has_status_item(FactionStatusItem.PLAYED_TRIBUNE)
    game.refresh_from_db()
    assert game.current_proposal is not None


@pytest.mark.django_db
def test_close_senate_blocked_when_tribune_active(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    factions = list(Faction.objects.filter(game=game))
    pm_faction = next(
        f
        for f in factions
        if any(
            s.has_title(Senator.Title.PRESIDING_MAGISTRATE) for s in f.senators.all()
        )
    )
    non_pm_faction = next(f for f in factions if f.id != pm_faction.id)
    non_pm_faction.add_status_item(FactionStatusItem.PLAYED_TRIBUNE)
    non_pm_faction.save()

    snapshot = GameStateSnapshot(game.id)

    # Act
    allowed = CloseSenateAction().is_allowed(snapshot, pm_faction.id)

    # Assert
    assert allowed is None
