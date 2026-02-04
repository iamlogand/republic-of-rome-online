from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game


class InitiativeNextEffect(EffectBase):
    """Pass the next initiative to the next faction."""

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.END
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        factions = Faction.objects.filter(game=game_id)
        positions = [f.position for f in factions.order_by("position")]

        for initiative_index in reversed(Faction.INITIATIVE_INDICES):
            for faction in factions:
                if faction.has_status_item(
                    FactionStatusItem.initiative(initiative_index)
                ):
                    game = Game.objects.get(id=game_id)
                    if initiative_index == Faction.INITIATIVE_INDICES[-1]:
                        # Last initiative has been taken
                        for faction in factions:
                            for i in Faction.INITIATIVE_INDICES:
                                if faction.has_status_item(
                                    FactionStatusItem.initiative(i)
                                ):
                                    faction.remove_status_item(
                                        FactionStatusItem.initiative(i)
                                    )
                        game.phase = Game.Phase.POPULATION
                        game.sub_phase = Game.SubPhase.START
                        game.save()
                        return True

                    # Figure out which faction is next
                    next_initiative = FactionStatusItem.initiative(
                        initiative_index + 1
                    )
                    next_position_index = positions.index(faction.position) + 1
                    next_position = (
                        positions[next_position_index]
                        if next_position_index < len(positions)
                        else positions[0]
                    )
                    next_faction = factions.get(position=next_position)

                    if not any(
                        next_faction.has_status_item(FactionStatusItem.initiative(i))
                        for i in Faction.INITIATIVE_INDICES
                    ):
                        # Next faction hasn't yet took an initiative
                        next_faction.add_status_item(next_initiative)
                        next_faction.add_status_item(
                            FactionStatusItem.CURRENT_INITIATIVE
                        )
                        next_faction.save()
                        game.sub_phase = Game.SubPhase.INITIATIVE_ROLL
                    else:
                        # All factions have taken at least one initiative
                        game.sub_phase = Game.SubPhase.INITIATIVE_AUCTION
                    game.save()
                    return True
        return False
