from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Senator


class PersuasionCounterBribeNextEffect(EffectBase):
    """Advance to the next counter-bidder, or end the round and move to persuasion decision."""

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.PERSUASION_COUNTER_BRIBE
            and any(
                f.has_status_item(FactionStatusItem.CURRENT_COUNTER_BRIBER)
                and (
                    f.has_status_item(FactionStatusItem.SKIPPED)
                    or f.has_status_item(FactionStatusItem.COUNTER_BRIBED)
                )
                for f in game_state.factions
            )
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        factions = list(Faction.objects.filter(game=game_id).order_by("position"))

        persuading_senator = next(
            (
                s
                for s in Senator.objects.filter(game=game_id, alive=True)
                if s.has_status_item(Senator.StatusItem.PERSUADER)
            ),
            None,
        )
        if not persuading_senator:
            return False
        persuader = next(
            (f for f in factions if f.id == persuading_senator.faction_id), None
        )
        if not persuader:
            return False

        current = next(
            (
                f
                for f in factions
                if f.has_status_item(FactionStatusItem.CURRENT_COUNTER_BRIBER)
            ),
            None,
        )
        if not current:
            return False

        current.remove_status_item(FactionStatusItem.CURRENT_COUNTER_BRIBER)
        current.save()

        # Reload to get updated state after save
        factions = list(Faction.objects.filter(game=game_id).order_by("position"))

        # Find all non-persuader factions that haven't acted this round
        pending = [
            f
            for f in factions
            if f.id != persuader.id
            and not f.has_status_item(FactionStatusItem.SKIPPED)
            and not f.has_status_item(FactionStatusItem.COUNTER_BRIBED)
        ]

        if pending:
            # Find the first pending faction clockwise after current.position
            positions = [f.position for f in factions]
            current_index = positions.index(current.position)
            n = len(positions)
            for i in range(1, n + 1):
                candidate = factions[(current_index + i) % n]
                if candidate in pending:
                    candidate.add_status_item(FactionStatusItem.CURRENT_COUNTER_BRIBER)
                    candidate.save()
                    return True

        # All non-persuader factions have acted — end of round
        game = Game.objects.get(id=game_id)
        game.sub_phase = Game.SubPhase.PERSUASION_DECISION
        game.save()
        return True
