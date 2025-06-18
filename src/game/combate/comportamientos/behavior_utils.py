from typing import Optional

from src.game.tablero.coordenada import CoordenadaHexagonal


def calcular_zona_base(carta) -> Optional[CoordenadaHexagonal]:
    return getattr(carta.duenio, "zona_base", None)


def calcular_vision(carta, mapa_global):
    if not mapa_global:
        return set()
    from src.game.combate.ia.ia_utilidades import calcular_vision_jugador

    return calcular_vision_jugador(carta.duenio, mapa_global)
