import json
import os
from typing import Any, Dict, List, Optional
from django.conf import settings
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


def _load_statesmen() -> dict:
    path = os.path.join(settings.BASE_DIR, "rorapp", "data", "statesman.json")
    with open(path, "r") as f:
        return json.load(f)


def _load_senators() -> dict:
    path = os.path.join(settings.BASE_DIR, "rorapp", "data", "senator.json")
    with open(path, "r") as f:
        return json.load(f)


def _family_code(statesman_code: str) -> str:
    return "".join(c for c in statesman_code if c.isdigit())


class PlayStatesmanAction(ActionBase):
    NAME = "Play statesman"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if not faction:
            return None

        if not any(c.startswith("statesman:") for c in faction.cards):
            return None

        if (
            game_state.game.phase == Game.Phase.REVOLUTION
            and game_state.game.sub_phase == Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
            and faction.has_status_item(FactionStatusItem.AWAITING_DECISION)
        ):
            return faction

        if (
            game_state.game.phase == Game.Phase.INITIAL
            and game_state.game.sub_phase == Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
            and faction.has_status_item(FactionStatusItem.AWAITING_DECISION)
        ):
            return faction

        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        game_id = snapshot.game.id
        statesman_cards = [c for c in faction.cards if c.startswith("statesman:")]

        statesmen_dict = _load_statesmen()

        options = []
        for card in statesman_cards:
            statesman_code = card.split(":", 1)[1]
            family_code = _family_code(statesman_code)

            # Skip if same statesman already in play
            if any(s.code == statesman_code and s.alive for s in snapshot.senators):
                continue

            # Skip if opponent controls the family senator
            if any(
                s.code == family_code
                and s.family
                and s.alive
                and s.faction
                and s.faction.id != faction_id
                for s in snapshot.senators
            ):
                continue

            display_name = next(
                (k for k, v in statesmen_dict.items() if v["code"] == statesman_code),
                statesman_code,
            )
            options.append({"value": card, "name": display_name})

        if not options:
            return []

        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                schema=[
                    {
                        "type": "select",
                        "name": "Statesman",
                        "options": options,
                    }
                ],
            )
        ]

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, Any],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:

        card = selection["Statesman"]
        statesman_code = card.split(":", 1)[1]
        family_code = _family_code(statesman_code)

        statesmen_dict = _load_statesmen()
        match = next(
            ((k, v) for k, v in statesmen_dict.items() if v["code"] == statesman_code),
            None,
        )
        if not match:
            return ExecutionResult(False, "Unknown statesman.")
        statesman_full_name, statesman_data = match

        faction = Faction.objects.get(game=game_id, id=faction_id)

        # Check for same-faction family senator to upgrade
        family_senator = Senator.objects.filter(
            game=game_id, code=family_code, family=True, alive=True, faction=faction_id
        ).first()

        if family_senator:
            senator = family_senator
            outgoing_display_name = senator.display_name
            # Upgrade existing family senator row to statesman
            senator.code = statesman_code
            senator.statesman_name = statesman_full_name
            senator.military = statesman_data["military"]
            senator.oratory = statesman_data["oratory"]
            senator.loyalty = statesman_data["base_loyalty"]
            senator.influence = max(senator.influence, statesman_data["influence"])
            senator.popularity = max(senator.popularity, statesman_data["popularity"])
            senator.save()
            Log.create_object(
                game_id=game_id,
                text=f"{outgoing_display_name} of {faction.display_name} became known as {senator.display_name}.",
            )
        else:
            # Independent statesman — look up family name from senator.json
            senators_dict = _load_senators()
            family_senator_data = next(
                (v for v in senators_dict.values() if v["code"] == int(family_code)),
                None,
            )
            family_name = (
                next(
                    k for k, v in senators_dict.items() if v["code"] == int(family_code)
                )
                if family_senator_data
                else family_code
            )
            senator = Senator.objects.create(
                game_id=game_id,
                faction=faction,
                family_name=family_name,
                family=False,
                code=statesman_code,
                statesman_name=statesman_full_name,
                military=statesman_data["military"],
                oratory=statesman_data["oratory"],
                loyalty=statesman_data["base_loyalty"],
                influence=statesman_data["influence"],
                popularity=statesman_data["popularity"],
            )
            Log.create_object(
                game_id=game_id,
                text=f"{senator.display_name} appeared in {faction.display_name}.",
            )

        # Remove card from faction hand
        faction.cards.remove(card)
        faction.save()

        return ExecutionResult(True)
