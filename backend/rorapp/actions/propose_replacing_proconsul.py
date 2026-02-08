from typing import Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import (
    AvailableAction,
    Campaign,
    Faction,
    Game,
    Log,
    Senator,
)


class ProposeReplacingProconsulAction(ActionBase):
    NAME = "Propose replacing proconsul"
    POSITION = 4

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.OTHER_BUSINESS
            and (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
            and any(
                s
                for s in game_state.senators
                if s.faction
                and s.faction.id == faction.id
                and s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
            )
        ):
            # Check if there are campaigns with commanders that can be replaced
            replaceable_campaigns = [
                c
                for c in game_state.campaigns
                if c.commander is not None
                and not c.recently_deployed
                and not c.recently_reinforced
            ]
            if not replaceable_campaigns:
                return None

            # Check if there are available commanders
            available_commanders = [
                s
                for s in game_state.senators
                if s.faction
                and s.alive
                and s.location == "Rome"
                and (
                    s.has_title(Senator.Title.ROME_CONSUL)
                    or s.has_title(Senator.Title.FIELD_CONSUL)
                )
            ]
            if available_commanders:
                return faction

        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if faction:
            replaceable_campaigns = sorted(
                [
                    c
                    for c in snapshot.campaigns
                    if c.commander is not None
                    and not c.recently_deployed
                    and not c.recently_reinforced
                ],
                key=lambda c: c.id,
            )

            available_commanders = sorted(
                [
                    s
                    for s in snapshot.senators
                    if s.faction
                    and s.alive
                    and s.location == "Rome"
                    and (
                        s.has_title(Senator.Title.ROME_CONSUL)
                        or s.has_title(Senator.Title.FIELD_CONSUL)
                    )
                ],
                key=lambda s: s.name,
            )

            # Rome Consul can only be deployed if field consul has already been deployed
            field_consuls = [
                s
                for s in available_commanders
                if s.has_title(Senator.Title.FIELD_CONSUL)
            ]
            field_consul = field_consuls[0] if len(field_consuls) == 1 else None
            if field_consul and field_consul.location == "Rome":
                available_commanders = [
                    s
                    for s in available_commanders
                    if not s.has_title(Senator.Title.ROME_CONSUL)
                ]

            return [
                AvailableAction.objects.create(
                    game=snapshot.game,
                    faction=faction,
                    base_name=self.NAME,
                    position=self.POSITION,
                    schema=[
                        {
                            "type": "select",
                            "name": "Campaign",
                            "options": [
                                {
                                    "value": c.id,
                                    "object_class": "campaign",
                                    "id": c.id,
                                }
                                for c in replaceable_campaigns
                            ],
                        },
                        {
                            "type": "select",
                            "name": "Replacement commander",
                            "options": [
                                {
                                    "value": s.id,
                                    "object_class": "senator",
                                    "id": s.id,
                                }
                                for s in available_commanders
                            ],
                        },
                    ],
                )
            ]
        return []

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, str],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:

        game = Game.objects.get(id=game_id)
        faction = Faction.objects.get(game=game_id, id=faction_id)

        # Retrieve and validate campaign
        campaign_id = int(selection["Campaign"])
        campaign = (
            Campaign.objects.select_related("commander", "war")
            .prefetch_related("legions", "fleets")
            .get(game=game, id=campaign_id)
        )

        # Check campaign has a commander
        if campaign.commander is None:
            return ExecutionResult(
                False, "Cannot replace commander of a campaign without a commander."
            )

        # Check campaign wasn't recently deployed
        if campaign.recently_deployed:
            return ExecutionResult(
                False,
                "Cannot replace commander of a campaign that was deployed this turn.",
            )

        # Check campaign wasn't recently reinforced
        if campaign.recently_reinforced:
            return ExecutionResult(
                False,
                "Cannot replace commander of a campaign that was reinforced this turn.",
            )

        # Retrieve and validate replacement commander
        replacement_commander_id = selection["Replacement commander"]
        replacement_commander = Senator.objects.get(
            game=game, id=replacement_commander_id
        )

        # Check replacement commander is available
        available_commanders = [
            s
            for s in Senator.objects.filter(
                game=game, alive=True, faction__isnull=False
            )
            if s.location == "Rome"
            and (
                s.has_title(Senator.Title.ROME_CONSUL)
                or s.has_title(Senator.Title.FIELD_CONSUL)
            )
        ]

        # Rome Consul can only be deployed if field consul has already been deployed
        field_consuls = [
            s for s in available_commanders if s.has_title(Senator.Title.FIELD_CONSUL)
        ]
        field_consul = field_consuls[0] if len(field_consuls) == 1 else None
        if field_consul and field_consul.location == "Rome":
            available_commanders = [
                s
                for s in available_commanders
                if not s.has_title(Senator.Title.ROME_CONSUL)
            ]

        if replacement_commander.id not in [c.id for c in available_commanders]:
            return ExecutionResult(False, "Invalid replacement commander selected.")

        current_commander = campaign.commander
        war = campaign.war

        # Determine proposal
        proposal = f"Replace {current_commander.display_name} with {replacement_commander.display_name} in the {war.name}"

        # Validate proposal
        if proposal in game.defeated_proposals:
            return ExecutionResult(False, "This proposal was previously rejected")

        # Set current proposal
        game.current_proposal = proposal
        game.save()

        # Create log
        presiding_magistrate = [
            s
            for s in faction.senators.all()
            if s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
        ][0]
        Log.create_object(
            game_id,
            f"{presiding_magistrate.display_name} proposed the motion: {game.current_proposal}.",
        )

        return ExecutionResult(True)
