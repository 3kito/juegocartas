from typing import Set, Optional
from src.game.tablero.coordenada import CoordenadaHexagonal
from src.utils.helpers import log_evento


class ZonaMapa:
    def __init__(self, color: str, coordenadas: set, pareja_id: int, centro: CoordenadaHexagonal):
        self.color = color
        self.coordenadas = coordenadas
        self.pareja_id = pareja_id
        self.centro = centro

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

    def convertir_a_global(self, coord_local: CoordenadaHexagonal) -> CoordenadaHexagonal:
        """Convierte una coordenada local (tablero individual) a coord. global en esta zona."""
        coord_global = CoordenadaHexagonal(
            self.centro.q + coord_local.q, self.centro.r + coord_local.r
        )
        log_evento(
            f"ZONA {self.color.upper()} centro: {self.centro} | local {coord_local} → global {coord_global}",
            "DEBUG",
        )
        return coord_global

