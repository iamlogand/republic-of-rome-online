from rorapp.functions.websocket_message_helper import create_websocket_message
from rorapp.models import Phase, Step
from rorapp.serializers.step import StepSerializer


def get_latest_step(game_id: int, reverse_index: int = 0) -> Step:
    if reverse_index == 0:
        step = Step.objects.filter(phase__turn__game=game_id).order_by("-index").first()
        assert isinstance(step, Step)
        return step
    else:
        step = Step.objects.filter(phase__turn__game=game_id).order_by("-index")[
            reverse_index
        ]
        assert isinstance(step, Step)
        return step


def get_latest_phase(game_id: int, reverse_index: int = 0) -> Phase:
    latest_step = get_latest_step(game_id)
    if reverse_index == 0:
        phase = (
            Phase.objects.filter(turn=latest_step.phase.turn).order_by("-index").first()
        )
        assert isinstance(phase, Phase)
        return phase
    else:
        phase = Phase.objects.filter(turn=latest_step.phase.turn).order_by("-index")[
            reverse_index
        ]
        assert isinstance(phase, Phase)
        return phase


def create_step(game_id: int) -> Step:
    """
    Creates a new step in the current phase of the game.
    """

    latest_step = get_latest_step(game_id)
    latest_phase = get_latest_phase(game_id)
    new_step = Step(index=latest_step.index + 1, phase=latest_phase)
    new_step.save()
    return new_step


def create_step_and_message(game_id: int) -> tuple[Step, dict]:
    """
    Creates a new step in the current phase of the game and a websocket message for the new step.
    """

    new_step = create_step(game_id)
    message_to_send = create_websocket_message("step", StepSerializer(new_step).data)
    return new_step, message_to_send
