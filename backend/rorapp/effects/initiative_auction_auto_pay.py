from typing import List
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Log, Senator


class InitiativeAuctionAutoPayEffect(EffectBase):
    """
    After the initiative auction has been won,
    if the winning faction has only one senator that can afford to pay,
    automatically get that senator to pay for the initiative.
    """

    def validate(self, game_state: GameStateSnapshot) -> bool:
        if (
            game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.INITIATIVE_AUCTION
            and any(
                f.has_status_item(Faction.StatusItem.AUCTION_WINNER)
                for f in game_state.factions
            )
        ):
            if not any(f.get_bid_amount() is not None for f in game_state.factions):
                # The bid amount is zero, so no decision is needed
                return True

            for faction in game_state.factions:
                if faction.has_status_item(Faction.StatusItem.AUCTION_WINNER):
                    bid_amount = faction.get_bid_amount()
                    if (
                        bid_amount
                        and len(
                            [
                                s
                                for s in game_state.senators
                                if s.faction
                                and s.faction.id == faction.id
                                and s.talents >= bid_amount
                                and s.alive
                            ]
                        )
                        == 1
                    ):
                        # One senator can afford to pay, so no decision is needed
                        return True
        return False

    def execute(self, game_id: int) -> bool:

        factions = Faction.objects.filter(game=game_id)
        for faction in factions:
            if faction.has_status_item(Faction.StatusItem.AUCTION_WINNER):
                bid_amount = faction.get_bid_amount()
                senator = None

                if bid_amount:
                    # Ensure that only one senator can afford to pay
                    senators_that_can_pay: List[Senator] = []
                    for s in Senator.objects.filter(
                        game=game_id, faction=faction, alive=True
                    ):
                        if s.talents >= bid_amount:
                            senators_that_can_pay.append(s)
                    if len(senators_that_can_pay) != 1:
                        return False
                    senator = senators_that_can_pay[0]

                    senator.talents -= bid_amount
                    senator.save()

                faction.remove_status_item(Faction.StatusItem.AUCTION_WINNER)

                # Clean up
                for f in factions:
                    f.set_bid_amount(None)
                    if f.has_status_item(Faction.StatusItem.SKIPPED):
                        f.remove_status_item(Faction.StatusItem.SKIPPED)

                game = Game.objects.get(id=game_id)
                game.sub_phase = Game.SubPhase.INITIATIVE_ROLL
                game.save()

                factions = Faction.objects.filter(game=game_id)
                for initiative_index in Faction.INITIATIVE_INDICES:
                    if not any(
                        f.has_status_item(
                            Faction.StatusItem.initiative(initiative_index)
                        )
                        for f in factions
                    ):
                        faction.add_status_item(
                            Faction.StatusItem.initiative(initiative_index)
                        )
                        faction.add_status_item(Faction.StatusItem.CURRENT_INITIATIVE)
                        faction.save()

                        if senator and bid_amount:
                            Log.create_object(
                                game_id=game_id,
                                text=f"{senator.display_name} paid {bid_amount}T for initiative {initiative_index}.",
                            )
                        return True

        return False
