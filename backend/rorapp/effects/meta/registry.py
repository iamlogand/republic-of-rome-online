from typing import List, Type
from rorapp.effects import *
from rorapp.effects.meta.effect_base import EffectBase


effect_registry: List[Type[EffectBase]] = [
    InitiativeFirstEffect,
    InitiativeNextEffect,
    InitialPhaseDoneEffect,
    MortalityEffect,
    RevenueEffect,
    RedistributionDoneEffect,
    SponsorGamesAutoSkipEffect,
]
