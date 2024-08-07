from typing import List
from rest_framework.response import Response
from rorapp.functions.action_helper import delete_old_actions
from rorapp.functions.concession_helper import generate_assign_concessions_action
from rorapp.functions.forum_phase_helper import (
    generate_select_faction_leader_action,
    initiate_situation,
)
from rorapp.functions.progress_helper import (
    create_step_and_message,
    get_phase,
    get_step,
)
from rorapp.functions.revolution_phase_starter import start_revolution_phase
from rorapp.functions.websocket_message_helper import (
    create_websocket_message,
    destroy_websocket_message,
)
from rorapp.functions.game_ender import end_game_with_influence_victory
from rorapp.functions.chromatic_order_helper import get_next_faction_in_chromatic_order
from rorapp.models import (
    Action,
    ActionLog,
    Faction,
    Game,
    Senator,
    SenatorActionLog,
    Title,
)
from rorapp.models.step import Step
from rorapp.serializers import (
    ActionLogSerializer,
    ActionSerializer,
    TitleSerializer,
    SenatorActionLogSerializer,
)
from rorapp.serializers.step import StepSerializer


def select_faction_leader_from_action(
    action_id: int, data: dict
) -> tuple[Response, List[dict]]:
    """
    Select a faction leader.

    This function is called when a player selects their faction leader during the faction phase or the forum phase.
    Can handle scenarios where there is or is not a faction leader already assigned.

    Args:
        action_id (int): The action ID.

    Returns:
        Response: The response with a message and a status code.
    """

    try:
        action = Action.objects.get(id=action_id)
        faction = Faction.objects.get(id=action.faction.id)
        senator = Senator.objects.filter(faction=faction, alive=True).get(
            id=data.get("leader_id")
        )
    except Senator.DoesNotExist:
        return Response(
            {"message": "Selected faction leader (senator) was not found"}, status=404
        ), []

    return select_faction_leader(senator.id)


def select_faction_leader(senator_id: int) -> tuple[Response, List[dict]]:
    senator = Senator.objects.get(id=senator_id)
    game = Game.objects.get(id=senator.game.id)
    assert isinstance(senator.faction, Faction)
    faction = Faction.objects.get(id=senator.faction.id)
    step = get_step(game.id)
    action = Action.objects.get(
        step=step, faction=faction, type="select_faction_leader"
    )

    previous_title = get_previous_title(faction)
    messages_to_send = []
    if previous_title is not None and previous_title.senator.id != senator_id:
        messages_to_send.append(end_previous_title(previous_title, step))

    if previous_title is None or previous_title.senator.id != senator_id:
        messages_to_send.append(create_new_title(senator, step))
        previous_senator_id = (
            None if previous_title is None else previous_title.senator.id
        )
        messages_to_send.extend(
            create_action_logs_and_related_messages(
                game.id, step, faction, senator, previous_senator_id
            )
        )

    messages_to_send.append(complete_action(action, senator.id))
    messages_to_send.extend(proceed_to_next_step_if_faction_phase(game.id, step))
    messages_to_send.extend(proceed_to_next_step_if_forum_phase(game.id, step, faction))
    messages_to_send.extend(delete_old_actions(game.id))

    return Response(
        {"message": "Faction leader selected"}, status=200
    ), messages_to_send


def get_previous_title(faction) -> Title | None:
    previous_titles = (
        Title.objects.filter(senator__faction=faction)
        .filter(name="Faction Leader")
        .filter(end_step__isnull=True)
    )
    return None if not previous_titles.exists() else previous_titles.first()


def end_previous_title(previous_title, step) -> dict:
    previous_title.end_step = step
    previous_title.save()
    return destroy_websocket_message("title", previous_title.id)


def create_new_title(senator, step) -> dict:
    title = Title(name="Faction Leader", senator=senator, start_step=step)
    title.save()
    return create_websocket_message("title", TitleSerializer(title).data)


def create_action_logs_and_related_messages(
    game_id, step, faction, senator, previous_senator_id
) -> List[dict]:
    messages_to_send = []

    action_log = create_action_log(game_id, step, faction, senator, previous_senator_id)
    messages_to_send.append(
        create_websocket_message("action_log", ActionLogSerializer(action_log).data)
    )

    messages_to_send.append(create_senator_action_log(senator, action_log))

    if previous_senator_id:
        previous_senator = Senator.objects.get(id=previous_senator_id)
        messages_to_send.append(create_senator_action_log(previous_senator, action_log))

    return messages_to_send


def create_action_log(
    game_id, step, faction, senator, previous_senator_id
) -> ActionLog:
    all_action_logs = ActionLog.objects.filter(
        step__phase__turn__game=game_id
    ).order_by("-index")
    new_action_log_index = 0
    if all_action_logs.exists():
        latest_action_log = all_action_logs[0]
        new_action_log_index = latest_action_log.index + 1
    action_log = ActionLog(
        index=new_action_log_index,
        step=step,
        type="new_faction_leader",
        faction=faction,
        data={"senator": senator.id, "previous_senator": previous_senator_id},
    )
    action_log.save()
    return action_log


def create_senator_action_log(senator, action_log) -> dict:
    senator_action_log = SenatorActionLog(senator=senator, action_log=action_log)
    senator_action_log.save()
    return create_websocket_message(
        "senator_action_log", SenatorActionLogSerializer(senator_action_log).data
    )


def complete_action(action: Action, senator_id: int) -> dict:
    action.completed = True
    action.parameters = senator_id
    action.save()
    return create_websocket_message("action", ActionSerializer(action).data)


def proceed_to_next_step_if_faction_phase(game_id, step) -> List[dict]:
    messages_to_send = []
    if (
        step.phase.name == "Faction"
        and not Action.objects.filter(step__id=step.id, completed=False).exists()
    ):
        messages_to_send.extend(generate_assign_concessions_action(game_id))
    return messages_to_send


def proceed_to_next_step_if_forum_phase(game_id, step, faction) -> List[dict]:
    messages_to_send = []
    if step.phase.name.endswith("Forum"):
        next_faction = get_next_faction_in_chromatic_order(faction)

        if next_faction is not None:
            if step.phase.name.startswith("Final"):
                new_step, message = create_step_and_message(faction.game.id)
                messages_to_send.append(message)
                messages_to_send.append(
                    generate_select_faction_leader_action(next_faction, new_step)
                )
            else:
                messages_to_send.extend(initiate_situation(next_faction.id))
        else:
            if step.phase.name.startswith("Final"):
                messages_to_send.extend(end_game_with_influence_victory(game_id))
            else:
                messages_to_send.extend(start_revolution_phase(game_id))
    return messages_to_send
