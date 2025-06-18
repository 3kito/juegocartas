from enum import Enum
from typing import Optional

from .behavior_component import BehaviorComponent
from src.game.combate.ia.ia_utilidades import mover_carta_con_pathfinding


class MovementBehavior(Enum):
    EXPLORADOR = "explorador"
    MERODEADOR = "merodeador"
    SEGUIDOR = "seguidor"
    HUIR = "huir"
    REGRESO = "regreso"
    PARADO = "parado"
    CAZADOR = "cazador"


class MovementProcessor(BehaviorComponent):
    """Procesador genérico para comportamientos de movimiento."""

    def __init__(self, tipo: MovementBehavior):
        self.tipo = tipo

    def ejecutar(self, carta, tablero, info_entorno) -> Optional[object]:
        if self.tipo == MovementBehavior.PARADO:
            return None
        if self.tipo == MovementBehavior.REGRESO:
            destino = getattr(carta, "zona_base", None)
            if destino:
                mover_carta_con_pathfinding(carta, destino, tablero)
            return None
        enemigos = info_entorno.get("enemigos_en_rango", [])
        aliados = info_entorno.get("aliados", [])
        if self.tipo == MovementBehavior.HUIR and enemigos:
            # Moverse a la coordenada vecina más alejada del primer enemigo
            from src.game.tablero.coordenada import CoordenadaHexagonal

            origen = tablero.obtener_coordenada_de(carta)
            if origen and enemigos[0].coordenada:
                vecinos = [v for v in origen.vecinos() if tablero.esta_vacia(v)]
                if vecinos:
                    vecinos.sort(
                        key=lambda c: c.distancia(enemigos[0].coordenada),
                        reverse=True,
                    )
                    mover_carta_con_pathfinding(carta, vecinos[0], tablero)
            return None
        if self.tipo == MovementBehavior.SEGUIDOR:
            if aliados:
                aliado = aliados[0]
                if aliado.coordenada:
                    mover_carta_con_pathfinding(carta, aliado.coordenada, tablero)
            return None
        if self.tipo in {MovementBehavior.EXPLORADOR, MovementBehavior.CAZADOR}:
            origen = tablero.obtener_coordenada_de(carta)
            if not origen:
                return None
            for vec in origen.vecinos():
                if tablero.esta_vacia(vec):
                    mover_carta_con_pathfinding(carta, vec, tablero)
                    break
            return None
        if self.tipo == MovementBehavior.MERODEADOR:
            base = getattr(carta, "zona_base", None)
            if base:
                mover_carta_con_pathfinding(carta, base, tablero)
            return None
        return None
