from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import Faction, Fleet, Game, Legion, Log, Senator


class ReleasedForcesMaintenanceEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.REVENUE
            and game_state.game.sub_phase == Game.SubPhase.RELEASED_FORCES_MAINTENANCE
            and not any(
                f.has_status_item(FactionStatusItem.AWAITING_DECISION)
                for f in game_state.factions
            )
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)

        released_legions = list(
            Legion.objects.filter(game=game_id, released_by_rebel=True).order_by("number")
        )
        released_fleets = list(
            Fleet.objects.filter(game=game_id, released_by_rebel=True).order_by("number")
        )

        # If the State cannot afford any released forces, eliminate them all immediately (§1.11.35)
        if game.state_treasury < 2:
            if released_legions or released_fleets:
                Log.create_object(
                    game_id,
                    f"{unit_list_to_string(released_legions, released_fleets)} "
                    f"were eliminated as the State could not afford their maintenance.",
                )
                for legion in released_legions:
                    legion.delete()
                for fleet in released_fleets:
                    fleet.delete()
            game.sub_phase = Game.SubPhase.REDISTRIBUTION
            game.save()
            return True

        # Otherwise prompt the HRAO to decide which forces to maintain
        hrao = next(
            (
                s
                for s in Senator.objects.filter(game=game_id)
                if s.has_title(Senator.Title.HRAO)
            ),
            None,
        )
        if hrao and hrao.faction_id:
            faction = Faction.objects.get(id=hrao.faction_id)
            faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
            faction.save()
        return True
