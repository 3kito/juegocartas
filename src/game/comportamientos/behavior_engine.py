import json
from pathlib import Path
from typing import Dict, Any, List

from .behavior_primitives import ACTIONS, CONDITIONS
from src.game.combate.ia.ia_utilidades import obtener_info_entorno


class BehaviorEngine:
    """Generic behavior executor driven by JSON configuration."""

    def __init__(self, config_path: str | None = None):
        if config_path is None:
            config_path = Path(__file__).with_name("behaviors_config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            self.config: Dict[str, Any] = json.load(f)

    def execute(self, carta, tablero) -> List[Any]:
        info = obtener_info_entorno(carta, tablero)
        movimientos = self.config.get("movements", {})
        combates = self.config.get("combats", {})

        mov = movimientos.get(getattr(carta, "movement_behavior", "parado"), {})
        self._run_steps(mov.get("steps", []), carta, tablero, info)

        com = combates.get(getattr(carta, "combat_behavior", "ignorar"), {})
        return self._run_steps(com.get("steps", []), carta, tablero, info)

    def _run_steps(self, steps: List[Dict[str, Any]], carta, tablero, info) -> List[Any]:
        resultado: List[Any] = []
        for paso in steps:
            cond_name = paso.get("condition")
            if cond_name:
                cond = CONDITIONS.get(cond_name)
                if cond is None or not cond(carta, tablero, info):
                    continue
            action = ACTIONS.get(paso.get("action"))
            if action:
                res = action(carta, tablero, info)
                if res:
                    resultado.extend(res)
        return resultado
