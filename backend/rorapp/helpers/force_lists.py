from typing import List, Union

from rorapp.models.fleet import Fleet
from rorapp.models.legion import Legion


# Accepts an array of either Legions or Fleets
def force_list_to_string(items: List[Union[Legion, Fleet]]):

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
