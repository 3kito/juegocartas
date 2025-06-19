from typing import Set
from src.game.board.hex_coordinate import HexCoordinate


def generar_hexagonos_contiguos(origen: HexCoordinate, cantidad: int, disponibles: set = None) -> Set[HexCoordinate]:
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


def generar_hexagono_regular(centro: HexCoordinate, radio: int) -> Set[HexCoordinate]:
    """Genera un conjunto de coordenadas que forman un hexágono regular."""
    return set(centro.obtener_area(radio))
