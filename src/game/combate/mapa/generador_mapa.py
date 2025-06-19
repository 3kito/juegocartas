from .zona_mapa import ZonaMapa
from .utilidades_mapa import generar_hexagono_regular
from src.game.board.hex_coordinate import HexCoordinate
from src.game.combate.configuracion_tiempo_real import configurador_tiempo_real
import random

class GeneradorMapa:
    def __init__(self, tablero, celdas_por_zona: int = 19, cantidad_parejas: int = 3,
                 separacion_parejas: int = 1, separacion_misma_pareja: int = 2):
        self.tablero = tablero
        self.celdas_por_zona = celdas_por_zona
        self.cantidad_parejas = cantidad_parejas
        self.separacion_parejas = separacion_parejas
        self.separacion_misma_pareja = separacion_misma_pareja
        self.radio_zona = configurador_tiempo_real.mapas.radio_mapa_individual
        self.zonas_rojas = []
        self.zonas_azules = []

    def _hex_cabe(self, centro: HexCoordinate) -> bool:
        for c in centro.obtener_area(self.radio_zona):
            if c not in self.tablero.celdas:
                return False
        return True

    def _centro_valido(self, centro: HexCoordinate, zonas_existentes: list[ZonaMapa], separacion: int) -> bool:
        if not self._hex_cabe(centro):
            return False
        for zona in zonas_existentes:
            if centro.distancia_a(zona.centro) < (2 * self.radio_zona + separacion):
                return False
        return True

    def _obtener_centro_random(self, zonas_existentes: list[ZonaMapa], separacion: int) -> HexCoordinate | None:
        candidatos = list(self.tablero.celdas.keys())
        random.shuffle(candidatos)
        for cand in candidatos:
            if self._centro_valido(cand, zonas_existentes, separacion):
                return cand
        return None

    def generar(self):
        zonas_creadas: list[ZonaMapa] = []

        for pareja_id in range(self.cantidad_parejas):
            centro_rojo = self._obtener_centro_random(zonas_creadas, self.separacion_parejas)
            if centro_rojo is None:
                break

            coords_rojas = generar_hexagono_regular(centro_rojo, self.radio_zona)
            zona_roja = ZonaMapa("rojo", coords_rojas, pareja_id=pareja_id, centro=centro_rojo)
            self.zonas_rojas.append(zona_roja)
            zonas_creadas.append(zona_roja)

            centro_azul = self._obtener_centro_random(zonas_creadas, self.separacion_misma_pareja)
            if centro_azul is None:
                break

            coords_azules = generar_hexagono_regular(centro_azul, self.radio_zona)
            zona_azul = ZonaMapa("azul", coords_azules, pareja_id=pareja_id, centro=centro_azul)
            self.zonas_azules.append(zona_azul)
            zonas_creadas.append(zona_azul)
