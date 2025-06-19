from __future__ import annotations

from typing import List, Any

from .behavior_engine import BehaviorEngine

# Map legacy names to new ones
LEGACY_MOVEMENT_MAP = {
    "explorador": "explorador",
    "merodeador": "explorador",
    "seguidor": "explorador",
    "huir": "huir",
    "regreso": "parado",
    "parado": "parado",
    "cazador": "explorador",
}

LEGACY_COMBAT_MAP = {
    "agresivo": "agresivo",
    "defensivo": "defensivo",
    "guardian": "defensivo",
    "ignorar": "ignorar",
}

_engine = BehaviorEngine()


class BehaviorExecutor:
    """Compatibility adapter that mirrors the old interface."""

    def ejecutar(self, carta, tablero) -> List[Any]:
        mov = LEGACY_MOVEMENT_MAP.get(getattr(carta, "movement_behavior", "parado"), "parado")
        com = LEGACY_COMBAT_MAP.get(getattr(carta, "combat_behavior", "ignorar"), "ignorar")
        carta.movement_behavior = mov
        carta.combat_behavior = com
        return _engine.execute(carta, tablero)
