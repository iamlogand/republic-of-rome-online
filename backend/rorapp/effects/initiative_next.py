from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Senator

INITIATIVE_STATUS_ITEMS = [
    Faction.StatusItem.initiative(1),
    Faction.StatusItem.initiative(2),
    Faction.StatusItem.initiative(3),
    Faction.StatusItem.initiative(4),
    Faction.StatusItem.initiative(5),
    Faction.StatusItem.initiative(6),
]


class InitiativeNextEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        if (
            game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.END
        ):
            for item in INITIATIVE_STATUS_ITEMS:
                if not any(f.has_status_item(item) for f in game_state.factions):
                    return True
        return False

    def execute(self, game_id: int) -> None:
        factions = Faction.objects.filter(game=game_id)
        positions = [f.position for f in factions.order_by("position")]

        for item in reversed(INITIATIVE_STATUS_ITEMS[:5]):
            for faction in factions:
                if faction.has_status_item(item):

                    # Figure out which faction is next
                    next_item_index = INITIATIVE_STATUS_ITEMS.index(item) + 1
                    next_item = INITIATIVE_STATUS_ITEMS[next_item_index]
                    next_position_index = positions.index(faction.position) + 1
                    next_position = (
                        positions[next_position_index]
                        if next_position_index < len(positions)
                        else positions[0]
                    )
                    next_faction = factions.get(position=next_position)

                    game = Game.objects.get(id=game_id)
                    if not any(
                        next_faction.has_status_item(i)
                        for i in INITIATIVE_STATUS_ITEMS[:5]
                    ):
                        # Next faction hasn't yet took an initiative
                        next_faction.add_status_item(next_item)
                        next_faction.add_status_item(
                            Faction.StatusItem.CURRENT_INITIATIVE
                        )
                        next_faction.save()
                        game.sub_phase = Game.SubPhase.FACTION_LEADER
                    else:
                        # All factions have taken at least one initiative
                        # TODO implement an initiative bidding system
                        for faction in factions:
                            for item in INITIATIVE_STATUS_ITEMS:
                                if faction.has_status_item(item):
                                    faction.remove_status_item(item)
                        game.phase = Game.Phase.REVENUE
                        game.sub_phase = Game.SubPhase.START

                    game.save()
                    return
