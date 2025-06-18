from enum import Enum
from typing import Optional

from .behavior_component import BehaviorComponent
from src.utils.helpers import log_evento


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
        if (
            carta.tiene_orden_manual()
            or carta.tiene_orden_simulada()
            or carta.tiene_evento_activo("movimiento")
        ):
            log_evento(
                f"⏳ {carta.nombre} omite nueva orden de movimiento (en curso)",
                "DEBUG",
            )
            return None

        destino = None
        if self.tipo == MovementBehavior.PARADO:
            return None
        if self.tipo == MovementBehavior.REGRESO:
            destino = getattr(carta, "zona_base", None)
        else:
            enemigos = info_entorno.get("enemigos_en_rango", [])
            aliados = info_entorno.get("aliados", [])
            origen = tablero.obtener_coordenada_de(carta)

            if self.tipo == MovementBehavior.HUIR and enemigos:
                if origen and enemigos[0].coordenada:
                    vecinos = [v for v in origen.vecinos() if tablero.esta_vacia(v)]
                    if vecinos:
                        vecinos.sort(key=lambda c: c.distancia(enemigos[0].coordenada), reverse=True)
                        destino = vecinos[0]
            elif self.tipo == MovementBehavior.SEGUIDOR and aliados:
                aliado = aliados[0]
                if aliado.coordenada:
                    destino = aliado.coordenada
            elif self.tipo in {MovementBehavior.EXPLORADOR, MovementBehavior.CAZADOR}:
                if origen:
                    for vec in origen.vecinos():
                        if tablero.esta_vacia(vec):
                            destino = vec
                            break
            elif self.tipo == MovementBehavior.MERODEADOR:
                base = getattr(carta, "zona_base", None)
                if base:
                    destino = base

        if destino is not None:
            log_evento(
                f"📍 {carta.nombre} determina destino {destino}",
                "DEBUG",
            )
            carta.marcar_orden_simulada("mover", destino)
            log_evento(
                f"🤖 [SimOrden] {carta.nombre} genera movimiento a {destino}",
                "DEBUG",
            )
        else:
            log_evento(
                f"❌ {carta.nombre} no encuentra destino para {self.tipo.value}",
                "DEBUG",
            )
        return None
