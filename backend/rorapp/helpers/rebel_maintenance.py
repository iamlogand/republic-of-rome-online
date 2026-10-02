from rorapp.helpers.text import pluralize
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import Campaign, Legion, Log, Senator, War


def _charge_secondary_rebels(
    game_id: int, primary_rebel_id: int, total_charge: int
) -> int:
    """Charge `total_charge` across secondary rebels proportionally to their talents.

    Returns the total amount actually collected.
    """
    secondary_rebels = list(
        Senator.objects.filter(game_id=game_id, rebel=True, alive=True)
        .exclude(id=primary_rebel_id)
        .order_by("-talents")
    )
    if not secondary_rebels:
        return 0
    total_balance = sum(s.talents for s in secondary_rebels)
    if total_balance >= total_charge:

        # Build list of floored proportional charges
        charges = [
            (s.talents * total_charge) // total_balance for s in secondary_rebels
        ]

        # Build list of remainders left behind by the above charges
        remainders = [
            (s.talents * total_charge) % total_balance for s in secondary_rebels
        ]

        # Build list of indices of charges sorted by highest remainder
        indices_by_largest_remainder = sorted(
            range(len(secondary_rebels)), key=lambda i: -remainders[i]
        )

        # Distribute the leftover 1T at a time, prioritizing those with the highest remainder
        leftover = total_charge - sum(charges)
        for i in indices_by_largest_remainder[:leftover]:
            charges[i] += 1
    else:
        charges = [s.talents for s in secondary_rebels]
    for i, senator in enumerate(secondary_rebels):
        senator.talents -= charges[i]
        senator.save()
    return sum(charges)


def pay_rebel_maintenance(game_id: int) -> int:
    """Pay maintenance for rebel forces from the rebel's available funds (§1.11.35)"""

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

    total_cost = len(chargeable_legions) * 2
    if total_cost == 0:
        return 0

    remaining = total_cost

    personal_payment = min(primary_rebel.talents, remaining)
    primary_rebel.talents -= personal_payment
    primary_rebel.save()
    remaining -= personal_payment

    if remaining > 0:
        remaining -= _charge_secondary_rebels(game_id, primary_rebel.id, remaining)

    faction = primary_rebel.faction
    if remaining > 0 and faction:
        faction_payment = min(faction.treasury, remaining)
        faction.treasury -= faction_payment
        faction.save()
        remaining -= faction_payment

    units_to_release = remaining // 2

    amount_paid = total_cost - remaining
    if units_to_release == 0:
        Log.create_object(
            game_id,
            f"The rebels spent {total_cost}T maintaining "
            f"{unit_list_to_string(chargeable_legions, [])}.",
        )
    elif amount_paid > 0:
        Log.create_object(
            game_id,
            f"The rebels spent {amount_paid}T but could not afford full maintenance "
            f"for {unit_list_to_string(chargeable_legions, [])} "
            f"and must release {pluralize(units_to_release, 'unit')}.",
        )

    return units_to_release
