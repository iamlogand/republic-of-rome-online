import re
from typing import List, Sequence, Tuple, Type, Union, cast

from rorapp.helpers.text import format_list
from rorapp.models.fleet import Fleet
from rorapp.models.legion import Legion

LEGION_LIST_PATTERN = r"(?P<count>\d+)\s+legions?\s*\((?P<names>[^)]+)\)"
FLEET_LIST_PATTERN = r"(?P<count>\d+)\s+fleets?\s*\((?P<names>[^)]+)\)"


# Accepts an array of either Legions or Fleets and returns a string
def unit_list_to_string_inner(items: Sequence[Union[Legion, Fleet]]) -> str:

    groups = [[items[0]]]
    for item in items[1:]:
        if item.number == groups[-1][-1].number + 1:
            groups[-1].append(item)
        else:
            groups.append([item])

    group_names = []
    for group in groups:
        if len(group) == 1:
            group_names.append(group[0].name)
        elif len(group) == 2:
            group_names.append(group[0].name)
            group_names.append(group[1].name)
        else:
            group_names.append(f"{group[0].name}–{group[-1].name}")

    return format_list(group_names)


# Accepts an array of Legions and an array of Fleets and returns a string
def unit_list_to_string(legions: List[Legion], fleets: List[Fleet]) -> str:
    text = ""
    if legions:
        legion_names = unit_list_to_string_inner(legions)
        text += f"{len(legions)} {'legions' if len(legions) > 1 else 'legion'} ({legion_names})"
    if legions and fleets:
        text += " and "
    if fleets:
        fleet_names = unit_list_to_string_inner(fleets)
        text += (
            f"{len(fleets)} {'fleets' if len(fleets) > 1 else 'fleet'} ({fleet_names})"
        )
    return text


# Accepts a string and returns an array of either Legions or Fleets
def string_to_unit_list(
    s: str, game_id: int, type: Type[Union[Legion, Fleet]]
) -> List[Union[Legion, Fleet]]:
    groups = s.replace(" and ", ", ").split(", ")
    items = []

    potential_items: List[Union[Legion, Fleet]] = []
    if type == Legion:
        potential_items = list(Legion.objects.filter(game=game_id))
    else:
        potential_items = list(Fleet.objects.filter(game=game_id))

    for group in groups:
        if "–" in group:
            start_name, end_name = group.split("–")
            start_item = next(
                (i for i in potential_items if i.name == start_name), None
            )
            end_item = next((i for i in potential_items if i.name == end_name), None)

            if start_item is None:
                raise ValueError(
                    f"Could not find item: '{start_name}' in available {type.__name__}s"
                )

            if end_item is None:
                raise ValueError(
                    f"Could not find item: '{end_item}' in available {type.__name__}s"
                )

            start_number = start_item.number
            end_number = end_item.number
            for num in range(start_number, end_number + 1):
                item = next((i for i in potential_items if i.number == num), None)
                if item is None:
                    raise ValueError(
                        f"Could not find item with number {num} in available {type.__name__}s"
                    )

                items.append(item)
        else:
            item = next((i for i in potential_items if i.name == group), None)
            if item is None:
                raise ValueError(
                    f"Could not find item: '{group}' in available {type.__name__}s"
                )

            items.append(item)

    return items


# Accepts a string containing unit lists produced by unit_list_to_string
# (e.g. "2 legions (I, II) and 1 fleet (III)") and returns the Legions and Fleets
def string_to_unit_lists(s: str, game_id: int) -> Tuple[List[Legion], List[Fleet]]:
    legion_match = re.search(LEGION_LIST_PATTERN, s)
    fleet_match = re.search(FLEET_LIST_PATTERN, s)

    legions: List[Legion] = []
    if legion_match:
        legions = cast(
            List[Legion],
            string_to_unit_list(legion_match.group("names"), game_id, Legion),
        )

    fleets: List[Fleet] = []
    if fleet_match:
        fleets = cast(
            List[Fleet],
            string_to_unit_list(fleet_match.group("names"), game_id, Fleet),
        )

    if legion_match and len(legions) != int(legion_match.group("count")):
        raise ValueError("Legion count didn't match legion names")
    if fleet_match and len(fleets) != int(fleet_match.group("count")):
        raise ValueError("Fleet count didn't match fleet names")

    return legions, fleets
