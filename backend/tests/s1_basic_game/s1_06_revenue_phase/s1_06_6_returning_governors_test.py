import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Faction, Game, Province, Senator


def _end_redistribution(game: Game) -> None:
    game.phase = Game.Phase.REVENUE
    game.sub_phase = Game.SubPhase.REDISTRIBUTION
    game.save()
    for faction in Faction.objects.filter(game=game):
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()


def _governor_of(game: Game, senator: Senator, term: int) -> Province:
    senator.location = "Sicilia"
    senator.save()
    return Province.objects.create(
        game=game, name="Sicilia", developed=False, governor=senator, term=term
    )


@pytest.mark.parametrize("term", [3, 2])
@pytest.mark.django_db
def test_governor_term_reduced_at_end_of_revenue_phase(basic_game: Game, term: int):
    # Arrange
    game = basic_game
    governor = Senator.objects.filter(game=game, alive=True).first()
    assert governor is not None
    province = _governor_of(game, governor, term)
    _end_redistribution(game)

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    province.refresh_from_db()
    governor.refresh_from_db()
    assert province.term == term - 1
    assert province.governor_id == governor.id
    assert governor.location == "Sicilia"


@pytest.mark.parametrize("unaligned", [False, True], ids=["aligned", "unaligned"])
@pytest.mark.django_db
def test_governor_returns_to_rome_when_term_ends(basic_game: Game, unaligned: bool):
    # Arrange
    game = basic_game
    governor = Senator.objects.filter(game=game, alive=True).first()
    assert governor is not None
    if unaligned:
        governor.faction = None
    province = _governor_of(game, governor, 1)
    _end_redistribution(game)

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    province.refresh_from_db()
    governor.refresh_from_db()
    assert province.governor_id is None
    assert province.term is None
    assert governor.location == "Rome"
    assert governor.has_status_item(Senator.StatusItem.RETURNED_GOVERNOR)
    game.refresh_from_db()
    assert game.phase == Game.Phase.FORUM


@pytest.mark.django_db
def test_returned_governor_status_cleared_a_turn_after_return(basic_game: Game):
    # Arrange
    game = basic_game
    senator = Senator.objects.filter(game=game, alive=True).first()
    assert senator is not None
    senator.add_status_item(Senator.StatusItem.RETURNED_GOVERNOR)
    senator.save()
    _end_redistribution(game)

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    senator.refresh_from_db()
    assert not senator.has_status_item(Senator.StatusItem.RETURNED_GOVERNOR)


@pytest.mark.django_db
def test_returning_governor_becomes_hrao_when_he_outranks_senators_in_rome(
    basic_game: Game,
):
    # Arrange
    game = basic_game
    senators = list(Senator.objects.filter(game=game, alive=True))
    hrao = senators[0]
    hrao.add_title(Senator.Title.HRAO)
    hrao.save()
    governor = senators[1]
    governor.influence = 30
    governor.save()
    _governor_of(game, governor, 1)
    _end_redistribution(game)

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    governor.refresh_from_db()
    assert governor.has_title(Senator.Title.HRAO)
