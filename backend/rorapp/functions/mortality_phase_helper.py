import os
import json
from typing import List
from django.conf import settings
from rest_framework.response import Response
from rorapp.functions.mortality_chit_helper import draw_mortality_chits
from rorapp.functions.rank_helper import rank_senators_and_factions
from rorapp.functions.websocket_message_helper import (
    send_websocket_messages,
    create_websocket_message,
    update_websocket_message,
    destroy_websocket_message,
)
from rorapp.models import (
    Action,
    ActionLog,
    Faction,
    Game,
    Phase,
    Senator,
    SenatorActionLog,
    Step,
    Title,
    Turn,
)
from rorapp.serializers import (
    ActionLogSerializer,
    ActionSerializer,
    StepSerializer,
    TitleSerializer,
    PhaseSerializer,
    SenatorSerializer,
    SenatorActionLogSerializer,
)


def setup_mortality_phase(game_id: int) -> List[dict]:
    """
    Setup the mortality phase.

    Includes creation of a new step, phase, and actions for each faction.

    Args:
        game_id (int): The game ID.

    Returns:
        List[dict]: The list of WebSocket messages to send.
    """

    messages_to_send = []
    game = Game.objects.get(id=game_id)
    latest_step = Step.objects.filter(phase__turn__game=game).order_by("-index")[0]
    turn = Turn.objects.get(id=latest_step.phase.turn.id)
    new_phase = Phase(name="Mortality", index=1, turn=turn)
    new_phase.save()
    messages_to_send.append(
        create_websocket_message("phase", PhaseSerializer(new_phase).data)
    )

    new_step = Step(index=latest_step.index + 1, phase=new_phase)
    new_step.save()
    messages_to_send.append(
        create_websocket_message("step", StepSerializer(new_step).data)
    )

    factions = Faction.objects.filter(game__id=game.id)
    for faction in factions:
        action = Action(
            step=new_step,
            faction=faction,
            type="face_mortality",
            required=True,
            parameters=None,
        )
        action.save()
        messages_to_send.append(
            create_websocket_message("action", ActionSerializer(action).data)
        )

    return messages_to_send


def face_mortality(
    action_id: int, chit_codes: List[int] | None = None
) -> Response:
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
    if Action.objects.filter(step__id=action.step.id, completed=False).count() == 0:
        messages_to_send.extend(resolve_mortality(game.id, chit_codes))

    send_websocket_messages(game.id, messages_to_send)
    return Response({"message": "Ready for mortality"}, status=200)


def resolve_mortality(game_id: int, chit_codes: List[int] | None = None):
    """
    Resolve the mortality phase by randomly killing zero or more senators.

    Args:
        game_id (int): The game ID.
        chit_codes (List[int] | None, optional): An optional list of chits, which when provided will override the randomly drawn chits. Defaults to None.

    Returns:
        _type_: _description_
    """
    
    game = Game.objects.get(id=game_id)
    latest_step = Step.objects.filter(phase__turn__game=game_id).order_by("-index")[0]
    # Read senator presets
    senator_json_path = os.path.join(
        settings.BASE_DIR, "rorapp", "presets", "senator.json"
    )
    with open(senator_json_path, "r") as file:
        senators_dict = json.load(file)

    # Perform mortality
    drawn_codes = draw_mortality_chits(1) if chit_codes is None else chit_codes
    messages_to_send = []
    killed_senator_count = 0
    for code in drawn_codes:
        senators = Senator.objects.filter(
            game=game_id, death_step__isnull=True, code=code
        )
        if senators.exists():
            senator = senators.first()
            senators_former_faction = senator.faction

            # Kill the senator
            senator.death_step = latest_step
            senator.save()
            killed_senator_count += 1

            messages_to_send.append(
                update_websocket_message("senator", SenatorSerializer(senator).data)
            )

            # End associated titles
            titles_to_end = Title.objects.filter(
                senator__id=senator.id, end_step__isnull=True
            )
            ended_major_office = None
            heir = None
            if titles_to_end.exists():
                for title in titles_to_end:
                    title.end_step = latest_step
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
                            name="Faction Leader", senator=heir, start_step=latest_step
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
                step=latest_step,
                type="face_mortality",
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
            index=new_action_log_index, step=latest_step, type="face_mortality"
        )
        action_log.save()
        messages_to_send.append(
            create_websocket_message("action_log", ActionLogSerializer(action_log).data)
        )

    # Update senator ranks
    messages_to_send.extend(rank_senators_and_factions(game_id))

    # Proceed to the forum phase
    new_phase = Phase(
        name="Forum", index=latest_step.phase.index + 1, turn=latest_step.phase.turn
    )
    new_phase.save()
    messages_to_send.append(
        create_websocket_message("phase", PhaseSerializer(new_phase).data)
    )
    new_step = Step(index=latest_step.index + 1, phase=new_phase)
    new_step.save()
    messages_to_send.append(
        create_websocket_message("step", StepSerializer(new_step).data)
    )

    # Create actions for the forum phase
    first_faction = Faction.objects.filter(game__id=game_id).order_by("rank").first()
    action = Action(
        step=new_step,
        faction=first_faction,
        type="select_faction_leader",
        required=True,
        parameters=None,
    )
    action.save()

    messages_to_send.append(
        create_websocket_message("action", ActionSerializer(action).data)
    )

    return messages_to_send
