import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.game.board.hex_board import HexBoard
from src.game.board.hex_coordinate import HexCoordinate
from src.game.cards.base_card import BaseCard


def test_carta_muerta_se_remueve_del_tablero():
    carta = BaseCard({'id': 1, 'nombre': 'Test', 'stats': {'vida': 5, 'dano_fisico': 1}})
    tablero = HexBoard(radio=1)
    coord = HexCoordinate(0, 0)
    tablero.colocar_carta(coord, carta)
    assert tablero.obtener_carta_en(coord) is carta
    carta.recibir_dano(10)
    assert tablero.obtener_carta_en(coord) is None
