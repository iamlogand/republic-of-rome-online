import pytest
from rorapp.actions.elect_censor import ElectCensorAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.helpers.censor_candidates import get_eligible_censor_candidates
from rorapp.models import Faction, Game, Senator


def _setup_all_factions_done(game: Game):
    for f in Faction.objects.filter(game=game):
        f.add_status_item(FactionStatusItem.DONE)
        f.save()


@pytest.mark.django_db
def test_censor_elected(senate_censor_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = senate_censor_game
    senators = list(Senator.objects.filter(game=game, alive=True))
    julius = senators[0]
    cornelius = senators[1]
    cornelius.add_title(Senator.Title.PRIOR_CONSUL)
    cornelius.save()
    senators[2].add_status_item(Senator.StatusItem.MAJOR_CORRUPT)
    senators[2].save()

    faction = Faction.objects.get(id=julius.faction.id)
    ElectCensorAction().execute(game.id, faction.id, {"Censor": cornelius.id}, FakeRandomResolver())

    game.refresh_from_db()
    game.votes_yea = 15
    game.votes_nay = 0
    game.save()
    _setup_all_factions_done(game)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    cornelius.refresh_from_db()
    assert cornelius.has_title(Senator.Title.CENSOR)
    assert cornelius.has_title(Senator.Title.PRESIDING_MAGISTRATE)
    julius.refresh_from_db()
    assert not julius.has_title(Senator.Title.PRESIDING_MAGISTRATE)
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.PROSECUTION


@pytest.mark.django_db
def test_censor_election_defeated(senate_censor_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = senate_censor_game
    senators = list(Senator.objects.filter(game=game, alive=True))
    julius = senators[0]
    cornelius = senators[1]
    cornelius.add_title(Senator.Title.PRIOR_CONSUL)
    cornelius.save()
    senators[2].add_title(Senator.Title.PRIOR_CONSUL)
    senators[2].save()

    faction = Faction.objects.get(id=julius.faction.id)
    ElectCensorAction().execute(game.id, faction.id, {"Censor": cornelius.id}, FakeRandomResolver())

    game.refresh_from_db()
    game.votes_yea = 0
    game.votes_nay = 15
    game.save()
    _setup_all_factions_done(game)

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    cornelius.refresh_from_db()
    assert not cornelius.has_title(Senator.Title.CENSOR)
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.CENSOR_ELECTION
    assert any("Elect Censor" in p for p in game.defeated_proposals)


@pytest.mark.django_db
def test_censor_appointed_when_one_prior_consul_eligible(senate_censor_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = senate_censor_game
    senators = list(Senator.objects.filter(game=game, alive=True))
    cornelius = senators[1]
    cornelius.add_title(Senator.Title.PRIOR_CONSUL)
    cornelius.save()
    senators[2].add_status_item(Senator.StatusItem.MAJOR_CORRUPT)
    senators[2].save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    cornelius.refresh_from_db()
    assert cornelius.has_title(Senator.Title.CENSOR)
    assert cornelius.has_title(Senator.Title.PRESIDING_MAGISTRATE)
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.PROSECUTION


@pytest.mark.django_db
def test_no_prior_consuls_falls_back_to_all_senators(senate_censor_game: Game):
    # Arrange
    game = senate_censor_game
    all_senators = list(Senator.objects.filter(game=game, alive=True))

    # Act
    candidates, is_fallback = get_eligible_censor_candidates(all_senators)

    # Assert
    assert is_fallback
    assert len(candidates) > 1


@pytest.mark.django_db
def test_prior_consul_excluded_if_holding_major_office(senate_censor_game: Game):
    # Arrange
    game = senate_censor_game
    rome_consul = Senator.objects.get(game=game, titles__contains=Senator.Title.ROME_CONSUL.value)
    rome_consul.add_title(Senator.Title.PRIOR_CONSUL)
    rome_consul.save()

    all_senators = list(Senator.objects.filter(game=game, alive=True))

    # Act
    candidates, is_fallback = get_eligible_censor_candidates(all_senators)

    # Assert
    assert is_fallback
    assert rome_consul in candidates


