import pytest
from rorapp.actions.attempt_assassination import AttemptAssassinationAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Game, Senator


def _setup_land_bill_assassination(
    game: Game,
    assassin: Senator,
    target: Senator,
    roll_result: int,
    caught: bool = False,
):
    sponsor = target
    cosponsor = Senator.objects.get(game=game, family_name="Manlius")
    proposal = (
        f"Pass type II land bill"
        f" sponsored by {sponsor.display_name}"
        f" and co-sponsored by {cosponsor.display_name}"
    )
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.ASSASSINATION_RESOLUTION
    game.assassination_roll_result = roll_result
    game.assassination_roll_modifier = 0
    game.bodyguard_rerolls_remaining = 0
    game.interrupted_sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.current_proposal = proposal
    game.save()
    assassin.add_status_item(Senator.StatusItem.ASSASSIN)
    if caught:
        assassin.add_status_item(Senator.StatusItem.CAUGHT)
    assassin.save()
    target.add_status_item(Senator.StatusItem.ASSASSINATION_TARGET)
    target.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    target.save()
    cosponsor.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    cosponsor.save()


def _propose_land_bill(game: Game, sponsor: Senator, cosponsor: Senator) -> None:
    game.current_proposal = (
        f"Pass type II land bill"
        f" sponsored by {sponsor.display_name}"
        f" and co-sponsored by {cosponsor.display_name}"
    )
    game.save()
    for senator in (sponsor, cosponsor):
        senator.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
        senator.save()


def _target_names(game: Game, faction_id: int) -> set[str]:
    schema = AttemptAssassinationAction().get_schema(
        GameStateSnapshot(game.id), faction_id
    )
    return {
        Senator.objects.get(id=option["id"]).family_name
        for action in schema
        for field in action.field_descriptors
        if field["name"] == "Target"
        for option in field["options"]
    }


@pytest.mark.django_db
def test_caught_during_land_bill_only_kills_assassin(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    _setup_land_bill_assassination(
        game, cornelius, claudius, roll_result=1, caught=True
    )

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    cornelius.refresh_from_db()
    claudius.refresh_from_db()
    assert not cornelius.alive
    assert claudius.alive


@pytest.mark.django_db
def test_land_bill_vote_continues_when_sponsor_killed(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    original_proposal = (
        f"Pass type II land bill"
        f" sponsored by {claudius.display_name}"
        f" and co-sponsored by Manlius"
    )
    _setup_land_bill_assassination(game, cornelius, claudius, roll_result=5)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.current_proposal == original_proposal


@pytest.mark.django_db
def test_land_bill_vote_continues_after_no_effect_roll(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    _setup_land_bill_assassination(game, cornelius, claudius, roll_result=4)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS
    assert game.current_proposal is not None
    assert "land bill" in game.current_proposal.lower()


@pytest.mark.django_db
def test_senators_outside_the_sponsor_faction_remain_targetable(senate_game: Game):
    # Arrange
    game = senate_game
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    manlius = Senator.objects.get(game=game, family_name="Manlius")
    furius = Senator.objects.get(game=game, family_name="Furius")
    _propose_land_bill(game, claudius, manlius)
    assert furius.faction_id is not None

    # Act
    target_names = _target_names(game, furius.faction_id)

    # Assert
    assert {"Cornelius", "Fabius", "Valerius", "Julius"} <= target_names
    assert {"Claudius", "Manlius"} <= target_names


@pytest.mark.django_db
def test_sponsor_faction_may_assassinate_outside_the_land_bill(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    manlius = Senator.objects.get(game=game, family_name="Manlius")
    fulvius = Senator.objects.get(game=game, family_name="Fulvius")
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    _propose_land_bill(game, claudius, manlius)
    assert fulvius.faction_id is not None

    # Act
    result = AttemptAssassinationAction().execute(
        game.id,
        fulvius.faction_id,
        {"Assassin": fulvius.id, "Target": cornelius.id},
        resolver,
    )

    # Assert
    assert result.success
    cornelius.refresh_from_db()
    assert cornelius.has_status_item(Senator.StatusItem.ASSASSINATION_TARGET)


@pytest.mark.django_db
def test_assassination_still_offered_when_sponsor_faction_already_targeted(
    senate_game: Game,
):
    # Arrange
    game = senate_game
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    manlius = Senator.objects.get(game=game, family_name="Manlius")
    furius = Senator.objects.get(game=game, family_name="Furius")
    _propose_land_bill(game, claudius, manlius)
    sponsor_faction = claudius.faction
    assert sponsor_faction is not None
    sponsor_faction.add_status_item(FactionStatusItem.ASSASSINATION_TARGETED)
    sponsor_faction.save()
    assert furius.faction_id is not None

    # Act
    target_names = _target_names(game, furius.faction_id)

    # Assert
    assert {"Cornelius", "Fabius", "Valerius", "Julius"} <= target_names
    assert not {"Claudius", "Manlius"} & target_names


@pytest.mark.django_db
def test_third_party_faction_may_assassinate_a_non_sponsor(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    manlius = Senator.objects.get(game=game, family_name="Manlius")
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    furius = Senator.objects.get(game=game, family_name="Furius")
    _propose_land_bill(game, claudius, manlius)
    assert cornelius.faction_id is not None

    # Act
    result = AttemptAssassinationAction().execute(
        game.id,
        cornelius.faction_id,
        {"Assassin": cornelius.id, "Target": furius.id},
        resolver,
    )

    # Assert
    assert result.success
    furius.refresh_from_db()
    assert furius.has_status_item(Senator.StatusItem.ASSASSINATION_TARGET)


@pytest.mark.django_db
def test_caught_during_land_bill_spares_the_faction_of_the_assassin(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    valerius = Senator.objects.get(game=game, family_name="Valerius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    valerius.add_title(Senator.Title.FACTION_LEADER)
    valerius.save()
    _setup_land_bill_assassination(
        game, cornelius, claudius, roll_result=1, caught=True
    )
    influence_before = valerius.influence

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    valerius.refresh_from_db()
    assert valerius.influence == influence_before
    assert not valerius.has_status_item(Senator.StatusItem.ACCUSED)
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS
