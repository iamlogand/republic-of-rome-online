from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Game, Log, Senator


class SenateStartEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.START
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        game = Game.objects.get(id=game_id)

        # Make the HRAO into the Presiding Magistrate
        senators = [s for s in Senator.objects.filter(game_id=game_id)]
        for senator in senators:
            if senator.has_title(Senator.Title.HRAO):
                senator.add_title(Senator.Title.PRESIDING_MAGISTRATE)
                senator.save()
                Log.create_object(
                    game_id=game.id,
                    text=f"{senator.display_name} opened the senate as presiding magistrate.",
                )

        # Assign MAJOR markers to senators who hold a major office (§1.07.8)
        major_office_titles = [
            Senator.Title.ROME_CONSUL,
            Senator.Title.FIELD_CONSUL,
            Senator.Title.PROCONSUL,
            Senator.Title.CENSOR,
        ]
        for senator in senators:
            if senator.location == "Rome" and senator.alive:
                if any(senator.has_title(t) for t in major_office_titles):
                    senator.add_status_item(Senator.StatusItem.MAJOR_CORRUPT)
                    senator.save()

        # Progress game
        game.phase = Game.Phase.SENATE
        game.sub_phase = Game.SubPhase.CONSULAR_ELECTION
        game.save()
        return True
