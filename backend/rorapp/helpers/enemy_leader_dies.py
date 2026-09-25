from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import RandomResolver
from rorapp.helpers.deck import shuffle_card_into_top
from rorapp.helpers.kill_senator import CauseOfDeath, kill_senators
from rorapp.helpers.lay_down_command import lay_down_command
from rorapp.helpers.text import format_list
from rorapp.models import Campaign, EnemyLeader, Game, Log, Senator, War


def resolve_enemy_leader_dies(
    game: Game, leader: EnemyLeader, random_resolver: RandomResolver
) -> None:
    sues_for_peace = game.count_effect(GameEffect.ENEMY_LEADER_DIES) > 1
    game.remove_effect(GameEffect.ENEMY_LEADER_DIES)
    game.save()

    leader.delete()
    series_wars = list(
        War.objects.filter(
            game=game, series_name=leader.series_name, status=War.Status.ACTIVE
        ).order_by("index")
    )
    war = max(
        series_wars, key=lambda w: w.land_strength + w.naval_strength, default=None
    )
    if not sues_for_peace or war is None:
        Log.create_object(game.id, f"Enemy leader {leader.name} died.")
        return

    spoils = war.spoils // 2
    game.state_treasury += spoils
    game.deck = shuffle_card_into_top(
        game.deck, f"war:{war.name}", 6, random_resolver
    )
    game.save()
    Log.create_object(
        game.id,
        f"With the death of {leader.name}, the enemy sued for peace in the {war.name}. The State Treasury gained {spoils}T in spoils of war.",
    )

    for campaign in Campaign.objects.filter(war=war).order_by("id"):
        lay_down_command(campaign)

    # The war card leaves play, so its captives can no longer be ransomed (1.10.71)
    kill_senators(Senator.objects.filter(captor=war), CauseOfDeath.CAPTIVITY)
    war.delete()

    if series_wars == [war]:
        withdrawn = EnemyLeader.objects.filter(
            game=game, series_name=leader.series_name, active=True
        )
        names = [l.name for l in withdrawn]
        if names:
            withdrawn.update(active=False)
            Log.create_object(
                game.id, f"{format_list(names)} withdrew following the peace."
            )
