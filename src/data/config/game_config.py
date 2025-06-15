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
