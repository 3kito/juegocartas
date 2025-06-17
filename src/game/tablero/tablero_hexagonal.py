from typing import Dict, Optional, List
from src.game.tablero.coordenada import CoordenadaHexagonal
from src.utils.helpers import log_evento


class TableroHexagonal:
    def __init__(self, radio: int = 2):
        self.radio = radio
        self.centro = CoordenadaHexagonal(0, 0)
        self.celdas: Dict[CoordenadaHexagonal, Optional[any]] = {}
        self._generar_celdas()

    def _generar_celdas(self):
        """Genera las celdas del hexágono con el radio especificado."""
        coordenadas = self.centro.obtener_area(self.radio)

        for coord in coordenadas:
            self.celdas[coord] = None  # Inicialmente vacías

        log_evento(f"Tablero generado: {len(self.celdas)} celdas")

    def obtener_celda(self, coordenada: CoordenadaHexagonal):
        return self.celdas.get(coordenada)

    def colocar_carta(self, coordenada: CoordenadaHexagonal, carta):
        if coordenada in self.celdas:
            self.celdas[coordenada] = carta
            if hasattr(carta, "coordenada"):
                carta.coordenada = coordenada
            if hasattr(carta, "tablero"):
                carta.tablero = self
            log_evento(f"✅ Carta colocada en {coordenada}")
        else:
            log_evento(f"❌ Coordenada {coordenada} no existe en el tablero")

    def obtener_cartas_en_rango(self, origen, rango: int):
        """
        Retorna una lista de tuplas (coordenada, carta) dentro del rango especificado.
        """
        celdas_en_rango = origen.obtener_area(rango)
        resultado = []

        for coord in celdas_en_rango:
            if coord in self.celdas:
                carta = self.celdas[coord]
                if carta is not None:
                    resultado.append((coord, carta))

        return resultado

    def obtener_coordenada_de(self, carta) -> Optional[CoordenadaHexagonal]:
        for coord, obj in self.celdas.items():
            if obj is carta:
                return coord
        return None

    def obtener_cartas(self) -> List:
        return [carta for carta in self.celdas.values() if carta is not None]

    def obtener_carta_en(self, coordenada: CoordenadaHexagonal):
        return self.celdas.get(coordenada)

    def coordenadas_ocupadas(self) -> List[CoordenadaHexagonal]:
        return [coord for coord, carta in self.celdas.items() if carta is not None]

    def coordenadas_libres(self) -> List[CoordenadaHexagonal]:
        return [coord for coord, carta in self.celdas.items() if carta is None]

    def esta_vacia(self, coordenada: CoordenadaHexagonal) -> bool:
        return self.celdas.get(coordenada) is None

    def esta_dentro_del_tablero(self, coord: CoordenadaHexagonal) -> bool:
        return coord in self.celdas

    def limpiar_tablero(self):
        for coord in self.celdas:
            self.celdas[coord] = None
    def quitar_carta(self, coordenada):
        """Quita y devuelve la carta de la coordenada especificada"""
        carta = None
        if coordenada in self.celdas:
            carta = self.celdas[coordenada]
            self.celdas[coordenada] = None
            if carta:
                log_evento(
                    f"🔸 Carta '{getattr(carta, 'nombre', 'desconocida')}' retirada de {coordenada}",
                    "DEBUG",
                )
                if hasattr(carta, "coordenada"):
                    carta.coordenada = None
                if hasattr(carta, "tablero"):
                    carta.tablero = None
        return carta

    def contar_cartas(self) -> int:
        """Cuenta el número total de cartas en el tablero"""
        return len([carta for carta in self.celdas.values() if carta is not None])

    def obtener_coordenadas_disponibles(self) -> List[CoordenadaHexagonal]:
        """Alias para coordenadas_libres() - mantiene compatibilidad con jugador.py"""
        return self.coordenadas_libres()

    def mover_carta(self, desde: CoordenadaHexagonal, hacia: CoordenadaHexagonal) -> bool:
        """Mueve una carta de una coordenada a otra"""
        # Verificar que ambas coordenadas existen en el tablero
        if desde not in self.celdas or hacia not in self.celdas:
            log_evento(f"❌ Coordenadas inválidas para mover carta: {desde} → {hacia}")
            return False

        # Verificar que hay una carta en la posición origen
        carta = self.celdas.get(desde)
        if carta is None:
            log_evento(f"❌ No hay carta en {desde} para mover")
            return False

        # Verificar que la posición destino está libre
        if self.celdas.get(hacia) is not None:
            log_evento(f"❌ La posición {hacia} ya está ocupada")
            return False

        # Realizar el movimiento
        self.celdas[desde] = None
        self.celdas[hacia] = carta
        if hasattr(carta, "coordenada"):
            carta.coordenada = hacia
        log_evento(f"↔️ Carta movida: {desde} → {hacia}")
        return True

    def obtener_estadisticas(self) -> Dict[str, any]:
        """Retorna estadísticas detalladas del tablero"""
        cartas_totales = self.contar_cartas()
        espacios_totales = len(self.celdas)
        espacios_libres = len(self.coordenadas_libres())

        # Contar cartas por tipo si tienen el atributo nombre
        tipos_cartas = {}
        for carta in self.celdas.values():
            if carta is not None and hasattr(carta, 'nombre'):
                nombre = carta.nombre
                tipos_cartas[nombre] = tipos_cartas.get(nombre, 0) + 1

        return {
            'cartas_totales': cartas_totales,
            'espacios_totales': espacios_totales,
            'espacios_libres': espacios_libres,
            'espacios_ocupados': cartas_totales,
            'porcentaje_ocupacion': (cartas_totales / espacios_totales * 100) if espacios_totales > 0 else 0,
            'tipos_cartas': tipos_cartas,
            'radio_tablero': self.radio,
            'centro': str(self.centro)
        }

    def intercambiar_cartas(self, coord1: CoordenadaHexagonal, coord2: CoordenadaHexagonal) -> bool:
        """Intercambia las cartas en dos posiciones (bonus method)"""
        if coord1 not in self.celdas or coord2 not in self.celdas:
            log_evento(f"❌ Coordenadas inválidas para intercambiar: {coord1} ↔ {coord2}")
            return False

        carta1 = self.celdas[coord1]
        carta2 = self.celdas[coord2]

        self.celdas[coord1] = carta2
        self.celdas[coord2] = carta1

        log_evento(f"🔄 Cartas intercambiadas: {coord1} ↔ {coord2}")
        return True

    def obtener_cartas_con_posiciones(self) -> List[tuple]:
        """Retorna lista de tuplas (coordenada, carta) para todas las cartas en el tablero"""
        resultado = []
        for coord, carta in self.celdas.items():
            if carta is not None:
                resultado.append((coord, carta))
        return resultado

    def buscar_carta(self, carta_objetivo) -> Optional[CoordenadaHexagonal]:
        """Busca una carta específica y retorna su coordenada"""
        for coord, carta in self.celdas.items():
            if carta is carta_objetivo:
                return coord
        return None

    def obtener_densidad_area(self, centro: CoordenadaHexagonal, radio: int) -> float:
        """Calcula la densidad de cartas en un área específica"""
        celdas_area = centro.obtener_area(radio)
        celdas_validas = [c for c in celdas_area if c in self.celdas]

        if not celdas_validas:
            return 0.0

        cartas_en_area = sum(1 for c in celdas_validas if self.celdas[c] is not None)
        return cartas_en_area / len(celdas_validas)