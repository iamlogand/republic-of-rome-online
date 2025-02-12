from typing import List, Type
from rorapp.effects import RevenueEffect
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.effects import RedistributionDoneEffect


effect_registry: List[Type[EffectBase]] = [
    RevenueEffect,
    RedistributionDoneEffect,
]
