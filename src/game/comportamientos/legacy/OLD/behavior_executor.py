from __future__ import annotations

from typing import List

from src.game.combate.ia.ia_utilidades import obtener_info_entorno
from src.game.combate.interacciones.interaccion_modelo import Interaccion
from .movement_behaviors import MovementBehavior, MovementProcessor
from .combat_behaviors import CombatBehavior, CombatProcessor


class BehaviorExecutor:
    """Coordinador de comportamientos de movimiento y combate."""

    def __init__(self):
        self._cache_mov = {}
        self._cache_com = {}

    def _get_movement_processor(self, movimiento: MovementBehavior) -> MovementProcessor:
        if movimiento not in self._cache_mov:
            self._cache_mov[movimiento] = MovementProcessor(movimiento)
        return self._cache_mov[movimiento]

    def _get_combat_processor(self, combate: CombatBehavior) -> CombatProcessor:
        if combate not in self._cache_com:
            self._cache_com[combate] = CombatProcessor(combate)
        return self._cache_com[combate]

    def ejecutar(self, carta, tablero) -> List[Interaccion]:
        info_entorno = obtener_info_entorno(carta, tablero)
        mov_tipo = getattr(carta, "movement_behavior", MovementBehavior.PARADO)
        com_tipo = getattr(carta, "combat_behavior", CombatBehavior.IGNORAR)
        mov_proc = self._get_movement_processor(MovementBehavior(mov_tipo))
        com_proc = self._get_combat_processor(CombatBehavior(com_tipo))

        mov_proc.ejecutar(carta, tablero, info_entorno)
        interacciones = com_proc.ejecutar(carta, tablero, info_entorno)
        return interacciones
