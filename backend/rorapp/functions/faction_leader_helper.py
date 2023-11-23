from rest_framework.response import Response
from typing import Optional
from rorapp.functions.action_helper import delete_old_actions
from rorapp.functions.forum_phase_helper import (
    get_next_faction_in_forum_phase,
)
from rorapp.functions.mortality_phase_helper import setup_mortality_phase
from rorapp.functions.websocket_message_helper import (
    send_websocket_messages,
    create_websocket_message,
    destroy_websocket_message,
    update_websocket_message,
)
from rorapp.functions.turn_starter import start_next_turn
from rorapp.models import (
    Action,
    ActionLog,
    Faction,
    Game,
    Senator,
    SenatorActionLog,
    Step,
    Title,
)
from rorapp.serializers import (
    ActionLogSerializer,
    ActionSerializer,
    StepSerializer,
    TitleSerializer,
    SenatorActionLogSerializer,
)


def select_faction_leader(action_id, data) -> Response:
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
        senator = Senator.objects.filter(faction=faction, death_step__isnull=True).get(
            id=data.get("leader_id")
        )
    except Senator.DoesNotExist:
        return Response(
            {"message": "Selected faction leader (senator) was not found"}, status=404
        )

    return set_faction_leader(senator.id)


def set_faction_leader(senator_id: int) -> Response:
    senator = Senator.objects.get(id=senator_id)
    game = Game.objects.get(id=senator.game.id)
    faction = Faction.objects.get(id=senator.faction.id)
    step = Step.objects.filter(phase__turn__game=game.id).latest("index")
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

    messages_to_send.append(complete_action(action))
    messages_to_send.extend(proceed_to_next_step_if_faction_phase(game.id, step))
    messages_to_send.extend(proceed_to_next_step_if_forum_phase(game.id, step, faction))
    messages_to_send.append(delete_old_actions(game.id))
    send_websocket_messages(game.id, messages_to_send)

    return Response({"message": "Faction leader selected"}, status=200)


def get_previous_title(faction) -> Optional[Title]:
    previous_titles = (
        Title.objects.filter(senator__faction=faction)
        .filter(name="Faction Leader")
        .filter(end_step__isnull=True)
    )
    return None if previous_titles.count() == 0 else previous_titles.first()


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
) -> [dict]:
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
    if all_action_logs.count() > 0:
        latest_action_log = all_action_logs[0]
        new_action_log_index = latest_action_log.index + 1
    action_log = ActionLog(
        index=new_action_log_index,
        step=step,
        type="select_faction_leader",
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


def complete_action(action) -> dict:
    action.completed = True
    action.save()
    return update_websocket_message("action", ActionSerializer(action).data)


def proceed_to_next_step_if_faction_phase(game_id, step) -> [dict]:
    messages_to_send = []
    if (
        step.phase.name == "Faction"
        and Action.objects.filter(step__id=step.id, completed=False).count() == 0
    ):
        messages_to_send.extend(setup_mortality_phase(game_id))
    return messages_to_send


def proceed_to_next_step_if_forum_phase(game_id, step, faction) -> [dict]:
    messages_to_send = []
    if step.phase.name == "Forum":
        next_faction = get_next_faction_in_forum_phase(faction)

        if next_faction is not None:
            new_step = Step(index=step.index + 1, phase=step.phase)
            new_step.save()

            action = Action(
                step=new_step,
                faction=next_faction,
                type="select_faction_leader",
                required=True,
                parameters=None,
            )
            action.save()
            messages_to_send.append(
                create_websocket_message("step", StepSerializer(new_step).data)
            )
            messages_to_send.append(
                create_websocket_message("action", ActionSerializer(action).data)
            )
        else:
            messages_to_send.extend(start_next_turn(game_id, step))
    return messages_to_send
