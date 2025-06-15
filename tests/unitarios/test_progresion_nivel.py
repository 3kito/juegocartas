import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.core.jugador import Jugador
from src.data.config.game_config import GameConfig


def test_subida_nivel_automatica_multiple():
    j = Jugador(1, "Test")
    costos = GameConfig().costos_nivel
    j.ganar_experiencia(15)
    assert j.nivel == 3
    assert j.experiencia == 15 - costos[1] - costos[2]

