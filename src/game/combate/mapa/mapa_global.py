from typing import Dict, Optional
from src.game.tablero.coordenada import CoordenadaHexagonal
from src.game.tablero.tablero_hexagonal import TableroHexagonal
from src.game.combate.mapa.zona_mapa import ZonaMapa
from src.game.combate.mapa.generador_mapa import GeneradorMapa
from src.game.combate.configuracion_tiempo_real import configurador_tiempo_real
from src.utils.helpers import log_evento


class MapaGlobal:
    def __init__(self, radio: int | None = None, celdas_por_zona: int | None = None, cantidad_parejas: int | None = None):
        if radio is None:
            radio = configurador_tiempo_real.mapas.radio_mapa_global
        if celdas_por_zona is None:
            celdas_por_zona = configurador_tiempo_real.mapas.celdas_por_zona
        if cantidad_parejas is None:
            cantidad_parejas = configurador_tiempo_real.mapas.cantidad_parejas

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

        cartas_pendientes = [
            (coord, carta)
            for coord, carta in jugador.tablero.celdas.items()
            if carta is not None
        ]

        cartas_colocadas = 0
        for zona in zonas:
            if not cartas_pendientes:
                break
            nuevas_pendientes = []
            for coord_local, carta in cartas_pendientes:
                coord_global = zona.convertir_a_global(coord_local)
                if coord_global in zona.coordenadas and self.tablero.esta_vacia(coord_global):
                    carta.coordenada = coord_global
                    self.tablero.colocar_carta(coord_global, carta)
                    log_evento(f"   📍 {carta.nombre} colocada en {coord_global}")
                    cartas_colocadas += 1
                else:
                    nuevas_pendientes.append((coord_local, carta))

            cartas_pendientes = nuevas_pendientes

        if cartas_colocadas == 0:
            log_evento(f"   ⚠️ {jugador.nombre} no tiene cartas para colocar")
        else:
            log_evento(f"   ✅ {cartas_colocadas} carta(s) colocada(s) para {jugador.nombre}")
