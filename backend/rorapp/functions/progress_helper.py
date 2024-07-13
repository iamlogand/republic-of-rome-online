from rorapp.functions.websocket_message_helper import create_websocket_message
from rorapp.models import Phase, Step, Turn
from rorapp.serializers import PhaseSerializer, StepSerializer


def get_step(game_id: int, index: int = -1) -> Step:
    if index < 0:
        step = Step.objects.filter(phase__turn__game=game_id).order_by("-index")[
            -index - 1
        ]
    else:
        step = Step.objects.filter(phase__turn__game=game_id).order_by("index")[index]
    if not isinstance(step, Step):
        raise ValueError("No step found")
    return step


def get_turn(game_id: int, index: int = -1) -> Turn:
    if index < 0:
        turn = Turn.objects.filter(game=game_id).order_by("-index")[-index - 1]
    else:
        turn = Turn.objects.filter(game=game_id).order_by("index")[index]
    if not isinstance(turn, Turn):
        raise ValueError("No turn found")
    return turn


def get_phase(game_id: int, index: int = -1, turn_index: int = -1) -> Phase:
    turn = get_turn(game_id, turn_index)
    if not isinstance(turn, Turn):
        raise ValueError("No turn found")
    if index < 0:
        phase = Phase.objects.filter(turn=turn).order_by("-index")[-index - 1]
    else:
        phase = Phase.objects.filter(turn=turn).order_by("index")[index]
    return phase


def create_step(game_id: int) -> Step:
    """
    Creates a new step in the current phase of the game.
    """

    last_step = get_step(game_id)
    index = last_step.index + 1 if isinstance(last_step, Step) else 0
    latest_phase = get_phase(game_id)
    step = Step(index=index, phase=latest_phase)
    step.save()
    return step


def create_step_and_message(game_id: int) -> tuple[Step, dict]:
    """
    Creates a new step in the current phase of the game and a websocket message for the new step.
    """

    step = create_step(game_id)
    message_to_send = create_websocket_message("step", StepSerializer(step).data)
    return step, message_to_send


def create_phase(game_id: int, name: str) -> Phase:
    """
    Creates a new phase in the current turn of the game.
    """

    last_turn = Turn.objects.filter(game=game_id).order_by("index").last()
    assert isinstance(last_turn, Turn)
    try:
        index = get_phase(game_id).index
    except IndexError:
        index = 0
    phase = Phase(name=name, index=index + 1, turn=last_turn)
    phase.save()
    return phase


def create_phase_and_message(game_id: int, name: str) -> tuple[Phase, dict]:
    """
    Creates a new phase in the current turn of the game and a websocket message for the new phase.
    """

    phase = create_phase(game_id, name)
    message_to_send = create_websocket_message("phase", PhaseSerializer(phase).data)
    return phase, message_to_send
