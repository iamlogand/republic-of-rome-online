from typing import List, Type
from rorapp.effects import *
from rorapp.effects.meta.effect_base import EffectBase


effect_registry: List[Type[EffectBase]] = [
    ElectConsulsEffect,
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
    RaiseForcesEffect,
    RevenueEffect,
    RedistributionDoneEffect,
    SenatePhaseStartEffect,
    SponsorGamesAutoSkipEffect,
]
