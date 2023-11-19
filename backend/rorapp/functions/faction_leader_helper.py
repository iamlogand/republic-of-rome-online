from rest_framework.response import Response
from typing import Optional
from rorapp.functions.forum_phase_helper import (
    get_next_faction_in_forum_phase,
)
from rorapp.functions.mortality_phase_helper import setup_mortality_phase
from rorapp.functions.websocket_message_helper import (
    send_websocket_messages,
    create_websocket_message,
    destroy_websocket_message,
)
from rorapp.functions.turn_starter import start_next_turn
from rorapp.models import (
    Action,
    Step,
    Senator,
    Title,
    ActionLog,
    SenatorActionLog,
)
from rorapp.serializers import (
    ActionLogSerializer,
    ActionSerializer,
    StepSerializer,
    TitleSerializer,
    SenatorActionLogSerializer,
)


def select_faction_leader(game, faction, action, step, data):
    """
    Select a faction leader.

    This function is called when a player selects their faction leader during the faction phase or the forum phase.
    Can handle scenarios where there is or is not a faction leader already assigned.

    :param game: the game
    :param faction: the faction selecting the leader
    :param action: the action
    :param step: the step
    :param data: the data, expects a `leader_id` for the senator selected as the faction leader

    :return: a response with a message and a status code
    :rtype: rest_framework.response.Response
    """

    try:
        senator = Senator.objects.filter(faction=faction, death_step__isnull=True).get(
            id=data.get("leader_id")
        )
    except Senator.DoesNotExist:
        return Response(
            {"message": "Selected faction leader (senator) was not found"}, status=404
        )

    previous_title = get_previous_title(faction)
    messages_to_send = []
    if previous_title is not None and previous_title.senator != senator:
        messages_to_send.append(end_previous_title(previous_title, step))

    if previous_title is None or previous_title.senator != senator:
        messages_to_send.append(create_new_title(senator, step))
        previous_senator_id = (
            None if previous_title is None else previous_title.senator.id
        )
        messages_to_send.extend(
            create_action_logs_and_related_messages(
                game, step, faction, senator, previous_senator_id
            )
        )

    messages_to_send.append(delete_action(action))
    create_completed_action(step, faction)
    messages_to_send.extend(proceed_to_next_step_if_faction_phase(step, game))
    messages_to_send.extend(proceed_to_next_step_if_forum_phase(game, step, faction))
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
    game, step, faction, senator, previous_senator_id
) -> [dict]:
    messages_to_send = []

    action_log = create_action_log(game, step, faction, senator, previous_senator_id)
    messages_to_send.append(
        create_websocket_message("action_log", ActionLogSerializer(action_log).data)
    )

    messages_to_send.append(create_senator_action_log(senator, action_log))

    if previous_senator_id:
        previous_senator = Senator.objects.get(id=previous_senator_id)
        messages_to_send.append(create_senator_action_log(previous_senator, action_log))

    return messages_to_send


def create_action_log(game, step, faction, senator, previous_senator_id) -> ActionLog:
    all_action_logs = ActionLog.objects.filter(step__phase__turn__game=game).order_by(
        "-index"
    )
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


def delete_action(action) -> dict:
    action_id = action.id
    action.delete()
    return destroy_websocket_message("action", action_id)


def create_completed_action(step, faction) -> None:
    completed_action = Action(
        step=step,
        faction=faction,
        type="select_faction_leader",
        required=True,
        completed=True,
    )
    completed_action.save()
    return


def proceed_to_next_step_if_faction_phase(step, game) -> [dict]:
    messages_to_send = []
    if (
        step.phase.name == "Faction"
        and Action.objects.filter(step__id=step.id, completed=False).count() == 0
    ):
        messages_to_send.append(setup_mortality_phase(game.id))
    return messages_to_send


def proceed_to_next_step_if_forum_phase(game, step, faction) -> [dict]:
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
            messages_to_send.extend(start_next_turn(game, step))
    return messages_to_send
