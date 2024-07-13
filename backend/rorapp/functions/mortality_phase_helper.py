import os
import json
from django.conf import settings
from rest_framework.response import Response
from rorapp.functions.mortality_chit_helper import draw_mortality_chits
from rorapp.functions.progress_helper import get_step
from rorapp.functions.rank_helper import rank_senators_and_factions
from rorapp.functions.revenue_phase_helper import generate_personal_revenue
from rorapp.functions.websocket_message_helper import (
    create_websocket_message,
    destroy_websocket_message,
)
from rorapp.models import (
    Action,
    ActionLog,
    Game,
    Senator,
    SenatorActionLog,
    Title,
)
from rorapp.serializers import (
    ActionLogSerializer,
    TitleSerializer,
    SenatorSerializer,
    SenatorActionLogSerializer,
)


def face_mortality(
    action_id: int, chit_codes: list[int] | None = None
) -> tuple[Response, list[dict]]:
    """
    Ready up for facing mortality.

    This function is called when a faction acknowledges that they are ready to face mortality.

    Args:
        action_id (int): The action ID.

    Returns:
        Response: The response with a message and a status code.
    """

    messages_to_send = []

    # Mark the action as complete
    action = Action.objects.get(id=action_id)
    action.completed = True
    action.save()

    messages_to_send.append(destroy_websocket_message("action", action_id))
    game = Game.objects.get(id=action.faction.game.id)

    # If this the last faction to face mortality, perform mortality and proceed to the next step
    if not Action.objects.filter(step__id=action.step.id, completed=False).exists():
        messages_to_send.extend(resolve_mortality(game.id, chit_codes))

    return Response({"message": "Ready for mortality"}, status=200), messages_to_send


def resolve_mortality(game_id: int, chit_codes: list[int] | None = None) -> list[dict]:
    """
    Resolve the mortality phase by randomly killing zero or more senators.

    Args:
        game_id (int): The game ID.
        chit_codes (list[int] | None, optional): An optional list of chits, which when provided will override the randomly drawn chits. Defaults to None.

    Returns:
        dict: The WebSocket messages to send.
    """

    game = Game.objects.get(id=game_id)
    step = get_step(game_id)
    # Read senator data
    senator_json_path = os.path.join(
        settings.BASE_DIR, "rorapp", "data", "senator.json"
    )
    with open(senator_json_path, "r") as file:
        senators_dict = json.load(file)

    # Perform mortality
    drawn_codes = draw_mortality_chits(1) if chit_codes is None else chit_codes
    messages_to_send = []
    killed_senator_count = 0
    for code in drawn_codes:
        senators = Senator.objects.filter(game=game_id, alive=True, code=code)
        if senators.exists():
            senator = senators.first()
            assert isinstance(senator, Senator)
            senators_former_faction = senator.faction

            # Kill the senator
            senator.alive = False
            senator.save()
            killed_senator_count += 1

            messages_to_send.append(
                create_websocket_message("senator", SenatorSerializer(senator).data)
            )

            # End associated titles
            titles_to_end = Title.objects.filter(
                senator__id=senator.id, end_step__isnull=True
            )
            ended_major_office = None
            heir = None
            if titles_to_end.exists():
                for title in titles_to_end:
                    title.end_step = step
                    title.save()

                    if title.major_office is True:
                        ended_major_office = title.name

                    # If the title is faction leader, create an heir senator as faction leader
                    if title.name == "Faction Leader":
                        # Create a new senator
                        heir = Senator(
                            name=senator.name,
                            game=game,
                            faction=senators_former_faction,
                            code=senator.code,
                            generation=senator.generation + 1,
                            military=senators_dict[senator.name]["military"],
                            oratory=senators_dict[senator.name]["oratory"],
                            loyalty=senators_dict[senator.name]["loyalty"],
                            influence=senators_dict[senator.name]["influence"],
                        )
                        heir.save()

                        messages_to_send.append(
                            create_websocket_message(
                                "senator", SenatorSerializer(heir).data
                            )
                        )

                        # Create a new title for the heir
                        new_faction_leader = Title(
                            name="Faction Leader", senator=heir, start_step=step
                        )
                        new_faction_leader.save()

                        messages_to_send.append(
                            create_websocket_message(
                                "title", TitleSerializer(new_faction_leader).data
                            )
                        )

            # Create an action_log and action_log relations
            new_action_log_index = (
                ActionLog.objects.filter(step__phase__turn__game=game_id)
                .order_by("-index")[0]
                .index
                + 1
            )
            action_log = ActionLog(
                index=new_action_log_index,
                step=step,
                type="mortality",
                faction=senators_former_faction,
                data={
                    "senator": senator.id,
                    "major_office": ended_major_office,
                    "heir_senator": heir.id if heir else None,
                },
            )
            action_log.save()
            messages_to_send.append(
                create_websocket_message(
                    "action_log", ActionLogSerializer(action_log).data
                )
            )

            senator_action_log = SenatorActionLog(
                senator=senator, action_log=action_log
            )
            senator_action_log.save()
            messages_to_send.append(
                create_websocket_message(
                    "senator_action_log",
                    SenatorActionLogSerializer(senator_action_log).data,
                )
            )

            if heir:
                heir_senator_action_log = SenatorActionLog(
                    senator=heir, action_log=action_log
                )
                heir_senator_action_log.save()
                messages_to_send.append(
                    create_websocket_message(
                        "senator_action_log",
                        SenatorActionLogSerializer(heir_senator_action_log).data,
                    )
                )

    # If nobody dies, issue a notification to say so
    if killed_senator_count == 0:
        new_action_log_index = (
            ActionLog.objects.filter(step__phase__turn__game=game_id)
            .order_by("-index")[0]
            .index
            + 1
        )
        action_log = ActionLog(
            index=new_action_log_index, step=step, type="mortality"
        )
        action_log.save()
        messages_to_send.append(
            create_websocket_message("action_log", ActionLogSerializer(action_log).data)
        )

    # Update senator ranks
    messages_to_send.extend(rank_senators_and_factions(game_id))

    # Generate personal revenue
    messages_to_send.extend(generate_personal_revenue(game_id))

    return messages_to_send
