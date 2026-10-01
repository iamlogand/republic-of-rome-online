from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import Campaign, Fleet, Legion, Log, Senator, War


def _proportional_charges(balances: list[int], total: int) -> list[int]:
    n = len(balances)
    total_balance = sum(balances)
    if n == 0 or total <= 0 or total_balance == 0:
        return [0] * n
    floors = [(b * total) // total_balance for b in balances]
    fractional_parts = [(b * total) % total_balance for b in balances]
    order = sorted(range(n), key=lambda i: -fractional_parts[i])
    for i in range(total - sum(floors)):
        floors[order[i]] += 1
    return [min(floors[i], balances[i]) for i in range(n)]


def pay_rebel_maintenance(game_id: int) -> int:
    """Pay maintenance for rebel forces from the rebel's available funds (§1.11.35).

    Deducts from personal treasury, then secondary rebels (proportionally),
    then faction treasury. Returns the number of units that still need to be
    released because the rebel could not afford them; zero means fully paid.
    """
    revolt = (
        War.objects.filter(game_id=game_id, primary_rebel__isnull=False)
        .exclude(status=War.Status.DEFEATED)
        .select_related("primary_rebel__faction")
        .first()
    )
    if revolt is None:
        return 0

    primary_rebel = revolt.primary_rebel
    if primary_rebel is None:
        return 0

    rebel_campaign = Campaign.objects.filter(
        game_id=game_id, commander=primary_rebel
    ).first()
    if rebel_campaign is None:
        return 0

    chargeable_legions = list(
        Legion.objects.filter(campaign=rebel_campaign)
        .exclude(veteran=True, allegiance=primary_rebel)
        .order_by("number")
    )
    chargeable_fleets = list(
        Fleet.objects.filter(campaign=rebel_campaign).order_by("number")
    )

    total_cost = (len(chargeable_legions) + len(chargeable_fleets)) * 2
    if total_cost == 0:
        return 0

    remaining = total_cost

    personal_payment = min(primary_rebel.talents, remaining)
    primary_rebel.talents -= personal_payment
    primary_rebel.save()
    remaining -= personal_payment

    if remaining > 0:
        secondary_rebels = list(
            Senator.objects.filter(game_id=game_id, rebel=True, alive=True)
            .exclude(id=primary_rebel.id)
            .order_by("id")
        )
        if secondary_rebels:
            charges = _proportional_charges([s.talents for s in secondary_rebels], remaining)
            for senator, charge in zip(secondary_rebels, charges):
                senator.talents -= charge
                senator.save()
            remaining -= sum(charges)

    faction = primary_rebel.faction
    if remaining > 0 and faction:
        faction_payment = min(faction.treasury, remaining)
        faction.treasury -= faction_payment
        faction.save()
        remaining -= faction_payment

    units_to_release = remaining // 2

    if units_to_release == 0:
        Log.create_object(
            game_id,
            f"{primary_rebel.display_name} spent {total_cost}T maintaining "
            f"{unit_list_to_string(chargeable_legions, chargeable_fleets)}.",
        )

    return units_to_release
