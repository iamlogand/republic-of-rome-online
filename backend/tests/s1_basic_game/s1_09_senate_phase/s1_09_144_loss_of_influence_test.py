import pytest
from rorapp.actions.nominate_censor import NominateCensorAction
from rorapp.actions.step_down_as_presiding_magistrate import (
    StepDownAsPresidingMagistrateAction,
)
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.helpers.unanimous_defeat import handle_unanimous_defeat
from rorapp.models import Faction, Game, Senator


@pytest.mark.django_db
def test_tribune_proposal_unanimous_defeat_does_not_penalize_pm(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    senators = list(Senator.objects.filter(game=game, alive=True))
    pm_senator = next(
        s for s in senators if s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
    )
    pm_faction = pm_senator.faction
    assert pm_faction is not None
    pm_faction.add_status_item(FactionStatusItem.PROPOSED_VIA_TRIBUNE)
    pm_faction.save()

    other_senators = [s for s in senators if s.faction_id != pm_faction.id]
    for senator in other_senators:
        senator.add_status_item(Senator.StatusItem.VOTED_NAY)
        senator.save()

    # Act
    handle_unanimous_defeat(game.id)

    # Assert
    pm_senator.refresh_from_db()
    assert not pm_senator.has_status_item(Senator.StatusItem.UNANIMOUSLY_DEFEATED)


@pytest.mark.django_db
def test_pm_with_zero_influence_auto_steps_down_on_unanimous_defeat(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    senators = list(Senator.objects.filter(game=game, alive=True))
    pm_senator = next(
        s for s in senators if s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
    )
    pm_senator.influence = 0
    pm_senator.save()
    pm_faction = pm_senator.faction
    assert pm_faction is not None
    pm_faction.save()

    other_senators = [s for s in senators if s.faction_id != pm_faction.id]
    for senator in other_senators:
        senator.add_status_item(Senator.StatusItem.VOTED_NAY)
        senator.save()

    # Act
    handle_unanimous_defeat(game.id)

    # Assert
    pm_senator.refresh_from_db()
    assert not pm_senator.has_title(Senator.Title.PRESIDING_MAGISTRATE)
    assert pm_senator.has_status_item(Senator.StatusItem.STEPPED_DOWN)
    new_pm = next(
        (
            s
            for s in Senator.objects.filter(game=game)
            if s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
        ),
        None,
    )
    assert new_pm is not None
    assert new_pm.id != pm_senator.id


@pytest.mark.django_db
def test_late_step_down_keeps_censor_as_only_presiding_magistrate(
    senate_censor_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_censor_game
    senators = list(Senator.objects.filter(game=game, alive=True))
    former_pm = senators[0]
    nominee = senators[1]
    censor = senators[2]
    field_consul = senators[4]
    nominee.add_title(Senator.Title.PRIOR_CONSUL)
    nominee.add_status_item(Senator.StatusItem.MAJOR_CORRUPT)
    censor.add_title(Senator.Title.PRIOR_CONSUL)
    field_consul.add_title(Senator.Title.FIELD_CONSUL)
    for senator in senators:
        senator.add_status_item(Senator.StatusItem.VOTED_NAY)
        senator.save()

    assert former_pm.faction_id is not None
    NominateCensorAction().execute(
        game.id, former_pm.faction_id, {"Censor": nominee.id}, resolver
    )
    game.refresh_from_db()
    game.votes_yea = 0
    game.votes_nay = sum(s.votes for s in senators)
    game.save()
    for faction in Faction.objects.filter(game=game):
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()
    execute_effects_and_manage_actions(game.id, resolver)

    # Act
    StepDownAsPresidingMagistrateAction().execute(
        game.id, former_pm.faction_id, {}, resolver
    )
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    presiding_magistrates = [
        s.id
        for s in Senator.objects.filter(game=game, alive=True)
        if s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
    ]
    assert presiding_magistrates == [censor.id]
    former_pm.refresh_from_db()
    assert not former_pm.has_status_item(Senator.StatusItem.UNANIMOUSLY_DEFEATED)
    assert former_pm.has_status_item(Senator.StatusItem.STEPPED_DOWN)
