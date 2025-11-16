from typing import List, Type
from rorapp.effects import *
from rorapp.effects.meta.effect_base import EffectBase


effect_registry: List[Type[EffectBase]] = [
    CombatEndEffect,
    CombatResolutionEffect,
    CombatStartEffect,
    DeployForcesEffect,
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
    RaiseForcesEffect,
    RedistributionDoneEffect,
    RevenueEffect,
    SenateEndEffect,
    SenateStartEffect,
    SponsorGamesAutoSkipEffect,
]
