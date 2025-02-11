from typing import List, Type
from rorapp.effects import PersonalRevenueEffect
from rorapp.effects.meta.effect_base import EffectBase


effect_registry: List[Type[EffectBase]] = [
    PersonalRevenueEffect,
]
