import pytest
from rorapp.actions.elect_dictator import ElectDictatorAction
from rorapp.actions.skip import SkipAction
from rorapp.actions.veto_with_tribune import VetoWithTribuneAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Senator


def _setup_election_game(basic_game: Game) -> tuple:
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.DICTATOR_ELECTION
    game.save()
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    cornelius.add_title(Senator.Title.ROME_CONSUL)
    cornelius.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    cornelius.add_title(Senator.Title.HRAO)
    cornelius.save()
    return game, cornelius, cornelius.faction


@pytest.mark.django_db
def test_presiding_magistrate_can_call_dictator_election(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game, cornelius, pm_faction = _setup_election_game(basic_game)
    snapshot = GameStateSnapshot(game.id)

    # Act
    allowed = ElectDictatorAction().is_allowed(snapshot, pm_faction.id)

    # Assert
    assert allowed is not None


@pytest.mark.django_db
def test_tribune_can_propose_dictator_election(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game, cornelius, pm_faction = _setup_election_game(basic_game)
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    faction_1 = claudius.faction
    assert faction_1 is not None
    faction_1.add_status_item(FactionStatusItem.PLAYED_TRIBUNE)
    faction_1.save()
    snapshot = GameStateSnapshot(game.id)

    # Act
    allowed = ElectDictatorAction().is_allowed(snapshot, faction_1.id)

    # Assert
    assert allowed is not None


@pytest.mark.django_db
def test_dictator_election_passed_appoints_dictator(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game, cornelius, _ = _setup_election_game(basic_game)
    julius = Senator.objects.get(game=game, family_name="Julius")
    game.current_proposal = f"Elect Dictator {julius.display_name}"
    game.votes_yea = 15
    game.votes_nay = 0
    game.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    julius.refresh_from_db()
    assert julius.has_title(Senator.Title.DICTATOR)


@pytest.mark.django_db
def test_dictator_election_failed_adds_to_defeated_proposals(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game, cornelius, _ = _setup_election_game(basic_game)
    julius = Senator.objects.get(game=game, family_name="Julius")
    proposal = f"Elect Dictator {julius.display_name}"
    game.current_proposal = proposal
    game.votes_yea = 0
    game.votes_nay = 15
    game.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert proposal in game.defeated_proposals


@pytest.mark.django_db
def test_pm_can_skip_to_censor_election(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game, cornelius, pm_faction = _setup_election_game(basic_game)

    # Act
    SkipAction().execute(game.id, pm_faction.id, {}, resolver)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.CENSOR_ELECTION


@pytest.mark.django_db
def test_dictator_proposals_cannot_be_vetoed_by_tribune(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.current_proposal = "Some proposal raised by the Dictator"
    game.save()
    julius = Senator.objects.get(game=game, family_name="Julius")
    julius.add_title(Senator.Title.DICTATOR)
    julius.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    julius.add_title(Senator.Title.HRAO)
    julius.save()
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    faction_1 = claudius.faction
    assert faction_1 is not None
    faction_1.cards = ["tribune"]
    faction_1.save()
    snapshot = GameStateSnapshot(game.id)

    # Act
    allowed = VetoWithTribuneAction().is_allowed(snapshot, faction_1.id)

    # Assert
    assert allowed is None


@pytest.mark.django_db
def test_tribune_raised_proposal_can_be_vetoed(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.current_proposal = "Some proposal raised via tribune"
    game.save()
    julius = Senator.objects.get(game=game, family_name="Julius")
    julius.add_title(Senator.Title.DICTATOR)
    julius.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    julius.add_title(Senator.Title.HRAO)
    julius.save()
    furius = Senator.objects.get(game=game, family_name="Furius")
    faction_2 = furius.faction
    assert faction_2 is not None
    faction_2.add_status_item(FactionStatusItem.PROPOSED_VIA_TRIBUNE)
    faction_2.save()
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    faction_1 = claudius.faction
    assert faction_1 is not None
    faction_1.cards = ["tribune"]
    faction_1.save()
    snapshot = GameStateSnapshot(game.id)

    # Act
    allowed = VetoWithTribuneAction().is_allowed(snapshot, faction_1.id)

    # Assert
    assert allowed is not None
