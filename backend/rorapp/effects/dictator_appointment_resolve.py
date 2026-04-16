from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.dictator_appointment import appoint_dictator
from rorapp.models import Faction, Game, Log, Senator


class DictatorAppointmentResolveEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        if not (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.DICTATOR_APPOINTMENT
            and (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
        ):
            return False

        # Collect unique factions that hold a consul senator
        consul_faction_ids = {
            s.faction_id
            for s in game_state.senators
            if s.faction_id
            and (
                s.has_title(Senator.Title.ROME_CONSUL)
                or s.has_title(Senator.Title.FIELD_CONSUL)
            )
        }
        if not consul_faction_ids:
            return False

        consul_factions = [f for f in game_state.factions if f.id in consul_faction_ids]
        # All consul-holding factions must have decided (SKIPPED or DONE)
        return all(
            f.has_status_item(FactionStatusItem.SKIPPED)
            or f.has_status_item(FactionStatusItem.DONE)
            for f in consul_factions
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        senators = list(Senator.objects.filter(game=game_id, alive=True))

        consul_faction_ids = {
            s.faction_id
            for s in senators
            if s.faction_id
            and (
                s.has_title(Senator.Title.ROME_CONSUL)
                or s.has_title(Senator.Title.FIELD_CONSUL)
            )
        }
        consul_factions = list(
            Faction.objects.filter(game=game_id, id__in=consul_faction_ids)
        )

        any_skipped = any(
            f.has_status_item(FactionStatusItem.SKIPPED) for f in consul_factions
        )

        if any_skipped:
            # At least one consul's faction skipped → go to election
            all_skipped = all(
                f.has_status_item(FactionStatusItem.SKIPPED) for f in consul_factions
            )
            if not all_skipped:
                Log.create_object(
                    game_id,
                    "Consuls could not agree on a Dictator.",
                )
            elif len(consul_factions) > 1:
                Log.create_object(
                    game_id,
                    "The consuls declined to appoint a Dictator.",
                )

            # Clear SUGGESTED_DICTATOR from all senators
            for s in senators:
                s.remove_status_item(Senator.StatusItem.SUGGESTED_DICTATOR)
            Senator.objects.bulk_update(senators, ["status_items"])
            # Clear DONE and SKIPPED from consul-holding factions
            for f in consul_factions:
                f.remove_status_item(FactionStatusItem.DONE)
                f.remove_status_item(FactionStatusItem.SKIPPED)
            Faction.objects.bulk_update(consul_factions, ["status_items"])

            game = Game.objects.get(id=game_id)
            game.sub_phase = Game.SubPhase.DICTATOR_ELECTION
            game.clear_defeated_proposals()
            game.save()
        else:
            # No skips — single-consul-faction case: appoint the SUGGESTED_DICTATOR senator
            suggested = next(
                (
                    s
                    for s in senators
                    if s.has_status_item(Senator.StatusItem.SUGGESTED_DICTATOR)
                ),
                None,
            )
            if not suggested:
                return False

            Log.create_object(
                game_id,
                f"The consuls appointed {suggested.display_name} as Dictator.",
            )
            suggested.remove_status_item(Senator.StatusItem.SUGGESTED_DICTATOR)
            suggested.save()
            # Clear DONE from all factions
            factions = list(Faction.objects.filter(game=game_id))
            for f in factions:
                f.remove_status_item(FactionStatusItem.DONE)
            Faction.objects.bulk_update(factions, ["status_items"])

            appoint_dictator(game_id, suggested.id)

        return True
