import pytest
from rorapp.actions.attempt_assassination import AttemptAssassinationAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Senator


@pytest.mark.django_db
def test_attempt_assassination_not_allowed_outside_senate_phase(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.FORUM
    game.save()
    faction = Faction.objects.filter(game=game).first()
    assert faction is not None
    snapshot = GameStateSnapshot(game.id)

    # Act
    result = AttemptAssassinationAction().is_allowed(snapshot, faction.id)

    # Assert
    assert result is None


@pytest.mark.django_db
def test_attempt_assassination_not_allowed_during_assassination_resolution(
    senate_game: Game,
):
    # Arrange
    game = senate_game
    game.sub_phase = Game.SubPhase.ASSASSINATION_RESOLUTION
    game.save()
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    assert cornelius.faction_id is not None
    snapshot = GameStateSnapshot(game.id)

    # Act
    result = AttemptAssassinationAction().is_allowed(snapshot, cornelius.faction_id)

    # Assert
    assert result is None


@pytest.mark.django_db
def test_attempt_assassination_not_allowed_when_faction_already_attempted(
    senate_game: Game,
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    faction = cornelius.faction
    assert faction is not None
    faction.add_status_item(FactionStatusItem.ATTEMPTED_ASSASSINATION)
    faction.save()
    snapshot = GameStateSnapshot(game.id)

    # Act
    result = AttemptAssassinationAction().is_allowed(snapshot, faction.id)

    # Assert
    assert result is None


@pytest.mark.django_db
def test_attempt_assassination_not_allowed_when_no_senators_in_rome(senate_game: Game):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    faction = cornelius.faction
    assert faction is not None
    for senator in faction.senators.filter(alive=True):
        senator.location = "Africa"
        senator.save()
    snapshot = GameStateSnapshot(game.id)

    # Act
    result = AttemptAssassinationAction().is_allowed(snapshot, faction.id)

    # Assert
    assert result is None


@pytest.mark.django_db
def test_attempt_assassination_transitions_to_assassination_resolution(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    faction_0 = cornelius.faction
    assert faction_0 is not None

    # Act
    AttemptAssassinationAction().execute(
        game.id,
        faction_0.id,
        {"Assassin": cornelius.id, "Target": claudius.id},
        resolver,
    )

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.ASSASSINATION_RESOLUTION
    assert game.interrupted_sub_phase == Game.SubPhase.OTHER_BUSINESS


@pytest.mark.django_db
def test_attempt_assassination_sets_senator_statuses(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    faction_0 = cornelius.faction
    assert faction_0 is not None

    # Act
    AttemptAssassinationAction().execute(
        game.id,
        faction_0.id,
        {"Assassin": cornelius.id, "Target": claudius.id},
        resolver,
    )

    # Assert
    cornelius.refresh_from_db()
    claudius.refresh_from_db()
    assert cornelius.has_status_item(Senator.StatusItem.ASSASSIN)
    assert claudius.has_status_item(Senator.StatusItem.ASSASSINATION_TARGET)


@pytest.mark.django_db
def test_attempt_assassination_sets_faction_statuses(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    faction_0 = cornelius.faction
    faction_1 = claudius.faction
    assert faction_0 is not None
    assert faction_1 is not None

    # Act
    AttemptAssassinationAction().execute(
        game.id,
        faction_0.id,
        {"Assassin": cornelius.id, "Target": claudius.id},
        resolver,
    )

    # Assert
    faction_0.refresh_from_db()
    faction_1.refresh_from_db()
    assert faction_0.has_status_item(FactionStatusItem.ATTEMPTED_ASSASSINATION)
    assert faction_1.has_status_item(FactionStatusItem.ASSASSINATION_TARGETED)


@pytest.mark.django_db
def test_attempt_assassination_removes_played_assassin_cards(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    faction_0 = cornelius.faction
    assert faction_0 is not None
    faction_0.cards = ["assassin", "assassin", "secret bodyguard"]
    faction_0.save()

    # Act
    AttemptAssassinationAction().execute(
        game.id,
        faction_0.id,
        {"Assassin": cornelius.id, "Target": claudius.id, "Assassin cards": "2"},
        resolver,
    )

    # Assert
    faction_0.refresh_from_db()
    assert sum(1 for c in faction_0.cards if c == "assassin") == 0
    assert sum(1 for c in faction_0.cards if c == "secret bodyguard") == 1


@pytest.mark.django_db
def test_attempt_assassination_sets_roll_modifier_from_cards_played(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    faction_0 = cornelius.faction
    assert faction_0 is not None
    faction_0.cards = ["assassin", "assassin"]
    faction_0.save()

    # Act
    AttemptAssassinationAction().execute(
        game.id,
        faction_0.id,
        {"Assassin": cornelius.id, "Target": claudius.id, "Assassin cards": "2"},
        resolver,
    )

    # Assert
    game.refresh_from_db()
    assert game.assassination_roll_modifier == 2


@pytest.mark.django_db
def test_attempt_assassination_blocked_against_already_targeted_faction(
    senate_game: Game,
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    faction_1 = claudius.faction
    assert faction_1 is not None
    faction_1.add_status_item(FactionStatusItem.ASSASSINATION_TARGETED)
    faction_1.save()
    snapshot = GameStateSnapshot(game.id)

    # Act
    assert cornelius.faction_id is not None
    result = AttemptAssassinationAction().get_schema(snapshot, cornelius.faction_id)

    # Assert
    assert result  # action is still available
    target_options = result[0].schema[1]["options"]
    claudius_in_options = any(o["id"] == claudius.id for o in target_options)
    assert not claudius_in_options


@pytest.mark.django_db
def test_land_bill_with_same_faction_sponsors_restricts_targets(senate_game: Game):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    manlius = Senator.objects.get(game=game, family_name="Manlius")
    furius = Senator.objects.get(game=game, family_name="Furius")
    game.current_proposal = (
        "Pass type II land bill sponsored by Claudius and co-sponsored by Manlius"
    )
    game.save()
    claudius.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    claudius.save()
    manlius.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    manlius.save()
    snapshot = GameStateSnapshot(game.id)

    # Act
    assert cornelius.faction_id is not None
    result = AttemptAssassinationAction().get_schema(snapshot, cornelius.faction_id)

    # Assert
    assert result
    target_options = result[0].schema[1]["options"]
    target_ids = {o["id"] for o in target_options}
    assert target_ids == {claudius.id, manlius.id}
    assert furius.id not in target_ids


@pytest.mark.django_db
def test_land_bill_assassination_execute_rejects_non_sponsor_target(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    manlius = Senator.objects.get(game=game, family_name="Manlius")
    furius = Senator.objects.get(game=game, family_name="Furius")
    game.current_proposal = (
        "Pass type II land bill sponsored by Claudius and co-sponsored by Manlius"
    )
    game.save()
    claudius.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    claudius.save()
    manlius.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    manlius.save()

    # Act
    assert cornelius.faction_id is not None
    result = AttemptAssassinationAction().execute(
        game.id,
        cornelius.faction_id,
        {"Assassin": cornelius.id, "Target": furius.id},
        resolver,
    )

    # Assert
    assert not result.success
