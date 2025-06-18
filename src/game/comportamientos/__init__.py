"""Comportamientos package reorganized."""

from .core.behavior_manager import BehaviorManager
from .legacy.behavior_executor import BehaviorExecutor
from .legacy.movement_behaviors import MovementBehavior, MovementProcessor
from .legacy.combat_behaviors import CombatBehavior, CombatProcessor
from .legacy.behavior_restrictions import BehaviorRestrictions

__all__ = [
    "BehaviorManager",
    "BehaviorExecutor",
    "MovementBehavior",
    "MovementProcessor",
    "CombatBehavior",
    "CombatProcessor",
    "BehaviorRestrictions",
]
