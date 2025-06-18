"""Compatibilidad con el antiguo sistema de comportamientos."""

from .OLD.behavior_executor import BehaviorExecutor
from .OLD.movement_behaviors import MovementBehavior, MovementProcessor
from .OLD.combat_behaviors import CombatBehavior, CombatProcessor
from .OLD.behavior_restrictions import BehaviorRestrictions

__all__ = [
    "BehaviorExecutor",
    "MovementBehavior",
    "MovementProcessor",
    "CombatBehavior",
    "CombatProcessor",
    "BehaviorRestrictions",
]
