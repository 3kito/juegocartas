from typing import Dict, Optional
from src.game.tablero.coordenada import CoordenadaHexagonal
from src.game.tablero.tablero_hexagonal import TableroHexagonal
from src.game.combate.mapa.zona_mapa import ZonaMapa
from src.game.combate.mapa.generador_mapa import GeneradorMapa
from src.utils.helpers import log_evento


class MapaGlobal:
    def __init__(self, radio: int = 4, celdas_por_zona: int = 19, cantidad_parejas: int = 3):
        self.tablero = TableroHexagonal(radio=radio)
        self.celdas: Dict[CoordenadaHexagonal, Optional[object]] = self.tablero.celdas
        self.zonas_rojas: list[ZonaMapa] = []
        self.zonas_azules: list[ZonaMapa] = []
        self._generar_zonas(celdas_por_zona, cantidad_parejas)

    def _generar_zonas(self, celdas_por_zona: int, cantidad_parejas: int):
        generador = GeneradorMapa(self.tablero, celdas_por_zona=celdas_por_zona, cantidad_parejas=cantidad_parejas)
        generador.generar()
        self.zonas_rojas = generador.zonas_rojas
        self.zonas_azules = generador.zonas_azules

    def obtener_color_en(self, coord: CoordenadaHexagonal) -> Optional[str]:
        for zona in self.zonas_rojas:
            if coord in zona.coordenadas:
                return "rojo"
        for zona in self.zonas_azules:
            if coord in zona.coordenadas:
                return "azul"
        return None

    # En src/game/combate/mapa/mapa_global.py - método ubicar_jugador_en_zona()
    def ubicar_jugador_en_zona(self, jugador, color: str):
        zonas = self.zonas_rojas if color == "rojo" else self.zonas_azules
        log_evento(f"🗺️ Ubicando {jugador.nombre} en zona {color.upper()}")

        cartas_colocadas = 0
        for zona in zonas:
            cartas_restantes = [c for c in jugador.cartas_banco if c.coordenada is None]
            for carta in cartas_restantes:
                coord = zona.obtener_coordenada_libre(self.tablero)
                if coord:
                    carta.coordenada = coord
                    self.tablero.colocar_carta(coord, carta)
                    log_evento(f"   📍 {carta.nombre} colocada en {coord}")
                    cartas_colocadas += 1
                else:
                    break

        if cartas_colocadas == 0:
            log_evento(f"   ⚠️ {jugador.nombre} no tiene cartas para colocar")
        else:
            log_evento(f"   ✅ {cartas_colocadas} carta(s) colocada(s) para {jugador.nombre}")
