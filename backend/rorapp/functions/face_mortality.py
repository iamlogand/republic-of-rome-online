import os
import json
from django.conf import settings
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rorapp.functions.draw_mortality_chits import draw_mortality_chits
from rorapp.functions.rank_senators_and_factions import rank_senators_and_factions
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
    
    messages_to_send.append({
        "operation": "destroy",
        "instance": {
            "class": "potential_action",
            "id": potential_action_id
        }
    })
    
    # If this the last faction to face mortality, perform mortality and proceed to the next step
    if PotentialAction.objects.filter(step__id=step.id).count() == 0:
        
        # Read senator presets
        senator_json_path = os.path.join(settings.BASE_DIR, 'rorapp', 'presets', 'senator.json')
        with open(senator_json_path, 'r') as file:
            senators_dict = json.load(file)
        
        # Perform mortality
        drawn_codes = draw_mortality_chits(1)
        for code in drawn_codes:
            senators = Senator.objects.filter(game=game, alive=True, code=code)
            if senators.exists():
                senator = senators.first()
                senators_former_faction = senator.faction
                
                # Kill the senator
                senator.alive = False
                senator.faction = None
                senator.save()
                
                messages_to_send.append({
                    "operation": "update",
                    "instance": {
                        "class": "senator",
                        "data": SenatorSerializer(senator).data
                    }
                })
                
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
                        
                        messages_to_send.append({
                            "operation": "destroy",
                            "instance": {
                                "class": "title",
                                "id": title.id
                            }
                        })
                        
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
                            heir_id = heir.id
                            
                            messages_to_send.append({
                                "operation": "create",
                                "instance": {
                                    "class": "senator",
                                    "data": SenatorSerializer(heir).data
                                }
                            })

                            # Create a new title for the heir
                            new_faction_leader = Title(name="Faction Leader", senator=heir, start_step=step)
                            new_faction_leader.save()
                            
                            messages_to_send.append({
                                "operation": "create",
                                "instance": {
                                    "class": "title",
                                    "data": TitleSerializer(new_faction_leader).data
                                }
                            })
                
                # Create a action_log and action_log relations     
                new_action_log_index = ActionLog.objects.filter(step__phase__turn__game=game).order_by('-index')[0].index + 1
                action_log = ActionLog(
                    index=new_action_log_index,
                    step=step,
                    type="face_mortality",
                    faction=senators_former_faction,
                    data={"senator": senator.id, "major_office": ended_major_office, "heir_senator": heir.id if heir else None}
                )
                action_log.save()
                messages_to_send.append({
                    "operation": "create",
                    "instance": {
                        "class": "action_log",
                        "data": ActionLogSerializer(action_log).data
                    }
                })
                
                senator_action_log = SenatorActionLog(senator=senator, action_log=action_log)
                senator_action_log.save()
                messages_to_send.append({
                    "operation": "create",
                    "instance": {
                        "class": "senator_action_log",
                        "data": SenatorActionLogSerializer(senator_action_log).data
                    }
                })
                
                if heir:
                    heir_senator_action_log = SenatorActionLog(senator=heir, action_log=action_log)
                    heir_senator_action_log.save()
                    messages_to_send.append({
                        "operation": "create",
                        "instance": {
                            "class": "senator_action_log",
                            "data": SenatorActionLogSerializer(heir_senator_action_log).data
                        }
                    })
                
        # Update senator ranks
        messages_to_send.extend(rank_senators_and_factions(game.id))
                
        # Proceed to the next turn
        turn = Turn.objects.get(id=step.phase.turn.id)
        new_turn = Turn(index=turn.index + 1, game=game)
        new_turn.save()

        new_phase = Phase(name="Mortality", index=1, turn=new_turn)
        new_phase.save()
        
        new_step = Step(index=step.index + 1, phase=new_phase)
        new_step.save()

        messages_to_send.append({
            "operation": "create",
            "instance": {
                "class": "turn",
                "data": TurnSerializer(new_turn).data
            }
        })
        messages_to_send.append({
            "operation": "create",
            "instance": {
                "class": "phase",
                "data": PhaseSerializer(new_phase).data
            }
        })
        messages_to_send.append({
            "operation": "create",
            "instance": {
                "class": "step",
                "data": StepSerializer(new_step).data
            }
        })
        
        # Create potential actions for the next mortality phase
        factions = Faction.objects.filter(game__id=game.id)
        for faction in factions:
            action = PotentialAction(
                step=new_step, faction=faction, type="face_mortality",
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
    
    return Response({"message": f"Ready for mortality"}, status=200)
