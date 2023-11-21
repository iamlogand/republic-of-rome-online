from typing import List
from rorapp.functions.websocket_message_helper import update_websocket_message
from rorapp.models import Faction, Senator, Title
from rorapp.serializers import SenatorSerializer, FactionSerializer


def rank_senators_and_factions(game_id) -> List[dict]:
    """
    Assign the correct ranks to senators and set faction ranks based on the HRAO.

    Rank 0 is the HRAO and all subsequent ranks (1, 2, 3, etc) are the successors in order of succession.

    Args:
        game_id (int): The Game ID.

    Returns:
        List[dict]: The WebSocket messages to send.
    """

    # Get aligned alive senators
    senators = Senator.objects.filter(
        game=game_id, death_step__isnull=True, faction__isnull=False
    )

    # Sort by descending influence, descending oratory and ascending code (ID)
    senators = senators.order_by("-influence", "-oratory", "code")

    # Get major offices
    major_offices = Title.objects.filter(
        senator__game=game_id, major_office=True, end_step=None
    )

    # Order the major offices
    ordered_major_offices = [
        major_offices.filter(name="Dictator").first(),
        major_offices.filter(name__contains="Rome Consul").first(),
        major_offices.filter(name="Field Consul").first(),
        major_offices.filter(name="Censor").first(),
        major_offices.filter(name="Master of Horse").first(),
    ]

    # Remove None major offices
    ordered_major_offices = [
        office for office in ordered_major_offices if office is not None
    ]

    messages_to_send = []

    # Assign rank values
    rank_to_assign = 0
    while True:
        selected_senator = None

        # Assign the rank to a major office holder
        if rank_to_assign <= len(ordered_major_offices) - 1:
            selected_senator = ordered_major_offices[rank_to_assign].senator

        # Assign the rank to the first remaining senator
        else:
            selected_senator = senators.first()
            if selected_senator is None:
                break

        senators = senators.exclude(id=selected_senator.id)

        # Update senator's rank only if it's changed
        if selected_senator.rank != rank_to_assign:
            selected_senator.rank = rank_to_assign
            selected_senator.save()

            messages_to_send.append(
                update_websocket_message(
                    "senator", SenatorSerializer(selected_senator).data
                )
            )

        rank_to_assign += 1

    # Get unaligned and dead senators
    unaligned_senators = Senator.objects.filter(
        game=game_id, death_step__isnull=True, faction__isnull=True
    )
    dead_senators = Senator.objects.filter(game=game_id, death_step__isnull=False)
    unaligned_and_dead_senators = unaligned_senators.union(dead_senators)

    # Set rank to None for unaligned and dead senators
    for senator in unaligned_and_dead_senators:
        # Update senator's rank only if it's changed
        if senator.rank is not None:
            senator.rank = None
            senator.save()

            messages_to_send.append(
                update_websocket_message("senator", SenatorSerializer(senator).data)
            )

    # Get the HRAO
    hrao = Senator.objects.filter(game=game_id, death_step__isnull=True, rank=0).first()

    # Get factions in order of position
    factions = Faction.objects.filter(game=game_id).order_by("position")

    # Sort the factions into positional order
    factions_before_hrao_faction = []
    for i in range(len(factions)):
        if factions[i] == hrao.faction:
            sorted_factions = factions[i:] + factions_before_hrao_faction
            break
        else:
            factions_before_hrao_faction.append(factions[i])

    # Set faction ranks
    for rank in range(0, len(sorted_factions)):
        faction = sorted_factions[rank]

        # Update faction's rank only if it's changed
        if faction.rank != rank:
            faction.rank = rank
            faction.save()

            messages_to_send.append(
                update_websocket_message("faction", FactionSerializer(faction).data)
            )

    return messages_to_send
