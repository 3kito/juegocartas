"""Comportamientos package reorganized."""

from .core.behavior_manager import BehaviorManager
from .legacy.OLD.behavior_executor import BehaviorExecutor
from .legacy.OLD.movement_behaviors import MovementBehavior, MovementProcessor
from .legacy.OLD.combat_behaviors import CombatBehavior, CombatProcessor
from .legacy.OLD.behavior_restrictions import BehaviorRestrictions

__all__ = [
    "BehaviorManager",
    "BehaviorExecutor",
    "MovementBehavior",
    "MovementProcessor",
    "CombatBehavior",
    "CombatProcessor",
    "BehaviorRestrictions",
]
