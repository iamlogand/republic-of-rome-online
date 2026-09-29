import re
from enum import Enum
from typing import Iterable, List

from django.db.models import Max

from rorapp.classes.concession import Concession
from rorapp.helpers.fail_revolt import fail_revolt
from rorapp.helpers.game_data import get_senator_codes, load_senators
from rorapp.helpers.hrao import rank_key, set_hrao
from rorapp.helpers.text import format_list, to_sentence_case
from rorapp.models import Campaign, Fleet, Game, Legion, Log, Senator, War


class CauseOfDeath(Enum):
    NATURAL = "natural"
    BATTLE = "battle"
    EPIDEMIC = "epidemic"
    MOB = "mob"
    ASSASSINATION = "assassination"
    EXECUTION = "execution"
    ACCOMPLICE = "accomplice"
    CAPTIVITY = "captivity"


def leave_campaigns(senator: Senator) -> None:
    game = senator.game

    # Remove senator from campaign
    campaigns = list(game.campaigns.filter(commander=senator))
    if bool(campaigns):
        campaign: Campaign = campaigns[0]
        uncommanded_campaigns = game.campaigns.filter(
            war=campaign.war, commander=None
        ).exclude(id=campaign.id)

        # Merge uncommanded campaigns on same war
        if len(uncommanded_campaigns) == 1:
            if campaign.legions:
                legions = campaign.legions.all()
                for legion in legions:
                    legion.campaign = uncommanded_campaigns[0]
                Legion.objects.bulk_update(legions, ["campaign"])
            if campaign.fleets:
                fleets = campaign.fleets.all()
                for fleet in fleets:
                    fleet.campaign = uncommanded_campaigns[0]
                Fleet.objects.bulk_update(fleets, ["campaign"])
            campaign.delete()
        else:
            campaign.commander = None
            campaign.save()

    # Remove senator as Master of Horse from campaign
    master_of_horse_campaigns = list(game.campaigns.filter(master_of_horse=senator))
    if bool(master_of_horse_campaigns):
        master_of_horse_campaign: Campaign = master_of_horse_campaigns[0]
        master_of_horse_campaign.master_of_horse = None
        master_of_horse_campaign.save()


def kill_senators(
    senators: Iterable[Senator],
    cause_of_death: CauseOfDeath = CauseOfDeath.NATURAL,
) -> None:
    # Kill the lowest ranking victims first, so that the HRAO's successor is
    # only chosen once every other victim is already dead (1.09.11)
    for senator in sorted(senators, key=rank_key, reverse=True):
        senator.refresh_from_db()
        if senator.alive:
            kill_senator(senator, cause_of_death)


def next_curia_position(game: Game) -> int:
    highest = Senator.objects.filter(game=game, curia_position__isnull=False).aggregate(
        highest=Max("curia_position")
    )["highest"]
    return (highest or 0) + 1


def kill_senator(
    senator: Senator,
    cause_of_death: CauseOfDeath = CauseOfDeath.NATURAL,
    leave_heir: bool = True,
):
    # An earlier death may have made this senator the HRAO (1.09.11)
    senator.refresh_from_db()
    game: Game = senator.game
    display_name = senator.display_name
    display_name_with_faction = senator.display_name_with_faction
    was_hrao = senator.has_title(Senator.Title.HRAO)
    was_presiding_magistrate = senator.has_title(Senator.Title.PRESIDING_MAGISTRATE)
    revolt = (
        War.objects.filter(primary_rebel=senator)
        .exclude(status=War.Status.DEFEATED)
        .first()
    )

    released_concessions: List[Concession] = []
    campaigns: List[Campaign] = []

    senators_dict = load_senators()
    family_code = get_senator_codes(senator.code)[0]
    senator_data = next(
        (v for v in senators_dict.values() if v["code"] == int(family_code)),
        None,
    )

    if senator_data:
        senator.military = senator_data["military"]
        senator.oratory = senator_data["oratory"]
        senator.loyalty = senator_data["loyalty"]
        senator.influence = senator_data["influence"]

    senator.code = family_code
    senator.statesman_name = None
    senator.clear_status_items()
    senator.location = "Rome"
    senator.popularity = 0
    senator.knights = 0
    senator.captor = None
    senator.rebel = False
    senator.talents = 0
    senator.clear_corrupt_concessions()

    for concession in senator.get_concessions():
        game.add_concession(concession)
        released_concessions.append(concession)
    senator.clear_concessions()
    if released_concessions:
        game.save()

    was_faction_leader = False
    # A punished faction leader has their family card sent to the bottom of the curia(1.09.74)
    if senator.has_title(Senator.Title.FACTION_LEADER) and leave_heir:
        senator.clear_titles()
        senator.add_title(Senator.Title.FACTION_LEADER)
        senator.generation += 1
        was_faction_leader = True
    else:
        senator.clear_titles()
        senator.alive = False
        senator.faction = None
        if senator.family:
            senator.curia_position = next_curia_position(game)

    # Release the allegiance of any veteran legions loyal to the senator
    Legion.objects.filter(game=game, allegiance=senator).update(allegiance=None)

    leave_campaigns(senator)

    deleted = False
    if not senator.family:
        senator.delete()
        deleted = True
    else:
        senator.save()

    # Log senator death
    log_text = to_sentence_case(display_name_with_faction)

    if cause_of_death == CauseOfDeath.BATTLE:
        log_text += " was killed in battle."
    elif cause_of_death == CauseOfDeath.EPIDEMIC:
        log_text += " died in the epidemic."
    elif cause_of_death == CauseOfDeath.MOB:
        log_text += " was killed by the mob."
    elif cause_of_death == CauseOfDeath.ASSASSINATION:
        log_text += " was assassinated."
    elif cause_of_death == CauseOfDeath.EXECUTION:
        log_text += " was executed for attempted murder."
    elif cause_of_death == CauseOfDeath.ACCOMPLICE:
        log_text += " was implicated in the assassination plot and executed."
    elif cause_of_death == CauseOfDeath.CAPTIVITY:
        log_text += " was killed in captivity."
    else:
        log_text += " died of natural causes."

    if was_faction_leader and not deleted:
        log_text += f" His heir {senator.display_name} replaced him as faction leader."

    Log.create_object(game.id, log_text)

    # Log released concessions
    if released_concessions:
        count = len(released_concessions)
        concession_names = [concession.value for concession in released_concessions]
        concession_log = f"The death of {display_name} has made the"
        if count == 1:
            concession_log += f" {concession_names[0]} concession"
        else:
            concession_list = format_list(concession_names)
            concession_log += f" {concession_list} concessions"
        concession_log += " available."
        Log.create_object(game.id, text=concession_log)

    # Handle HRAO death by setting new HRAO
    if was_hrao:
        set_hrao(game.id, log_presiding_magistrate=game.phase == Game.Phase.SENATE)

    # Handle PM death by transferring title to new HRAO
    if was_presiding_magistrate and game.phase == Game.Phase.SENATE:
        from rorapp.helpers.transfer_presiding_magistrate import (
            transfer_presiding_magistrate_to_hrao,
        )

        transfer_presiding_magistrate_to_hrao(game.id)

    # A revolt fails when its Primary Rebel dies, however he dies (1.11.372)
    if revolt:
        fail_revolt(revolt, display_name)
