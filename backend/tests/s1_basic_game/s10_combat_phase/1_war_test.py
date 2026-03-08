import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Campaign, Game, Legion, Senator
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_agreed_attacker_fights_first(two_campaigns):
    # Arrange
    campaign1, campaign2 = two_campaigns
    game = campaign1.game
    commander1 = campaign1.commander
    commander2 = campaign2.commander

    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=campaign1)
    for i in range(11, 21):
        Legion.objects.create(game=game, number=i, campaign=campaign2)

    commander1.add_status_item(Senator.StatusItem.PREFERRED_ATTACKER)
    commander1.save()

    faction1 = commander1.faction
    faction2 = commander2.faction
    faction1.add_status_item(FactionStatusItem.DONE)
    faction1.save()
    faction2.add_status_item(FactionStatusItem.DONE)
    faction2.save()

    resolver = FakeRandomResolver()
    resolver.dice_rolls = [18, 18]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Campaign.objects.filter(game=game).exists() == False
    commander1.refresh_from_db()
    assert commander1.alive == True
    commander2.refresh_from_db()
    assert commander2.alive == True


@pytest.mark.django_db
def test_disputed_attack_order_resolved_by_dice(two_campaigns):
    # Arrange
    campaign1, campaign2 = two_campaigns
    game = campaign1.game
    commander1 = campaign1.commander
    commander2 = campaign2.commander

    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=campaign1)
    for i in range(11, 21):
        Legion.objects.create(game=game, number=i, campaign=campaign2)

    commander1.add_status_item(Senator.StatusItem.PREFERRED_ATTACKER)
    commander1.save()
    commander2.add_status_item(Senator.StatusItem.PREFERRED_ATTACKER)
    commander2.save()

    faction1 = commander1.faction
    faction2 = commander2.faction
    faction1.add_status_item(FactionStatusItem.DONE)
    faction1.save()
    faction2.add_status_item(FactionStatusItem.DONE)
    faction2.save()

    resolver = FakeRandomResolver()
    resolver.dice_rolls = [18, 18]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Campaign.objects.filter(game=game).exists() == False
    commander1.refresh_from_db()
    assert commander1.alive == True
    commander2.refresh_from_db()
    assert commander2.alive == True
