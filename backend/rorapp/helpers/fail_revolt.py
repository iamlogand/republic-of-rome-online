from rorapp.helpers.hrao import set_hrao
from rorapp.helpers.lay_down_command import lay_down_command
from rorapp.models import Campaign, Log, War


def fail_revolt(revolt: War, rebel_name: str) -> None:
    """Return the revolt's forces to the Senate and its opponents to Rome (1.11.372)."""

    revolt.status = War.Status.DEFEATED
    revolt.unprosecuted = False
    # The rebel's own row may already be gone, so leave primary_rebel alone
    revolt.save(update_fields=["status", "unprosecuted"])
    Log.create_object(
        revolt.game_id, f"The revolt ended with the death of {rebel_name}."
    )

    campaigns = list(Campaign.objects.filter(war=revolt).order_by("id"))
    for campaign in campaigns:
        lay_down_command(campaign)
    # Senators returning to Rome may outrank the HRAO (1.09.11)
    if campaigns:
        set_hrao(revolt.game_id)
