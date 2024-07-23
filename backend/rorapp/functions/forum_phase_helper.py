from typing import List
from rest_framework.response import Response
from rorapp.functions.progress_helper import (
    create_step_and_message,
    get_phase,
    get_step,
)
from rorapp.functions.senator_helper import create_new_family
from rorapp.functions.war_helper import create_new_war
from rorapp.functions.enemy_leader_helper import create_new_enemy_leader
from rorapp.functions.secret_helper import create_new_secret
from rorapp.functions.websocket_message_helper import (
    create_websocket_message,
    destroy_websocket_message,
)
from rorapp.models import (
    Action,
    ActionLog,
    Faction,
    Senator,
    Situation,
    Step,
)
from rorapp.serializers import (
    ActionSerializer,
    ActionLogSerializer,
    PhaseSerializer,
    StepSerializer,
)


def generate_select_faction_leader_action(faction: Faction, step: Step) -> dict:
    senators = Senator.objects.filter(faction=faction, alive=True)
    senator_id_list = [senator.id for senator in senators]
    action = Action(
        step=step,
        faction=faction,
        type="select_faction_leader",
        required=True,
        parameters=senator_id_list,
    )
    action.save()
    return create_websocket_message("action", ActionSerializer(action).data)


def initiate_situation(faction_id: int) -> list[dict]:
    """
    Initiate a random situation.

    This function is called when a player initiates a situation during the forum phase.

    Args:
        action_id (int): The action ID.

    Returns:
        dict: The response with a message and a status code.
    """
    messages_to_send = []

    faction = Faction.objects.get(id=faction_id)
    assert isinstance(faction, Faction)

    # Get situation
    situation = Situation.objects.filter(game=faction.game).order_by("index").last()
    assert isinstance(situation, Situation)

    _, message = create_step_and_message(faction.game.id)
    messages_to_send.append(message)

    if situation.secret:
        messages_to_send.extend(create_new_secret(faction.id, situation.name))
        situation.delete()
    else:
        match situation.type:
            case "war":
                messages_to_send.extend(create_new_war(faction.id, situation.name))
                situation.delete()
            case "senator":
                messages_to_send.extend(create_new_family(faction.id, situation.name))
                situation.delete()
            case "leader":
                messages_to_send.extend(
                    create_new_enemy_leader(faction.id, situation.name)
                )
                situation.delete()

    # If no more situations remain then rename the current phase to "Final Forum Phase",
    # triggering the end of the game once the phase is completed
    if Situation.objects.filter(game=faction.game).count() == 0:
        current_phase = get_phase(faction.game.id)
        current_phase.name = "Final Forum"
        current_phase.save()
        messages_to_send.append(
            create_websocket_message("phase", PhaseSerializer(current_phase).data)
        )
        latest_step = get_step(faction.game.id)
        new_action_log_index = (
            ActionLog.objects.filter(step__phase__turn__game=faction.game.id)
            .order_by("-index")[0]
            .index
            + 1
        )
        era_ends_action_log = ActionLog(
            index=new_action_log_index,
            step=latest_step,
            type="era_ends",
        )
        era_ends_action_log.save()
        messages_to_send.append(
            create_websocket_message(
                "action_log", ActionLogSerializer(era_ends_action_log).data
            )
        )

    step, message = create_step_and_message(faction.game.id)
    messages_to_send.append(message)

    messages_to_send.append(generate_select_faction_leader_action(faction, step))
    return messages_to_send
