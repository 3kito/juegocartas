"""Combat executor with basic cooldown usage."""

from .combat_types import CombatType
from ..core.cooldown_system import CooldownSystem


class CombatExecutor:
    def __init__(self, cooldown_system: CooldownSystem | None = None):
        self.cooldowns = cooldown_system or CooldownSystem()

    def attack(self, atacante, objetivo, current_time: float) -> bool:
        if not self.cooldowns.is_ready(atacante, "attack", current_time):
            return False
        # TODO: implement attack resolution
        self.cooldowns.set_cooldown(atacante, "attack", getattr(atacante, "velocidad_ataque", 1), current_time)
        return True
