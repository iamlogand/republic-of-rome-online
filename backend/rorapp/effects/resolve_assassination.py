from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.assassination_proposal_consequences import (
    handle_proposal_consequences,
)
from rorapp.helpers.kill_senator import CauseOfDeath, kill_senator
from rorapp.models import Faction, Game, Log, Senator


class ResolveAssassinationEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.ASSASSINATION_RESOLUTION
            and game_state.game.assassination_roll_result != 0
            and not any(
                f
                for f in game_state.factions
                if f.has_status_item(FactionStatusItem.AWAITING_DECISION)
            )
            and game_state.game.bodyguard_rerolls_remaining == 0
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        senators = list(Senator.objects.filter(game=game_id, alive=True))

        assassin = next(
            (s for s in senators if s.has_status_item(Senator.StatusItem.ASSASSIN)),
            None,
        )
        target = next(
            (
                s
                for s in senators
                if s.has_status_item(Senator.StatusItem.ASSASSINATION_TARGET)
            ),
            None,
        )

        if assassin is None or target is None:
            self._cleanup(game, senators)
            return True

        is_caught = assassin.has_status_item(Senator.StatusItem.CAUGHT)
        roll_result = game.assassination_roll_result

        # Log the outcome now that bodyguards have had their chance
        if roll_result >= 5 and is_caught:
            Log.create_object(
                game_id,
                f"The assassination attempt succeeded, but {assassin.display_name} was caught!",
            )
        elif roll_result >= 5:
            Log.create_object(
                game_id,
                f"The assassination attempt succeeded. {target.display_name} was killed!",
            )
        elif is_caught:
            Log.create_object(
                game_id,
                f"The assassination attempt failed. {assassin.display_name} was caught!",
            )
        else:
            Log.create_object(
                game_id,
                f"The assassination attempt had no effect. {target.display_name} survived and the assassin escaped.",
            )

        is_land_bill_assassination = (
            game.interrupted_sub_phase == Game.SubPhase.OTHER_BUSINESS
            and game.current_proposal is not None
            and "land bill" in game.current_proposal.lower()
            and target.has_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
            and self._sponsors_are_same_faction(game_id)
        )

        # --- Apply target consequence ---
        # Capture NAMED_IN_PROPOSAL before kill_senator clears status items.
        target_named_in_proposal = target.has_status_item(
            Senator.StatusItem.NAMED_IN_PROPOSAL
        )
        target_killed = False
        if roll_result >= 5 and not is_caught:
            # Target was killed before a bodyguard-catch-reroll could save them;
            # a caught result on a reroll does NOT undo the kill (it's possible to
            # kill the target AND have the assassin caught by a subsequent reroll).
            kill_senator(target, CauseOfDeath.ASSASSINATION)
            target_killed = True
            # Reload game after kill_senator may have saved it
            game.refresh_from_db()
            handle_proposal_consequences(game, target, target_named_in_proposal)
            game.refresh_from_db()
        elif roll_result >= 5 and is_caught:
            # Bodyguard catch reroll caught the assassin after the original kill roll.
            # Kill the target first, then punish the assassin below.
            kill_senator(target, CauseOfDeath.ASSASSINATION)
            target_killed = True
            game.refresh_from_db()
            handle_proposal_consequences(game, target, target_named_in_proposal)
            game.refresh_from_db()

        # --- Apply caught consequence ---
        if is_caught:
            assert assassin.faction_id is not None
            assassin_faction_id = assassin.faction_id
            was_faction_leader = assassin.has_title(Senator.Title.FACTION_LEADER)
            target_popularity = target.popularity

            kill_senator(assassin, CauseOfDeath.EXECUTION)
            game.refresh_from_db()

            if not is_land_bill_assassination:
                # Faction Leader loses 5 influence
                faction_leader = next(
                    (
                        s
                        for s in Senator.objects.filter(
                            game=game_id, alive=True, faction_id=assassin_faction_id
                        )
                        if s.has_title(Senator.Title.FACTION_LEADER)
                    ),
                    None,
                )
                if faction_leader and not was_faction_leader:
                    faction_leader.influence = max(0, faction_leader.influence - 5)
                    faction_leader.save()
                    Log.create_object(
                        game_id,
                        f"{faction_leader.display_name} loses 5 influence for the failed assassination.",
                    )

                # Mortality chit draw if target had positive popularity
                chit_count = max(target_popularity, 0)
                if chit_count > 0:
                    codes = random_resolver.draw_mortality_chits(chit_count)
                    faction_senators = list(
                        Senator.objects.filter(
                            game=game_id, alive=True, faction_id=assassin_faction_id
                        )
                    )
                    for code in codes:
                        for senator in faction_senators:
                            from rorapp.helpers.game_data import get_senator_codes

                            if get_senator_codes(senator.code)[0] == str(code):
                                Log.create_object(
                                    game_id,
                                    f"{senator.display_name} is implicated in the assassination plot.",
                                )
                                kill_senator(senator, CauseOfDeath.ASSASSINATION)
                                game.refresh_from_db()
                                break

        # --- Clean up assassination statuses ---
        self._cleanup(game, list(Senator.objects.filter(game=game_id, alive=True)))

        # --- Return to interrupted sub_phase ---
        game.sub_phase = game.interrupted_sub_phase
        game.interrupted_sub_phase = ""
        game.assassination_roll_result = 0
        game.assassination_roll_modifier = 0
        game.bodyguard_rerolls_remaining = 0
        game.save()

        return True

    def _sponsors_are_same_faction(self, game_id: int) -> bool:
        sponsors = list(
            Senator.objects.filter(
                game=game_id,
                alive=True,
                status_items__contains=Senator.StatusItem.NAMED_IN_PROPOSAL.value,
            )
        )
        if len(sponsors) < 2:
            return False
        return all(s.faction_id == sponsors[0].faction_id for s in sponsors[1:])

    def _cleanup(self, game: Game, senators: list) -> None:
        cleanup_statuses = [
            Senator.StatusItem.ASSASSIN,
            Senator.StatusItem.ASSASSINATION_TARGET,
            Senator.StatusItem.CAUGHT,
        ]
        for senator in senators:
            changed = False
            for status in cleanup_statuses:
                if senator.has_status_item(status):
                    senator.remove_status_item(status)
                    changed = True
            if changed:
                senator.save()
