from typing import Dict, Any
from .behavior_primitives import ACTIONS, CONDITIONS


class BehaviorValidator:
    """Validates behavior configuration."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def validate(self) -> bool:
        for group in ("movements", "combats"):
            behaviors = self.config.get(group, {})
            for name, data in behaviors.items():
                if not isinstance(data, dict):
                    raise ValueError(f"Behavior {name} debe ser un objeto")
                for step in data.get("steps", []):
                    cond = step.get("condition")
                    if cond and cond not in CONDITIONS:
                        raise ValueError(f"Condicion desconocida: {cond}")
                    action = step.get("action")
                    if action not in ACTIONS:
                        raise ValueError(f"Accion desconocida: {action}")
        return True
