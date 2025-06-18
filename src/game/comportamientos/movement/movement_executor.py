"""Movement executor that respects cooldowns."""

from .movement_types import MovementType
from ..core.cooldown_system import CooldownSystem


class MovementExecutor:
    def __init__(self, cooldown_system: CooldownSystem | None = None):
        self.cooldowns = cooldown_system or CooldownSystem()

    def move(self, carta, destino, tablero, current_time: float):
        if not self.cooldowns.is_ready(carta, "move", current_time):
            return False
        # TODO: integrate pathfinding and movement logic
        self.cooldowns.set_cooldown(carta, "move", getattr(carta, "velocidad_movimiento", 1), current_time)
        return True
