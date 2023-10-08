import os
import json
from django.conf import settings
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rorapp.functions.draw_mortality_chits import draw_mortality_chits
from rorapp.functions.rank_senators_and_factions import rank_senators_and_factions
from rorapp.functions.send_websocket_messages import send_websocket_messages
from rorapp.functions.ws_message_create import ws_message_create
from rorapp.functions.ws_message_destroy import ws_message_destroy
from rorapp.functions.ws_message_update import ws_message_update
from rorapp.models import Faction, PotentialAction, CompletedAction, Step, Senator, Title, Phase, Turn, ActionLog, SenatorActionLog
from rorapp.serializers import ActionLogSerializer, PotentialActionSerializer, StepSerializer, TitleSerializer, PhaseSerializer, TurnSerializer, SenatorSerializer, SenatorActionLogSerializer


def face_mortality(game, faction, potential_action, step):
    '''
    Ready up for facing mortality.
    
    :return: a response with a message and a status code
    :rtype: rest_framework.response.Response
    '''
    
    messages_to_send = []
    
    # Delete the potential action
    potential_action_id = potential_action.id
    potential_action.delete()
    
    # Create a new completed action
    completed_action = CompletedAction(step=step, faction=faction, type="face_mortality", required=True)
    completed_action.save()
    
    messages_to_send.append(ws_message_destroy("potential_action", potential_action_id))
    
    # If this the last faction to face mortality, perform mortality and proceed to the next step
    if PotentialAction.objects.filter(step__id=step.id).count() == 0:
        
        # Read senator presets
        senator_json_path = os.path.join(settings.BASE_DIR, 'rorapp', 'presets', 'senator.json')
        with open(senator_json_path, 'r') as file:
            senators_dict = json.load(file)
        
        # Perform mortality
        drawn_codes = draw_mortality_chits(1)
        killed_senator_count = 0
        for code in drawn_codes:
            senators = Senator.objects.filter(game=game, death_step__isnull=True, code=code)
            if senators.exists():
                senator = senators.first()
                senators_former_faction = senator.faction
                
                # Kill the senator
                senator.death_step = step
                senator.faction = None
                senator.save()
                killed_senator_count += 1
                
                messages_to_send.append(ws_message_update("senator", SenatorSerializer(senator).data))
                
                # End associated titles
                titles_to_end = Title.objects.filter(senator__id=senator.id, end_step__isnull=True)
                ended_major_office = None
                heir = None
                if titles_to_end.exists():
                    for title in titles_to_end:
                        title.end_step = step
                        title.save()
                        
                        if title.major_office == True:
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
                                military=senators_dict[senator.name]['military'],
                                oratory=senators_dict[senator.name]['oratory'],
                                loyalty=senators_dict[senator.name]['loyalty'],
                                influence=senators_dict[senator.name]['influence'],
                            )
                            heir.save()
                            
                            messages_to_send.append(ws_message_create("senator", SenatorSerializer(heir).data))

                            # Create a new title for the heir
                            new_faction_leader = Title(name="Faction Leader", senator=heir, start_step=step)
                            new_faction_leader.save()
                            
                            messages_to_send.append(ws_message_create("title", TitleSerializer(new_faction_leader).data))
                
                # Create an action_log and action_log relations     
                new_action_log_index = ActionLog.objects.filter(step__phase__turn__game=game).order_by('-index')[0].index + 1
                action_log = ActionLog(
                    index=new_action_log_index,
                    step=step,
                    type="face_mortality",
                    faction=senators_former_faction,
                    data={"senator": senator.id, "major_office": ended_major_office, "heir_senator": heir.id if heir else None}
                )
                action_log.save()
                messages_to_send.append(ws_message_create("action_log", ActionLogSerializer(action_log).data))
                
                senator_action_log = SenatorActionLog(senator=senator, action_log=action_log)
                senator_action_log.save()
                messages_to_send.append(ws_message_create("senator_action_log", SenatorActionLogSerializer(senator_action_log).data))
                
                if heir:
                    heir_senator_action_log = SenatorActionLog(senator=heir, action_log=action_log)
                    heir_senator_action_log.save()
                    messages_to_send.append(ws_message_create("senator_action_log", SenatorActionLogSerializer(heir_senator_action_log).data))
            
        # If nobody dies, issue a notification to say so
        if killed_senator_count == 0:
            new_action_log_index = ActionLog.objects.filter(step__phase__turn__game=game).order_by('-index')[0].index + 1
            action_log = ActionLog(
                index=new_action_log_index,
                step=step,
                type="face_mortality"
            )
            action_log.save()
            messages_to_send.append(ws_message_create("action_log", ActionLogSerializer(action_log).data))
                
        # Update senator ranks
        messages_to_send.extend(rank_senators_and_factions(game.id))
                
        # Proceed to the forum phase
        new_phase = Phase(name="Forum", index=1, turn=step.phase.turn)
        new_phase.save()
        messages_to_send.append(ws_message_create("phase", PhaseSerializer(new_phase).data))
        new_step = Step(index=step.index + 1, phase=new_phase)
        new_step.save()
        messages_to_send.append(ws_message_create("step", StepSerializer(new_step).data))
        
        # Create potential actions for the forum phase
        first_faction = Faction.objects.filter(game__id=game.id).order_by('rank').first()
        action = PotentialAction(
            step=new_step, faction=first_faction, type="select_faction_leader",
            required=True, parameters=None
        )
        action.save()
        
        messages_to_send.append(ws_message_create("potential_action", PotentialActionSerializer(action).data))
        
    send_websocket_messages(game.id, messages_to_send)
    return Response({"message": f"Ready for mortality"}, status=200)
