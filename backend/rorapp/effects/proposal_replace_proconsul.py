from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.clear_proposal_and_votes import clear_proposal_and_votes
from rorapp.models import Campaign, Game, Log, Senator, War


class ProposalReplaceProconsulEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.OTHER_BUSINESS
            and not (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
            and all(f.has_status_item(FactionStatusItem.DONE) for f in game_state.factions)
            and game_state.game.current_proposal.startswith("Replace ")
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        game = Game.objects.get(id=game_id)
        if not game.current_proposal:
            return False

        if game.votes_yea > game.votes_nay:

            # Proposal passed
            Log.create_object(game.id, f"Motion passed: {game.current_proposal}.")

            senators = Senator.objects.filter(game=game, alive=True)

            # Parse proposal
            # Extract current commander
            current_commander_name_and_more = game.current_proposal[len("Replace ") :]
            current_commander = next(
                (
                    s
                    for s in senators
                    if current_commander_name_and_more.startswith(s.display_name)
                ),
                None,
            )
            if not current_commander:
                raise ValueError("Invalid current commander")

            # Extract new commander
            with_index = game.current_proposal.find(" with ")
            if with_index == -1:
                raise ValueError("Invalid proposal format")
            new_commander_name_and_more = game.current_proposal[
                with_index + len(" with ") :
            ]
            new_commander = next(
                (
                    s
                    for s in senators
                    if new_commander_name_and_more.startswith(s.display_name)
                ),
                None,
            )
            if not new_commander:
                raise ValueError("Invalid new commander")

            # Extract war
            wars = War.objects.filter(game=game)
            war = next(
                (w for w in wars if game.current_proposal.endswith(w.name)), None
            )
            if war is None:
                raise ValueError("Invalid war")

            # Find the campaign
            campaign = Campaign.objects.filter(
                game=game, commander=current_commander, war=war
            ).first()
            if not campaign:
                raise ValueError(
                    f"No campaign found for {current_commander.display_name} in {war.name}"
                )

            # Check campaign wasn't recently deployed or reinforced
            if campaign.recently_deployed or campaign.recently_reinforced:
                Log.create_object(
                    game_id,
                    f"Cannot replace commander of a campaign that was recently deployed or reinforced.",
                )
                game.save()
                clear_proposal_and_votes(game_id)
                return True

            # Update campaign commander
            campaign.commander = new_commander
            campaign.save()

            # Current commander returns to Rome and loses proconsul title
            current_commander.location = "Rome"
            current_commander.save()
            current_commander.remove_title(Senator.Title.PROCONSUL)

            # New commander goes to war location
            new_commander.location = war.location
            new_commander.save()

            Log.create_object(
                game_id,
                f"{new_commander.display_name} departed Rome to take command of {campaign.display_name} in the {war.name}. {current_commander.display_name} returned to Rome. ",
            )

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
