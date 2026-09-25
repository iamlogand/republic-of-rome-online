from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import RandomResolver
from rorapp.helpers.deck import shuffle_card_into_top
from rorapp.helpers.kill_senator import CauseOfDeath, kill_senators
from rorapp.helpers.lay_down_command import lay_down_command
from rorapp.helpers.provinces import award_provinces_for_war
from rorapp.helpers.text import format_list
from rorapp.models import Campaign, EnemyLeader, Game, Log, Senator, War


def apply_new_alliance(game: Game, war: War, random_resolver: RandomResolver) -> None:
    another_new_alliance = game.count_effect(GameEffect.NEW_ALLIANCE) > 1
    spoils = war.spoils if another_new_alliance else war.spoils // 2
    game.state_treasury += spoils
    game.remove_effect(GameEffect.NEW_ALLIANCE)

    log_text = f"Rome's new alliance brought an end to the {war.name}."
    if spoils:
        log_text += f" The State Treasury gained {spoils}T in spoils of war."
    if not another_new_alliance:
        log_text += " The war was shuffled into the top six cards of the deck."
    Log.create_object(game.id, log_text)

    for campaign in Campaign.objects.filter(game=game, war=war).select_related(
        "commander", "master_of_horse"
    ):
        lay_down_command(campaign)

    # The war ends either way, so its captives can no longer be ransomed (1.10.71)
    kill_senators(Senator.objects.filter(captor=war), CauseOfDeath.CAPTIVITY)

    if another_new_alliance:
        war.status = War.Status.DEFEATED
        war.unprosecuted = False
        war.save()
        award_provinces_for_war(game, war)
    else:
        game.deck = shuffle_card_into_top(
            game.deck, f"war:{war.name}", 6, random_resolver
        )
        war.delete()
    game.save()

    if not War.objects.filter(
        game=game, series_name=war.series_name, status=War.Status.ACTIVE
    ).exists():
        leaders = EnemyLeader.objects.filter(
            game=game, series_name=war.series_name, active=True
        )
        leader_names = [leader.name for leader in leaders]
        if leader_names:
            leaders.update(active=False)
            Log.create_object(
                game.id,
                f"{format_list(leader_names)} withdrew following the peace.",
            )
