from rorapp.helpers.hrao import set_hrao
from rorapp.helpers.transfer_presiding_magistrate import (
    transfer_presiding_magistrate_to_hrao,
)
from rorapp.models import Province, Senator


def assign_governor(province: Province, senator: Senator) -> None:
    was_hrao = senator.has_title(Senator.Title.HRAO)
    was_presiding_magistrate = senator.has_title(Senator.Title.PRESIDING_MAGISTRATE)

    province.governor = senator
    province.save()

    # An elected Governor leaves Rome immediately without participating in any
    # remaining Senate votes (1.09.5)
    senator.location = province.name
    senator.remove_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    senator.remove_title(Senator.Title.HRAO)
    senator.remove_title(Senator.Title.PRESIDING_MAGISTRATE)
    senator.save()

    if was_hrao:
        set_hrao(province.game_id)
    if was_presiding_magistrate:
        transfer_presiding_magistrate_to_hrao(province.game_id)


def clear_governorship(province: Province) -> None:
    province.governor = None
    province.save()
