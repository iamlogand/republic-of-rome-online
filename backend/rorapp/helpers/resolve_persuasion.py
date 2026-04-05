from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.models import Faction, Game, Log, Senator


def resolve_persuasion(
    game_id: int,
    persuading_senator: Senator,
    target: Senator,
    use_blackmail: bool,
    random_resolver: RandomResolver,
) -> None:
    persuading_senator.refresh_from_db()
    target.refresh_from_db()

    game = Game.objects.get(id=game_id)
    persuading_faction = persuading_senator.faction
    if not persuading_faction:
        raise ValueError(f"Senator {persuading_senator.display_name} has no faction")

    total_bribe = persuading_senator.get_bribe_amount() or 0
    modifier = (
        persuading_senator.oratory
        + persuading_senator.influence
        + 2 * total_bribe
        - target.loyalty
        - target.talents
        - (7 if target.faction_id else 0)
    )
    threshold = 9 if game.era_ends else 10
    roll = random_resolver.roll_dice() + random_resolver.roll_dice()
    success = roll <= modifier and roll < threshold

    if success:
        message = f"{persuading_senator.display_name} successfully persuaded {target.display_name} to"
        if target.faction:
            message += f" leave {target.faction.display_name} and"
        message += f" join {persuading_faction.display_name}."
        Log.create_object(game_id, message)
        target.faction = persuading_faction
        target.save()
    else:
        Log.create_object(
            game_id,
            f"{persuading_senator.display_name} failed to persuade {target.display_name}.",
        )
        if use_blackmail:
            influence_loss = random_resolver.roll_dice() + random_resolver.roll_dice()
            popularity_loss = random_resolver.roll_dice() + random_resolver.roll_dice()
            target.influence = max(0, target.influence - influence_loss)
            target.popularity = max(0, target.popularity - popularity_loss)
            target.save()
            Log.create_object(
                game_id,
                f"Blackmail: {target.display_name} lost {influence_loss} influence"
                f" and {popularity_loss} popularity.",
            )

    for senator in Senator.objects.filter(game=game_id):
        senator.remove_status_item(Senator.StatusItem.PERSUADER)
        senator.remove_status_item(Senator.StatusItem.PERSUASION_TARGET)
        senator.set_bribe_amount(None)
        senator.save()

    for faction in Faction.objects.filter(game=game_id):
        faction.remove_status_item(FactionStatusItem.COUNTER_BRIBED)
        faction.remove_status_item(FactionStatusItem.SKIPPED)
        faction.save()

    game.sub_phase = Game.SubPhase.ATTRACT_KNIGHT
    game.save()
