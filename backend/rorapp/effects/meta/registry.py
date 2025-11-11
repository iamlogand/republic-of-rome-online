from typing import List, Type
from rorapp.effects import *
from rorapp.effects.meta.effect_base import EffectBase


effect_registry: List[Type[EffectBase]] = [
    CombatEffect,
    ElectConsulsEffect,
    InitialPhaseDoneEffect,
    InitiativeAuctionAutoPayEffect,
    InitiativeAuctionAutoSkipEffect,
    InitiativeAuctionFirstEffect,
    InitiativeAuctionNextEffect,
    InitiativeFirstEffect,
    InitiativeNextEffect,
    InitiativeRollEffect,
    DeployForcesEffect,
    MortalityEffect,
    PopulationEffect,
    PreferredAttackerEffect,
    PreferredConsularOfficesEffect,
    RaiseForcesEffect,
    RevenueEffect,
    RedistributionDoneEffect,
    SenatePhaseStartEffect,
    SponsorGamesAutoSkipEffect,
]
