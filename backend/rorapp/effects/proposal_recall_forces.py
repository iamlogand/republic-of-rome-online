import re
from typing import cast, List
from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.clear_proposal_and_votes import clear_proposal_and_votes
from rorapp.helpers.unit_lists import string_to_unit_list, unit_list_to_string
from rorapp.models import Campaign, Fleet, Game, Legion, Log, Senator, War


class ProposalRecallForcesEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.OTHER_BUSINESS
            and not (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
            and all(f.has_status_item(FactionStatusItem.DONE) for f in game_state.factions)
            and game_state.game.current_proposal.startswith("Recall ")
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        game = Game.objects.get(id=game_id)
        if not game.current_proposal:
            return False

        if game.votes_yea > game.votes_nay:

            # Proposal passed
            Log.create_object(game.id, f"Motion passed: {game.current_proposal}.")

            senators = Senator.objects.filter(game=game, alive=True)
            commander_name_and_more = game.current_proposal[len("Recall ") :]
            commander = next(
                (
                    s
                    for s in senators
                    if commander_name_and_more.startswith(s.display_name)
                ),
                None,
            )
            campaigns = Campaign.objects.filter(game=game)
            campaign_name_and_more = game.current_proposal[
                : game.current_proposal.find(" in the")
            ]
            campaign = next(
                (
                    c
                    for c in campaigns
                    if campaign_name_and_more.endswith(c.display_name)
                ),
                None,
            )
            wars = War.objects.filter(game=game)
            war = next(
                (w for w in wars if game.current_proposal.endswith(w.name)), None
            )
            if war is None:
                raise ValueError("Invalid war")

            # Validate campaign wasn't recently deployed or reinforced
            if campaign and (
                campaign.recently_deployed or campaign.recently_reinforced
            ):
                Log.create_object(
                    game_id,
                    f"Cannot recall forces from a campaign that was recently deployed or reinforced.",
                )
                game.save()
                clear_proposal_and_votes(game_id)
                return True

            legion_pattern = (
                r"(?P<legion_count>\d+)\s+legions?\s*\((?P<legions>[^)]+)\)"
            )
            fleet_pattern = r"(?P<fleet_count>\d+)\s+fleets?\s*\((?P<fleets>[^)]+)\)"
            legion_match = re.search(legion_pattern, game.current_proposal)
            fleet_match = re.search(fleet_pattern, game.current_proposal)
            legion_count = (
                int(legion_match.group("legion_count")) if legion_match else 0
            )
            legions_string = legion_match.group("legions") if legion_match else ""
            fleet_count = int(fleet_match.group("fleet_count")) if fleet_match else 0
            fleets_string = fleet_match.group("fleets") if fleet_match else ""
            legions = (
                cast(List[Legion], string_to_unit_list(legions_string, game_id, Legion))
                if legions_string
                else []
            )
            fleets = (
                cast(List[Fleet], string_to_unit_list(fleets_string, game_id, Fleet))
                if fleets_string
                else []
            )

            if len(legions) != legion_count:
                raise ValueError("Legion count didn't match legion names")
            if len(fleets) != fleet_count:
                raise ValueError("Fleet count didn't match fleet names")

            for legion in legions:
                legion.campaign = None
            Legion.objects.bulk_update(legions, ["campaign"])
            for fleet in fleets:
                fleet.campaign = None
            Fleet.objects.bulk_update(fleets, ["campaign"])

            if campaign:
                campaign_id = campaign.id
                updated_campaign = Campaign.objects.get(game=game, id=campaign_id)
                if len(campaign.legions.all()) + len(campaign.fleets.all()) == 0:
                    updated_campaign.delete()

            log_text = ""
            if commander:
                commander.location = "Rome"
                commander.remove_title(Senator.Title.PROCONSUL)
                commander.save()
                log_text += f"{commander.display_name} returned to Rome. "
            log_text += f"{unit_list_to_string(legions, fleets)} returned to the reserve forces."
            Log.create_object(game_id, log_text)

        else:

            # Proposal failed
            game.defeated_proposals.append(game.current_proposal)
            Log.create_object(
                game_id,
                f"Motion defeated: {game.current_proposal}.",
            )

        game.save()
        clear_proposal_and_votes(game_id)
        return True
