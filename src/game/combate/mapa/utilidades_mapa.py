from typing import Set
from src.game.tablero.coordenada import CoordenadaHexagonal


def generar_hexagonos_contiguos(origen: CoordenadaHexagonal, cantidad: int, disponibles: set = None) -> Set[CoordenadaHexagonal]:
    seleccionadas = {origen}
    frontera = [origen]

    while len(seleccionadas) < cantidad and frontera:
        actual = frontera.pop()
        vecinos = actual.vecinos()

        for vecino in vecinos:
            if vecino in seleccionadas:
                continue
            if disponibles and vecino not in disponibles:
                continue
            seleccionadas.add(vecino)
            frontera.append(vecino)

    return seleccionadas


def generar_hexagono_regular(centro: CoordenadaHexagonal, radio: int) -> Set[CoordenadaHexagonal]:
    """Genera un conjunto de coordenadas que forman un hexágono regular."""
    return set(centro.obtener_area(radio))
