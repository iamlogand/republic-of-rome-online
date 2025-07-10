from typing import List, Type
from rorapp.effects import *
from rorapp.effects.meta.effect_base import EffectBase


effect_registry: List[Type[EffectBase]] = [
    ElectConsulsResult,
    InitialPhaseDoneEffect,
    InitiativeAuctionAutoPayEffect,
    InitiativeAuctionAutoSkipEffect,
    InitiativeAuctionFirstEffect,
    InitiativeAuctionNextEffect,
    InitiativeFirstEffect,
    InitiativeNextEffect,
    InitiativeRollEffect,
    CombatPhaseEndEffect,
    MortalityEffect,
    PopulationEffect,
    PreferredConsularOfficesEffect,
    RevenueEffect,
    RedistributionDoneEffect,
    SenatePhaseStartEffect,
    SponsorGamesAutoSkipEffect,
]
