from typing import List, Tuple
import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Game, Senator


def _setup_three_candidates(game: Game) -> List[Senator]:
    senators = [
        s
        for s in Senator.objects.filter(game=game, alive=True)
        if not s.has_title(Senator.Title.ROME_CONSUL)
    ]
    for senator in senators[3:]:
        senator.faction = None
        senator.save()
    return sorted(senators[:3], key=lambda s: s.family_name)


def _defeat(game: Game, pair: Tuple[Senator, Senator]) -> None:
    game.add_defeated_proposal(
        f"Elect consuls {pair[0].display_name} and {pair[1].display_name}"
    )
    game.save()


@pytest.mark.django_db
def test_consuls_appointed_when_one_pair_remains(
    senate_consular_election_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_consular_election_game
    first, second, third = _setup_three_candidates(game)
    _defeat(game, (first, second))
    _defeat(game, (first, third))

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    second.refresh_from_db()
    third.refresh_from_db()
    assert second.has_status_item(Senator.StatusItem.INCOMING_CONSUL)
    assert third.has_status_item(Senator.StatusItem.INCOMING_CONSUL)
    first.refresh_from_db()
    assert not first.has_status_item(Senator.StatusItem.INCOMING_CONSUL)


@pytest.mark.django_db
def test_consuls_not_appointed_while_two_pairs_remain(
    senate_consular_election_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_consular_election_game
    first, second, third = _setup_three_candidates(game)
    _defeat(game, (first, second))

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    for senator in (first, second, third):
        senator.refresh_from_db()
        assert not senator.has_status_item(Senator.StatusItem.INCOMING_CONSUL)
