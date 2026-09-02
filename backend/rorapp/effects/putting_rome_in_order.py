from rorapp.classes.concession import Concession
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.destroy_concession import destroy_concession
from rorapp.helpers.text import format_list
from rorapp.models import EnemyLeader, Game, Log, Senator, War

TAX_FARMERS_BY_ROLL = {
    1: Concession.LATIUM_TAX_FARMER,
    2: Concession.ETRURIA_TAX_FARMER,
    3: Concession.SAMNIUM_TAX_FARMER,
    4: Concession.CAMPANIA_TAX_FARMER,
    5: Concession.APULIA_TAX_FARMER,
    6: Concession.LUCANIA_TAX_FARMER,
}


class PuttingRomeInOrderEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.PUTTING_ROME_IN_ORDER
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        evil_omens_level = game.count_effect(GameEffect.EVIL_OMENS)

        self._destroy_tax_farmers(game, random_resolver)

        revived_concessions = []
        for concession in game.get_destroyed_concessions():
            roll = random_resolver.roll_dice() - evil_omens_level
            if roll >= 5:
                game.remove_destroyed_concession(concession)
                game.add_concession(concession)
                revived_concessions.append(concession.value)
        if revived_concessions:
            subject = (
                f"The {revived_concessions[0]} concession was"
                if len(revived_concessions) == 1
                else f"The {format_list(revived_concessions)} concessions were"
            )
            Log.create_object(
                game_id,
                f"{subject} rebuilt and returned to the forum.",
            )

        dead_senator_list = list(
            Senator.objects.filter(game=game_id, alive=False, family=True)
        )

        for senator in dead_senator_list:
            roll = random_resolver.roll_dice() - evil_omens_level
            if roll >= 5:
                previous_name = (
                    f"{senator.display_name}'"
                    if senator.display_name.endswith("s")
                    else f"{senator.display_name}'s"
                )
                senator.generation += 1
                senator.alive = True
                senator.save()
                Log.create_object(
                    game_id,
                    f"{previous_name} heir {senator.display_name} appeared as an unaligned senator.",
                )

        inactive_leaders = list(EnemyLeader.objects.filter(game=game_id, active=False))
        dead_leaders = []
        for leader in inactive_leaders:
            roll = random_resolver.roll_dice() - evil_omens_level
            if roll >= 5:
                dead_leaders.append(leader.name)
                leader.delete()
        if dead_leaders:
            Log.create_object(
                game_id,
                f"Enemy leader{' ' if len(dead_leaders) == 1 else 's '}{format_list(dead_leaders)} died.",
            )

        if game.era_ends:
            game.sub_phase = Game.SubPhase.ERA_ENDS
        else:
            game.phase = Game.Phase.POPULATION
            game.sub_phase = Game.SubPhase.START
        game.save()
        return True

    def _destroy_tax_farmers(self, game: Game, random_resolver: RandomResolver) -> None:
        if not War.objects.filter(
            game=game.id, series_name="Punic", index=1, status=War.Status.ACTIVE
        ).exists():
            return

        causes = ["The 2nd Punic War"]
        # Hannibal threatens tax farmers only while matched with the 2nd Punic War
        # (1.07.8), but a leader is recorded as active within his series rather than
        # placed on a particular war, so an active Hannibal is read as matched with
        # it. Giving EnemyLeader a link to its war would settle this exactly.
        if EnemyLeader.objects.filter(
            game=game.id, name="Hannibal", active=True
        ).exists():
            causes.append("Hannibal")

        for cause in causes:
            # Evil omens do not modify these rolls (1.07.8)
            concession = TAX_FARMERS_BY_ROLL[random_resolver.roll_dice()]
            destroyed, holder = destroy_concession(game, concession)
            if not destroyed:
                text = f"{cause} threatened the {concession.value} concession, which was not in play."
            elif holder:
                text = f"{cause} destroyed the {concession.value} concession held by {holder.display_name}."
            else:
                text = f"{cause} destroyed the unawarded {concession.value} concession."
            Log.create_object(game.id, text)
