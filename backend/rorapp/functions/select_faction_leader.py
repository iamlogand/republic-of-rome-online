from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rorapp.models import Faction, PotentialAction, CompletedAction, Step, Senator, Title, Phase
from rorapp.models.notification import Notification
from rorapp.serializers import NotificationSerializer, PotentialActionSerializer, StepSerializer, TitleSerializer

def select_faction_leader(game, faction, potential_action, step, data):
    '''
    Select a faction leader.
    
    This function is called when a player selects a faction leader during the faction phase.
    Can handle scenarios where there is or is not a faction leader already assigned.

    :param game: the game
    :param faction: the faction selecting the leader
    :param potential_action: the potential action
    :param step: the step
    :param data: the data, expects a `leader_id` for the senator selected as the faction leader
    '''

    # Try to get the senator
    try:
        senator = Senator.objects.filter(faction=faction).get(id=data.get("leader_id"))
    except Senator.DoesNotExist:
        return Response({"message": "Selected faction leader (senator) was not found"}, status=404)
    
    # Check if the senator is already a faction leader
    previous_titles = Title.objects.filter(senator__faction=faction).filter(name="Faction Leader").filter(end_step__isnull=True)
    previous_title = None if previous_titles.count() == 0 else previous_titles.first()
    
    messages_to_send = []
    
    previous_senator_id = None if previous_title is None else previous_title.senator.id
    
    # End the previous faction leader title if it's a different senator
    if previous_title is not None and previous_title.senator != senator:
        previous_title.end_step = step
        previous_title.save()
        
        messages_to_send.append({
            "operation": "destroy",
            "instance": {
                "class": "title",
                "id": previous_title.id
            }
        })
        
    # Create a new faction leader title if the senator doesn't have one
    if previous_title is None or previous_title.senator != senator:
        title = Title(name="Faction Leader", senator=senator, start_step=step)
        title.save()
        
        messages_to_send.append({
            "operation": "create",
            "instance": {
                "class": "title",
                "data": TitleSerializer(title).data
            }
        })
        
        all_notifications = Notification.objects.filter(step__phase__turn__game=game).order_by('-index')
        new_notification_index = 0
        if all_notifications.count() > 0:
            latest_notification = all_notifications[0]
            new_notification_index = latest_notification.index + 1
        notification = Notification(
            index=new_notification_index,
            step=step,
            type="select_faction_leader",
            faction=faction,
            data={"senator": senator.id, "previous_senator": previous_senator_id}
        )
        notification.save()
        
        messages_to_send.append({
            "operation": "create",
            "instance": {
                "class": "notification",
                "data": NotificationSerializer(notification).data
            }
        })

    # Delete the potential action
    potential_action_id = potential_action.id
    potential_action.delete()
    
    # Create a new completed action
    completed_action = CompletedAction(step=step, faction=faction, type="select_faction_leader", required=True)
    completed_action.save()
    
    messages_to_send.append({
        "operation": "destroy",
        "instance": {
            "class": "potential_action",
            "id": potential_action_id
        }
    })
    
    # If this is the final faction leader to be selected, proceed to the next step
    if PotentialAction.objects.filter(step__id=step.id).count() == 0:
        phase = Phase.objects.get(id=step.phase.id)
        step = Step(index=step.index + 1, phase=phase)
        step.save()
        
        messages_to_send.append({
            "operation": "create",
            "instance": {
                "class": "step",
                "data": StepSerializer(step).data
            }
        })
        
        # Create potential actions for another round of faction leader selection.
        # This is a temporary way to keep the game 'progressing' in a loop.
        # TODO: change this so it progresses to the mortality phase instead.
        factions = Faction.objects.filter(game__id=game.id)
        for faction in factions:
            action = PotentialAction(
                step=step, faction=faction, type="select_faction_leader",
                required=True, parameters=None
            )
            action.save()
            
            messages_to_send.append({
                "operation": "create",
                "instance": {
                    "class": "potential_action",
                    "data": PotentialActionSerializer(action).data
                }
            })
            
    # Send WebSocket messages
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"game_{game.id}",
        {
            "type": "game_update",
            "messages": messages_to_send
        }
    )
    
    return Response({"message": f"Faction leader selected"}, status=200)
