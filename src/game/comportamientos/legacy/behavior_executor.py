"""Compatibilidad: redirige a BehaviorExecutor basado en JSON."""
from __future__ import annotations

from typing import List, Any

from ..behavior_adapter import BehaviorExecutor as _Adapter

_executor = _Adapter()


class BehaviorExecutor:
    """Mantiene la interfaz original para código legacy."""

    def __init__(self):
        self._engine = _executor

    def ejecutar(self, carta, tablero) -> List[Any]:
        return self._engine.ejecutar(carta, tablero)
