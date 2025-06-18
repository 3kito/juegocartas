from .cooldown_system import CooldownSystem
from .action_validator import ActionValidator


class BehaviorManager:
    """Coordinator for card behaviors using cooldowns and validators."""

    def __init__(self):
        self.cooldown_system = CooldownSystem()
        self.action_validator = ActionValidator()

    def process_card_behaviors(self, carta, tablero, current_time: float):
        if not self.action_validator.can_act(carta, current_time):
            return []
        actions = self._generate_actions(carta, tablero)
        self.cooldown_system.set_cooldown(carta, "act", 0, current_time)
        return actions

    def _generate_actions(self, carta, tablero):
        # Placeholder for real behavior generation
        return []
