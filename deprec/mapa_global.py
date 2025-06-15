"""
Mapa global de combate con zonas rojas/azules y sistema hexagonal
"""

import random
from typing import List, Dict, Optional, Tuple, Set
from src.game.tablero.tablero_hexagonal import Coordenada, TableroHexagonal
from src.utils.helpers import log_evento


class ZonaCombate:
    """Representa una zona de combate (roja o azul) en el mapa global"""

    def __init__(self, color: str, coordenadas: List[Coordenada]):
        self.color = color  # "roja" o "azul"
        self.coordenadas = coordenadas
        self.ocupada = False
        self.jugador_asignado = None
        self.tablero_colocado: Optional[TableroHexagonal] = None

    def puede_colocar_tablero(self) -> bool:
        """Verifica si se puede colocar un tablero en esta zona"""
        return not self.ocupada and len(self.coordenadas) >= 19

    def colocar_tablero(self, jugador_id: int, tablero: TableroHexagonal) -> bool:
        """Coloca un tablero de jugador en esta zona"""
        if not self.puede_colocar_tablero():
            return False

        self.ocupada = True
        self.jugador_asignado = jugador_id
        self.tablero_colocado = tablero

        log_evento(f"📍 Tablero del Jugador {jugador_id} colocado en zona {self.color}")
        return True

    def liberar_zona(self):
        """Libera la zona al final del combate"""
        self.ocupada = False
        self.jugador_asignado = None
        self.tablero_colocado = None

    def obtener_centro(self) -> Coordenada:
        """Calcula el centro aproximado de la zona"""
        if not self.coordenadas:
            return Coordenada(0, 0)

        suma_q = sum(coord.q for coord in self.coordenadas)
        suma_r = sum(coord.r for coord in self.coordenadas)

        promedio_q = suma_q // len(self.coordenadas)
        promedio_r = suma_r // len(self.coordenadas)

        return Coordenada(promedio_q, promedio_r)

    def __str__(self):
        estado = "OCUPADA" if self.ocupada else "LIBRE"
        return f"Zona {self.color} ({estado}, {len(self.coordenadas)} celdas)"


class MapaGlobal:
    """Mapa hexagonal global para combate con zonas rojas y azules"""

    def __init__(self, tamaño: int = 15):
        self.tamaño = tamaño
        self.celdas: Dict[Coordenada, Optional[any]] = {}
        self.zonas_rojas: List[ZonaCombate] = []
        self.zonas_azules: List[ZonaCombate] = []
        self.jugadores_posicionados: Dict[int, ZonaCombate] = {}

        # Configuración
        self.num_zonas_por_color = 8
        self.tamaño_zona = 19  # Celdas por zona (igual que tablero individual)

        # Generar mapa
        self._generar_mapa_base()
        self._crear_zonas_combate()

    def _generar_mapa_base(self):
        """Genera el mapa hexagonal base"""
        centro = Coordenada(0, 0)

        # Generar todas las coordenadas dentro del radio
        for q in range(-self.tamaño, self.tamaño + 1):
            r1 = max(-self.tamaño, -q - self.tamaño)
            r2 = min(self.tamaño, -q + self.tamaño)
            for r in range(r1, r2 + 1):
                coord = Coordenada(q, r)
                self.celdas[coord] = None  # Inicialmente vacías

        total_celdas = len(self.celdas)
        log_evento(f"🗺️ Mapa global generado: {total_celdas} celdas (radio {self.tamaño})")

    def _crear_zonas_combate(self):
        """Crea las zonas rojas y azules distribuidas en el mapa"""
        coordenadas_disponibles = list(self.celdas.keys())
        random.shuffle(coordenadas_disponibles)

        # Crear zonas rojas
        for i in range(self.num_zonas_por_color):
            zona_coords = self._seleccionar_coordenadas_zona(coordenadas_disponibles)
            if len(zona_coords) >= self.tamaño_zona:
                zona = ZonaCombate("roja", zona_coords[:self.tamaño_zona])
                self.zonas_rojas.append(zona)
                # Remover coordenadas usadas
                for coord in zona_coords[:self.tamaño_zona]:
                    coordenadas_disponibles.remove(coord)

        # Crear zonas azules
        for i in range(self.num_zonas_por_color):
            zona_coords = self._seleccionar_coordenadas_zona(coordenadas_disponibles)
            if len(zona_coords) >= self.tamaño_zona:
                zona = ZonaCombate("azul", zona_coords[:self.tamaño_zona])
                self.zonas_azules.append(zona)
                # Remover coordenadas usadas
                for coord in zona_coords[:self.tamaño_zona]:
                    coordenadas_disponibles.remove(coord)

        log_evento(f"🔴 Creadas {len(self.zonas_rojas)} zonas rojas")
        log_evento(f"🔵 Creadas {len(self.zonas_azules)} zonas azules")

    def _seleccionar_coordenadas_zona(self, disponibles: List[Coordenada]) -> List[Coordenada]:
        """Selecciona coordenadas para formar una zona compacta"""
        if not disponibles:
            return []

        # Tomar punto inicial aleatorio
        inicio = random.choice(disponibles)
        zona_coords = [inicio]

        # Expandir alrededor del punto inicial
        while len(zona_coords) < self.tamaño_zona and disponibles:
            # Buscar coordenadas adyacentes a las ya seleccionadas
            candidatos = []
            for coord_zona in zona_coords:
                for vecino in coord_zona.obtener_vecinos():
                    if vecino in disponibles and vecino not in zona_coords:
                        candidatos.append(vecino)

            if candidatos:
                # Elegir candidato aleatorio
                siguiente = random.choice(candidatos)
                zona_coords.append(siguiente)
            else:
                # Si no hay adyacentes, tomar cualquier disponible
                restantes = [c for c in disponibles if c not in zona_coords]
                if restantes:
                    zona_coords.append(random.choice(restantes))
                else:
                    break

        return zona_coords

    def obtener_zona_libre(self, color: str) -> Optional[ZonaCombate]:
        """Obtiene una zona libre del color especificado"""
        zonas = self.zonas_rojas if color == "roja" else self.zonas_azules

        for zona in zonas:
            if zona.puede_colocar_tablero():
                return zona

        return None

    def asignar_jugador_a_zona(self, jugador_id: int, color: str, tablero: TableroHexagonal) -> bool:
        """Asigna un jugador a una zona libre del color especificado"""
        zona = self.obtener_zona_libre(color)

        if zona and zona.colocar_tablero(jugador_id, tablero):
            self.jugadores_posicionados[jugador_id] = zona
            return True

        return False

    def obtener_zona_jugador(self, jugador_id: int) -> Optional[ZonaCombate]:
        """Obtiene la zona donde está posicionado un jugador"""
        return self.jugadores_posicionados.get(jugador_id)

    def obtener_posicion_carta_en_mapa(self, jugador_id: int, coord_tablero: Coordenada) -> Optional[Coordenada]:
        """Convierte coordenada de tablero individual a coordenada del mapa global"""
        zona = self.obtener_zona_jugador(jugador_id)
        if not zona or not zona.tablero_colocado:
            return None

        # Mapear coordenada del tablero a coordenada del mapa
        # Por simplicidad, usar las primeras 19 coordenadas de la zona
        if coord_tablero in zona.tablero_colocado.celdas:
            # Encontrar índice de la coordenada en el tablero
            coordenadas_tablero = list(zona.tablero_colocado.celdas.keys())
            try:
                indice = coordenadas_tablero.index(coord_tablero)
                if indice < len(zona.coordenadas):
                    return zona.coordenadas[indice]
            except ValueError:
                pass

        return None

    def obtener_carta_en_posicion(self, coord_mapa: Coordenada):
        """Obtiene la carta en una posición específica del mapa"""
        # Buscar en todas las zonas ocupadas
        for jugador_id, zona in self.jugadores_posicionados.items():
            if zona.tablero_colocado:
                # Convertir coordenada de mapa a coordenada de tablero
                try:
                    indice = zona.coordenadas.index(coord_mapa)
                    coordenadas_tablero = list(zona.tablero_colocado.celdas.keys())
                    if indice < len(coordenadas_tablero):
                        coord_tablero = coordenadas_tablero[indice]
                        return zona.tablero_colocado.obtener_carta_en(coord_tablero)
                except (ValueError, IndexError):
                    continue

        return None

    def obtener_jugadores_activos(self, color: str) -> List[int]:
        """Obtiene lista de jugadores del color especificado"""
        jugadores = []

        for jugador_id, zona in self.jugadores_posicionados.items():
            if zona.color == color:
                jugadores.append(jugador_id)

        return jugadores

    def limpiar_mapa(self):
        """Limpia el mapa al final de la ronda de combate"""
        for zona in self.zonas_rojas + self.zonas_azules:
            zona.liberar_zona()

        self.jugadores_posicionados.clear()
        log_evento("🧹 Mapa global limpiado")

    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas del mapa"""
        return {
            'total_celdas': len(self.celdas),
            'zonas_rojas': len(self.zonas_rojas),
            'zonas_azules': len(self.zonas_azules),
            'zonas_rojas_ocupadas': sum(1 for z in self.zonas_rojas if z.ocupada),
            'zonas_azules_ocupadas': sum(1 for z in self.zonas_azules if z.ocupada),
            'jugadores_posicionados': len(self.jugadores_posicionados)
        }

    def obtener_representacion_visual(self) -> str:
        """Genera representación visual básica del mapa"""
        lineas = []
        lineas.append(f"🗺️ Mapa Global ({len(self.celdas)} celdas)")

        stats = self.obtener_estadisticas()
        lineas.append(f"🔴 Zonas rojas: {stats['zonas_rojas_ocupadas']}/{stats['zonas_rojas']} ocupadas")
        lineas.append(f"🔵 Zonas azules: {stats['zonas_azules_ocupadas']}/{stats['zonas_azules']} ocupadas")
        lineas.append(f"👥 Jugadores posicionados: {stats['jugadores_posicionados']}")

        if self.jugadores_posicionados:
            lineas.append("Posiciones:")
            for jugador_id, zona in self.jugadores_posicionados.items():
                lineas.append(f"  Jugador {jugador_id}: {zona}")

        return "\n".join(lineas)

    def __str__(self):
        return f"MapaGlobal({len(self.celdas)} celdas, {len(self.jugadores_posicionados)} jugadores)"