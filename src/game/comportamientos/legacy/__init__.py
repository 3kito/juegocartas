"""Compatibilidad con el antiguo sistema de comportamientos."""

from .behavior_executor import BehaviorExecutor
from .movement_behaviors import MovementBehavior, MovementProcessor
from .combat_behaviors import CombatBehavior, CombatProcessor
from .behavior_restrictions import BehaviorRestrictions

__all__ = [
    "BehaviorExecutor",
    "MovementBehavior",
    "MovementProcessor",
    "CombatBehavior",
    "CombatProcessor",
    "BehaviorRestrictions",
]
