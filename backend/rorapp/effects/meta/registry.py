from typing import List, Type
from rorapp.effects import *
from rorapp.effects.meta.effect_base import EffectBase


effect_registry: List[Type[EffectBase]] = [
    # High priority
    GameOverStateBankruptcyEffect,
    GameOverMilitaryOverwhelmedEffect,
    # Standard priority
    CombatEndEffect,
    CombatResolutionEffect,
    CombatStartEffect,
    ElectConsulsEffect,
    InitialPhaseDoneEffect,
    InitiativeAuctionAutoPayEffect,
    InitiativeAuctionAutoSkipEffect,
    InitiativeAuctionFirstEffect,
    InitiativeAuctionNextEffect,
    InitiativeFirstEffect,
    InitiativeNextEffect,
    InitiativeRollEffect,
    MortalityEffect,
    PopulationEffect,
    PreferredAttackerEffect,
    PreferredConsularOfficesEffect,
    ProposalDeployForcesEffect,
    ProposalRaiseForcesEffect,
    ProposalRecallForcesEffect,
    ProposalReinforceProconsulEffect,
    ProposalReplaceProconsulEffect,
    RedistributionDoneEffect,
    RevenueEffect,
    SenateEndEffect,
    SenateStartEffect,
    SponsorGamesAutoSkipEffect,
]
