from rest_framework.response import Response
from typing import List, Optional
from rorapp.functions.progress_helper import get_latest_phase, get_latest_step
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
    Faction,
    Phase,
    Senator,
    Situation,
    Step,
)
from rorapp.serializers import ActionSerializer, StepSerializer


def get_next_faction_in_forum_phase(
    last_faction: Faction | None = None,
) -> Optional[Faction]:
    """
    Find the faction that should take the next initiative in the forum phase.

    Args:
        last_faction (Faction): The faction that took the last initiative.

    Returns:
        Faction | None: The faction that should take the next initiative, if there is one.
    """

    factions = Faction.objects.filter(game__id=last_faction.game.id).order_by("rank")
    if last_faction is None:
        return factions.first()
    last_faction_index = list(factions).index(last_faction)
    next_faction_index = last_faction_index + 1
    if next_faction_index >= len(factions):
        return None
    return factions[next_faction_index]


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


def generate_initiate_situation_action(faction: Faction) -> List[dict]:
    messages_to_send = []

    # Create new step
    latest_step = get_latest_step(faction.game.id)
    # Need to get latest phase because the latest step might not be from the current forum phase
    latest_phase = get_latest_phase(faction.game.id)
    new_step = Step(index=latest_step.index + 1, phase=latest_phase)
    new_step.save()
    messages_to_send.append(
        create_websocket_message("step", StepSerializer(new_step).data)
    )

    # Create new action
    action = Action(
        step=new_step,
        faction=faction,
        type="initiate_situation",
        required=True,
    )
    action.save()
    messages_to_send.append(
        create_websocket_message("action", ActionSerializer(action).data)
    )
    return messages_to_send


def initiate_situation(action_id: int) -> dict:
    """
    Initiate a random situation.

    This function is called when a player initiates a situation during the forum phase.

    Args:
        action_id (int): The action ID.

    Returns:
        dict: The response with a message and a status code.
    """
    messages_to_send = []

    # Mark the action as complete
    action = Action.objects.get(id=action_id)
    action.completed = True
    action.save()
    messages_to_send.append(destroy_websocket_message("action", action_id))

    # Get situation
    situation = (
        Situation.objects.filter(game=action.step.phase.turn.game)
        .order_by("index")
        .last()
    )
    # TODO throw an exception if there are no situations, and add an "era ends" situation so that shouldn't even happen.
    if situation is not None:
        if situation.secret:
            messages_to_send.extend(
                create_new_secret(action.faction.id, situation.name)
            )
            situation.delete()
        else:
            match situation.type:
                case "war":
                    messages_to_send.extend(
                        create_new_war(action.faction.id, situation.name)
                    )
                    situation.delete()
                case "senator":
                    messages_to_send.extend(
                        create_new_family(action.faction.id, situation.name)
                    )
                    situation.delete()
                case "leader":
                    messages_to_send.extend(
                        create_new_enemy_leader(action.faction.id, situation.name)
                    )
                    situation.delete()

    # Create new step
    new_step = Step(index=action.step.index + 1, phase=action.step.phase)
    new_step.save()
    messages_to_send.append(
        create_websocket_message("step", StepSerializer(new_step).data)
    )

    messages_to_send.append(
        generate_select_faction_leader_action(action.faction, new_step)
    )
    return Response({"message": "Situation initiated"}, status=200), messages_to_send
