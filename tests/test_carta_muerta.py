import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.game.tablero.tablero_hexagonal import TableroHexagonal
from src.game.tablero.coordenada import CoordenadaHexagonal
from src.game.cartas.carta_base import CartaBase


def test_carta_muerta_se_remueve_del_tablero():
    carta = CartaBase({'id': 1, 'nombre': 'Test', 'stats': {'vida': 5, 'dano_fisico': 1}})
    tablero = TableroHexagonal(radio=1)
    coord = CoordenadaHexagonal(0, 0)
    tablero.colocar_carta(coord, carta)
    assert tablero.obtener_carta_en(coord) is carta
    carta.recibir_dano(10)
    assert tablero.obtener_carta_en(coord) is None
