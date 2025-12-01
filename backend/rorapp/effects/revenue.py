from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Log, Senator, War


class RevenueEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.REVENUE
            and game_state.game.sub_phase == Game.SubPhase.START
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        game = Game.objects.get(id=game_id)

        # Rome earns revenue
        game.state_treasury += 100
        debits_descriptions = []

        active_war_count = game.wars.filter(status=War.Status.ACTIVE).count()
        active_war_cost = active_war_count * 20
        game.state_treasury -= active_war_cost
        if active_war_cost > 0:
            debits_descriptions.append(
                f"{active_war_cost}T on {active_war_count} active wars"
            )

        legions_count = game.legions.count()
        legions_cost = 2 * legions_count
        game.state_treasury -= legions_cost
        if legions_cost > 0:
            debits_descriptions.append(
                f"{legions_cost}T on maintaining {legions_count} legions"
            )

        fleets_count = game.fleets.count()
        fleets_cost = 2 * fleets_count
        game.state_treasury -= fleets_cost
        if fleets_cost > 0:
            debits_descriptions.append(
                f"{fleets_cost}T on maintaining {fleets_count} fleets"
            )

        state_text = "The State earned 100T of revenue"
        count = len(debits_descriptions)
        if count > 0:
            state_text += " and spent"
        for i in range(count):
            description = debits_descriptions[i]
            if i > 0:
                if i == count - 1:
                    state_text += " and"
                else:
                    state_text += ","
            state_text += f" {description}"
        state_text += "."
        Log.create_object(game_id=game.id, text=state_text)

        # Senators earn personal revenue
        factions = Faction.objects.filter(game=game_id).order_by("position")
        for faction in factions:
            senators = Senator.objects.filter(game=game_id, faction=faction, alive=True)
            faction_revenue = 0
            for senator in senators:
                if senator.has_title(Senator.Title.FACTION_LEADER):
                    senator.talents += 3
                    faction_revenue += 3
                else:
                    senator.talents += 1
                    faction_revenue += 1
            Senator.objects.bulk_update(senators, ["talents"])
            Log.create_object(
                game_id=game.id,
                text=f"{faction.display_name} earned {faction_revenue}T of revenue.",
            )

        # Progress game
        game.sub_phase = Game.SubPhase.REDISTRIBUTION
        game.save()
        return True
