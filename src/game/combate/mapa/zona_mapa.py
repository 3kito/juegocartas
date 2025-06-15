from typing import Set, Optional
from src.game.tablero.coordenada import CoordenadaHexagonal


class ZonaMapa:
    def __init__(self, color: str, coordenadas: set, pareja_id: int):
        self.color = color
        self.coordenadas = coordenadas
        self.pareja_id = pareja_id

    def esta_cerca_de(self, otra: 'ZonaMapa', umbral: int = 4) -> bool:
        for coord1 in self.coordenadas:
            for coord2 in otra.coordenadas:
                if coord1.distancia_a(coord2) <= umbral:
                    return True
        return False

    def obtener_coordenada_libre(self, tablero) -> Optional[CoordenadaHexagonal]:
        for coord in self.coordenadas:
            if tablero.esta_vacia(coord):
                return coord
        return None

