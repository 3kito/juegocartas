from dataclasses import dataclass, field
from typing import Iterable

from .movement_behaviors import MovementBehavior
from .combat_behaviors import CombatBehavior


@dataclass
class BehaviorRestrictions:
    movement: list[MovementBehavior] = field(default_factory=list)
    combat: list[CombatBehavior] = field(default_factory=list)

    def permite_movimiento(self, comportamiento: MovementBehavior) -> bool:
        return not self.movement or comportamiento in self.movement

    def permite_combate(self, comportamiento: CombatBehavior) -> bool:
        return not self.combat or comportamiento in self.combat
