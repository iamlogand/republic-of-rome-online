from rorapp.models import Phase, Step, Turn


def get_latest_step(game_id: int, reverse_index: int = 0) -> Step:
    if reverse_index == 0:
        return Step.objects.filter(phase__turn__game=game_id).order_by("-index").first()
    else:
        return Step.objects.filter(phase__turn__game=game_id).order_by("-index")[
            reverse_index
        ]


def get_latest_phase(game_id: int, reverse_index: int = 0) -> Phase:
    if reverse_index == 0:
        return Phase.objects.filter(turn__game=game_id).order_by("-index").first()
    else:
        return Phase.objects.filter(turn__game=game_id).order_by("-index")[
            reverse_index
        ]


def get_latest_turn(game_id: int, reverse_index: int = 0) -> Turn:
    if reverse_index == 0:
        return Turn.objects.filter(game=game_id).order_by("-index").first()
    else:
        return Turn.objects.filter(game=game_id).order_by("-index")[reverse_index]
