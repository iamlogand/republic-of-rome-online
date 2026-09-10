from collections import Counter
from typing import Sequence

from django.db.models import Count

from rorapp.helpers.text import to_sentence_case
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import Campaign, Fleet, Game, Log


def destroy_storm_fleets(game: Game, fleets: Sequence[Fleet]) -> None:
    """Destroy selected Roman fleets and log any newly unsupported campaigns."""
    selected_fleets = sorted(fleets, key=lambda fleet: fleet.number)
    selected_by_campaign = Counter(
        fleet.campaign_id
        for fleet in selected_fleets
        if fleet.campaign_id is not None
    )

    campaigns = list(
        Campaign.objects.filter(game=game, id__in=selected_by_campaign)
        .annotate(
            fleet_count=Count("fleets", distinct=True),
            legion_count=Count("legions", distinct=True),
        )
        .select_related("commander", "war")
    )
    newly_unsupported = []
    for campaign in campaigns:
        if campaign.commander is None:
            continue
        if campaign.war.naval_strength == 0 and campaign.legion_count == 0:
            continue

        fleet_count_after = campaign.fleet_count - selected_by_campaign[campaign.id]
        if campaign.war.naval_strength == 0:
            was_supported = campaign.fleet_count >= campaign.war.fleet_support
            is_supported = fleet_count_after >= campaign.war.fleet_support
        else:
            was_supported = campaign.fleet_count > 0
            is_supported = fleet_count_after > 0
        if was_supported and not is_supported:
            newly_unsupported.append(campaign)

    Fleet.objects.filter(
        game=game, id__in=[fleet.id for fleet in selected_fleets]
    ).delete()
    Log.create_object(
        game.id,
        f"Storm at sea destroyed {unit_list_to_string([], selected_fleets)}.",
    )

    for campaign in sorted(newly_unsupported, key=lambda item: item.id):
        campaign_name = to_sentence_case(campaign.display_name)
        if campaign.war.naval_strength == 0:
            Log.create_object(
                game.id,
                f"{campaign_name} no longer has sufficient fleet support for its land battle against the {campaign.war.name}. Unless sufficient fleet support is restored during the Senate phase, it will be automatically recalled.",
            )
        else:
            Log.create_object(
                game.id,
                f"{campaign_name} no longer has any fleets for its naval battle against the {campaign.war.name}. Unless at least one fleet is assigned during the Senate phase, it will be automatically recalled.",
            )
