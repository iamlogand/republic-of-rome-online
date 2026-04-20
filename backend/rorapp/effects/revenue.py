from rorapp.classes.concession import Concession
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.text import format_list, pluralize
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
                f"{active_war_cost}T on {pluralize(active_war_count, 'active war')}"
            )

        legions_count = game.legions.count()
        legions_cost = 2 * legions_count
        game.state_treasury -= legions_cost
        if legions_cost > 0:
            debits_descriptions.append(
                f"{legions_cost}T on maintaining {pluralize(legions_count, 'legion')}"
            )

        fleets_count = game.fleets.count()
        fleets_cost = 2 * fleets_count
        game.state_treasury -= fleets_cost
        if fleets_cost > 0:
            debits_descriptions.append(
                f"{fleets_cost}T on maintaining {pluralize(fleets_count, 'fleet')}"
            )

        land_bill_1_count = game.count_effect(GameEffect.LAND_BILL_1)
        land_bill_2_count = game.count_effect(GameEffect.LAND_BILL_2)
        land_bill_3_count = game.count_effect(GameEffect.LAND_BILL_3)
        land_bill_cost = (
            land_bill_1_count * 20 + land_bill_2_count * 5 + land_bill_3_count * 10
        )
        if land_bill_cost > 0:
            game.state_treasury -= land_bill_cost
            debits_descriptions.append(
                f"{land_bill_cost}T on {pluralize(land_bill_1_count + land_bill_2_count + land_bill_3_count, 'land bill')}"
            )
            if land_bill_1_count > 0:
                game.remove_effect(GameEffect.LAND_BILL_1)

        state_text = "The State earned 100T of revenue"
        if debits_descriptions:
            state_text += f" and spent {format_list(debits_descriptions)}"
        state_text += "."
        Log.create_object(game_id=game.id, text=state_text)

        # Senators earn personal revenue
        factions = Faction.objects.filter(game=game_id).order_by("position")
        for faction in factions:
            senators = Senator.objects.filter(game=game_id, faction=faction, alive=True)
            revenue = 0
            for senator in senators:
                if senator.has_title(Senator.Title.FACTION_LEADER):
                    senator.talents += 3
                    revenue += 3
                else:
                    senator.talents += 1
                    revenue += 1

                for concession in senator.get_concessions():
                    if concession == Concession.AEGYPTIAN_GRAIN:
                        concession_revenue = 5
                    elif concession == Concession.SICILIAN_GRAIN:
                        concession_revenue = 4
                    elif concession in [Concession.HARBOR_FEES, Concession.MINING]:
                        concession_revenue = 3
                    elif concession == Concession.LAND_COMMISSIONER:
                        concession_revenue = 3
                    elif concession in [
                        Concession.LATIUM_TAX_FARMER,
                        Concession.ETRURIA_TAX_FARMER,
                        Concession.SAMNIUM_TAX_FARMER,
                        Concession.CAMPANIA_TAX_FARMER,
                        Concession.APULIA_TAX_FARMER,
                        Concession.LUCANIA_TAX_FARMER,
                    ]:
                        concession_revenue = 2
                    else:
                        concession_revenue = 0
                    senator.talents += concession_revenue
                    revenue += concession_revenue
                    # Reveal corrupt bar only for concessions that earned revenue
                    # Armaments/Ship Building reveal their bar only when forces are raised
                    if concession_revenue > 0:
                        senator.add_corrupt_concession(concession)

            Senator.objects.bulk_update(senators, ["talents", "corrupt_concessions"])
            Log.create_object(
                game_id=game.id,
                text=f"Senators in {faction.display_name} earned {revenue}T of revenue.",
            )

        # Progress game
        game.sub_phase = Game.SubPhase.REDISTRIBUTION
        game.save()
        return True
