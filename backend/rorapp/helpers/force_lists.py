from typing import Dict, List, Type, Union

from rorapp.models.fleet import Fleet
from rorapp.models.legion import Legion


# Accepts an array of either Legions or Fleets and returns a string
def force_list_to_string(items: List[Union[Legion, Fleet]]) -> str:

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
            group_names.append(f"{group[0].name}-{group[-1].name}")

    return " and ".join(", ".join(group_names).rsplit(", ", 1))


# Accepts a string and returns an array of either Legions or Fleets
def string_to_force_list(
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
        if "-" in group:
            start_name, end_name = group.split("-")
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
