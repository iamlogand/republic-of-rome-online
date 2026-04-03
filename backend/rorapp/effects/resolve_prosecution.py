import math
from rorapp.classes.concession import Concession
from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.finish_prosecution import finish_prosecution
from rorapp.helpers.kill_senator import kill_senator
from rorapp.helpers.text import format_list
from rorapp.models import Game, Log, Senator


class ResolveProsecutionEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.PROSECUTION
            and not (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
            and all(
                f.has_status_item(FactionStatusItem.DONE) for f in game_state.factions
            )
            and game_state.game.current_proposal.startswith("Prosecute ")
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        game = Game.objects.get(id=game_id)
        if not game.current_proposal:
            return False

        is_major = game.current_proposal.endswith("major corruption in office")
        senators = Senator.objects.filter(game=game_id)
        accused = next(
            (s for s in senators if s.has_status_item(Senator.StatusItem.ACCUSED)), None
        )
        prosecutor = next(
            (s for s in senators if s.has_status_item(Senator.StatusItem.PROSECUTOR)),
            None,
        )

        if not accused or not prosecutor:
            return False

        accused_had_prior_consul = accused.has_title(Senator.Title.PRIOR_CONSUL)
        accused_influence_before = accused.influence

        if game.votes_yea > game.votes_nay:
            # Guilty
            if is_major:
                if accused.alive:
                    kill_senator(accused)
                prosecutor = Senator.objects.get(id=prosecutor.id)
                if accused_had_prior_consul:
                    prosecutor.add_title(Senator.Title.PRIOR_CONSUL)
                prosecutor.influence += math.ceil(accused_influence_before / 2)
                prosecutor.save()
                if accused_had_prior_consul:
                    verdict_text = f"{accused.display_name} was found guilty of major corruption and executed. {prosecutor.display_name} gained prior consul status and {math.ceil(accused_influence_before / 2)} influence."
                else:
                    verdict_text = f"{accused.display_name} was found guilty of major corruption and executed. {prosecutor.display_name} gained {math.ceil(accused_influence_before / 2)} influence."
                Log.create_object(game_id=game.id, text=verdict_text)
            else:
                accused = Senator.objects.get(id=accused.id)
                accused.change_popularity(-5)
                influence_lost = min(5, accused.influence)
                accused.influence = max(0, accused.influence - 5)
                accused.remove_title(Senator.Title.PRIOR_CONSUL)
                concessions_taken = accused.get_concessions()
                for c in concessions_taken:
                    game.add_concession(c)
                accused.clear_concessions()
                accused.clear_corrupt_concessions()
                accused.save()
                game.save()

                prosecutor = Senator.objects.get(id=prosecutor.id)
                if accused_had_prior_consul:
                    prosecutor.add_title(Senator.Title.PRIOR_CONSUL)
                prosecutor.influence += math.ceil(influence_lost / 2)
                prosecutor.save()

                losses = []
                if influence_lost > 0:
                    losses.append(f"{influence_lost} influence")
                losses.append("5 popularity")
                if accused_had_prior_consul:
                    losses.append("prior consul status")
                if concessions_taken:
                    n = len(concessions_taken)
                    losses.append(f"{n} concession{'s' if n > 1 else ''}")
                gained_pc = (
                    " gained prior consul status and"
                    if accused_had_prior_consul
                    else " gained"
                )
                Log.create_object(
                    game_id=game.id,
                    text=f"{accused.display_name} was found guilty of minor corruption, losing {format_list(losses)}. {prosecutor.display_name}{gained_pc} {math.ceil(influence_lost / 2)} influence.",
                )
                if concessions_taken:
                    n = len(concessions_taken)
                    if n == 1:
                        concession_log = f"The conviction of {accused.display_name} has made the {concessions_taken[0]} concession available."
                    else:
                        concession_log = f"The conviction of {accused.display_name} has made the {format_list(concessions_taken)} concessions available."
                    Log.create_object(game_id=game.id, text=concession_log)

            finish_prosecution(game_id, is_major, guilty=True)

        else:
            # Not guilty
            reason = self._get_reason(game.current_proposal)
            game.add_defeated_proposal(game.current_proposal)
            if reason.startswith("corruption via ") and reason.endswith(" concession"):
                concession = Concession(reason[len("corruption via ") : -len(" concession")])
                accused.remove_corrupt_concession(concession)
                accused.save()
            Log.create_object(
                game_id=game.id,
                text=f"Motion defeated: {game.current_proposal}.",
            )
            game.save()
            finish_prosecution(game_id, is_major, guilty=False)

        return True

    def _get_reason(self, proposal: str) -> str:
        parts = proposal.split(" for ", 1)
        return parts[1] if len(parts) == 2 else ""
