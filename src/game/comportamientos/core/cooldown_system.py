class CooldownSystem:
    """Simple cooldown tracker for game entities."""

    def __init__(self):
        self._cooldowns = {}

    def is_ready(self, entity, action_name: str, current_time: float) -> bool:
        key = (id(entity), action_name)
        return current_time >= self._cooldowns.get(key, 0)

    def set_cooldown(self, entity, action_name: str, cooldown: float, current_time: float) -> None:
        key = (id(entity), action_name)
        self._cooldowns[key] = current_time + cooldown
