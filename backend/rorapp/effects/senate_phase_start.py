from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.game_data import load_statesmen
from rorapp.models import Faction, Game, Log, Senator


class SenatePhaseStartEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.START
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        game = Game.objects.get(id=game_id)

        # Reset per-turn assassination tracking
        factions = list(Faction.objects.filter(game=game))
        for faction in factions:
            faction.remove_status_item(FactionStatusItem.ATTEMPTED_ASSASSINATION)
            faction.remove_status_item(FactionStatusItem.ASSASSINATION_TARGETED)
        Faction.objects.bulk_update(factions, ["status_items"])

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

        # Assign MAJOR markers to senators who hold a major office
        major_office_titles = [
            Senator.Title.DICTATOR,
            Senator.Title.MASTER_OF_HORSE,
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

        # Grant free tribune to statesmen with that special ability
        statesmen_dict = load_statesmen()
        for senator in senators:
            if senator.alive and senator.location == "Rome" and senator.statesman_name:
                senator_data = next(
                    (v for v in statesmen_dict.values() if v["code"] == senator.code),
                    None,
                )
                if senator_data and "free_tribune" in senator_data.get("special", []):
                    senator.add_status_item(Senator.StatusItem.FREE_TRIBUNE)
                    senator.save()

        # Progress game
        game.phase = Game.Phase.SENATE
        game.sub_phase = Game.SubPhase.CONSULAR_ELECTION
        game.save()
        return True
