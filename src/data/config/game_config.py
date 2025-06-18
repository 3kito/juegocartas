import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "game_config.json")

class GameConfig:
    def __init__(self):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.fase_preparacion_segundos = data.get("fase_preparacion_segundos", 30)
        self.subasta_ratio = data.get("subasta_ratio", 0.5)
        self.oro_por_ronda = data.get("oro_por_ronda", 10)
        self.cartas_por_tienda = data.get("cartas_por_tienda", 5)
        self.cartas_subasta_default = data.get("cartas_subasta_default", 5)
        # Cantidad de copias de cada carta por tier
        self.copias_por_tier = {
            1: data.get("copias_por_tier", {}).get("1", 8),
            2: data.get("copias_por_tier", {}).get("2", 5),
            3: data.get("copias_por_tier", {}).get("3", 3),
        }

        # Limitar cantidad de tipos de carta por tier (0 = sin límite)
        self.max_cartas_por_tier = {
            1: data.get("max_cartas_por_tier", {}).get("1", 0),
            2: data.get("max_cartas_por_tier", {}).get("2", 0),
            3: data.get("max_cartas_por_tier", {}).get("3", 0),
        }

        # Lista de IDs de cartas permitidas (vacío = todas)
        self.cartas_activas = data.get("cartas_activas", [])

        # Modo testeo manual
        self.modo_testeo = data.get("modo_testeo", False)
