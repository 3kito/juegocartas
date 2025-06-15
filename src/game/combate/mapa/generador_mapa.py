from .zona_mapa import ZonaMapa
from .utilidades_mapa import generar_hexagonos_contiguos
from src.game.tablero.tablero_hexagonal import CoordenadaHexagonal
import random

class GeneradorMapa:
    def __init__(self, tablero, celdas_por_zona: int = 19, cantidad_parejas: int = 3):
        self.tablero = tablero
        self.celdas_por_zona = celdas_por_zona
        self.cantidad_parejas = cantidad_parejas
        self.zonas_rojas = []
        self.zonas_azules = []

    def generar(self):
        coordenadas_disponibles = set(self.tablero.celdas.keys())
        usadas = set()

        for pareja_id in range(self.cantidad_parejas):
            origen = random.choice(list(coordenadas_disponibles - usadas))
            zona_roja_coords = generar_hexagonos_contiguos(
                origen, self.celdas_por_zona, disponibles=coordenadas_disponibles
            )

            usadas.update(zona_roja_coords)
            self.zonas_rojas.append(ZonaMapa("rojo", zona_roja_coords, pareja_id=pareja_id))

            # Buscar origen cercano a la zona roja
            candidatos = list(zona_roja_coords)
            random.shuffle(candidatos)
            origen_azul = None
            for c in candidatos:
                vecinos = c.vecinos()
                for vecino in vecinos:
                    if vecino in coordenadas_disponibles and vecino not in usadas:
                        origen_azul = vecino
                        break
                if origen_azul:
                    break

            if not origen_azul:
                origen_azul = random.choice(list(coordenadas_disponibles - usadas))

            zona_azul_coords = generar_hexagonos_contiguos(
                origen_azul, self.celdas_por_zona, disponibles=coordenadas_disponibles
            )
            usadas.update(zona_azul_coords)
            self.zonas_azules.append(ZonaMapa("azul", zona_azul_coords, pareja_id=pareja_id))
