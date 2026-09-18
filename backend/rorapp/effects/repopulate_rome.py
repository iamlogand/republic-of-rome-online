from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.repopulation import (
    SENATORS_REQUIRED_IN_ROME,
    count_aligned_senators_in_rome,
    faction_to_receive_senator,
    senators_awaiting_promotion,
    unaligned_senators_in_rome,
)
from rorapp.helpers.text import possessive
from rorapp.models import Faction, Game, Log, Senator


class RepopulateRomeEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        game = game_state.game
        if game.phase != Game.Phase.SENATE:
            return False
        if game.sub_phase in (
            Game.SubPhase.START,
            Game.SubPhase.ASSASSINATION_RESOLUTION,
            Game.SubPhase.REPOPULATION,
            # The senate closes with automatic recalls, which may fill Rome (1.09.9)
            Game.SubPhase.END,
        ):
            return False
        if any(
            f.has_status_item(FactionStatusItem.AWAITING_DECISION)
            for f in game_state.factions
        ):
            return False
        if (
            count_aligned_senators_in_rome(game_state.senators)
            >= SENATORS_REQUIRED_IN_ROME
        ):
            return False
        return bool(
            senators_awaiting_promotion(game_state.senators)
            or unaligned_senators_in_rome(game_state.senators)
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        senators = list(Senator.objects.filter(game=game_id))
        factions = list(Faction.objects.filter(game=game_id).order_by("position"))

        faction = faction_to_receive_senator(factions, senators, random_resolver)
        if faction is None:
            return False

        awaiting_promotion = senators_awaiting_promotion(senators)
        if awaiting_promotion:
            senator = awaiting_promotion[0]
            previous_name = possessive(senator.display_name)
            senator.generation += 1
            senator.alive = True
            senator.faction = faction
            senator.location = "Rome"
            senator.curia_position = None
            senator.save()
            Log.create_object(
                game_id,
                f"With fewer than {SENATORS_REQUIRED_IN_ROME} aligned senators in Rome, "
                f"{previous_name} heir {senator.display_name} joined {faction.display_name}.",
            )
            return True

        # The receiving player chooses which of the unaligned senators to take (1.09.81)
        faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
        faction.save()
        game.interrupted_sub_phase = game.sub_phase or ""
        game.sub_phase = Game.SubPhase.REPOPULATION
        game.save()
        return True
