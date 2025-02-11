from typing import List, Type
from rorapp.effects import PersonalRevenueEffect
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.effects import RedistributionDoneEffect


effect_registry: List[Type[EffectBase]] = [
    PersonalRevenueEffect,
    RedistributionDoneEffect,
]
