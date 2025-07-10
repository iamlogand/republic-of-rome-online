import random
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.clear_proposal_and_votes import clear_proposal_and_votes
from rorapp.helpers.transfer_power_consuls import transfer_power_consuls
from rorapp.models import Faction, Game, Senator
from rorapp.models.log import Log


class PreferredConsularOfficesEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.CONSULAR_ELECTION
            and len(
                [
                    s
                    for s in game_state.senators
                    if s.has_status_item(Senator.StatusItem.INCOMING_CONSUL)
                    and (
                        s.has_status_item(Senator.StatusItem.PREFERS_ROME_CONSUL)
                        or s.has_status_item(Senator.StatusItem.PREFERS_FIELD_CONSUL)
                    )
                ]
            )
            == 2
        )

    def execute(self, game_id: int) -> bool:

        senators = Senator.objects.filter(game=game_id, alive=True)

        consuls = [
            s
            for s in senators
            if s.has_status_item(Senator.StatusItem.INCOMING_CONSUL)
            and (
                s.has_status_item(Senator.StatusItem.PREFERS_ROME_CONSUL)
                or s.has_status_item(Senator.StatusItem.PREFERS_FIELD_CONSUL)
            )
        ]
        prefer_rome_consul = [
            c
            for c in consuls
            if c.has_status_item(Senator.StatusItem.PREFERS_ROME_CONSUL)
        ]
        prefer_field_consul = [
            c
            for c in consuls
            if c.has_status_item(Senator.StatusItem.PREFERS_FIELD_CONSUL)
        ]

        if len(prefer_rome_consul) == 1:
            # Senators agree
            rome_consul = prefer_rome_consul[0]
            field_consul = prefer_field_consul[0]
            Log.create_object(
                game_id,
                f"{rome_consul.display_name} agreed to be Rome Consul and {field_consul.display_name} agreed to be Field Consul.",
            )
        else:
            # Senators disagree
            random.shuffle(consuls)
            rome_consul = consuls[0]
            field_consul = consuls[1]
            Log.create_object(
                game_id,
                f"Incoming consuls had conflicting preferences. After casting lots, {rome_consul.display_name} became Rome Consul and {field_consul.display_name} became Field Consul.",
            )

        transfer_power_consuls(game_id, rome_consul.id, field_consul.id)

        return True
