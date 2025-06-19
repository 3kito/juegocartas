import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.game.board.hex_board import HexBoard
from src.game.board.hex_coordinate import HexCoordinate, patron_circular
from src.game.cards.base_card import BaseCard


def test_celdas_visibles_por_patron():
    card = BaseCard({'id': 1, 'vision_pattern': [{'q':1,'r':0}, {'q':2,'r':0}]})
    board = HexBoard(radio=3)
    coord = HexCoordinate(0,0)
    board.colocar_carta(coord, card)
    visibles = card.calcular_celdas_visibles(coord)
    assert HexCoordinate(1,0) in visibles
    assert HexCoordinate(2,0) in visibles


def test_fallback_patron_circular():
    card = BaseCard({'id': 2, 'stats': {'rango_vision': 1}})
    board = HexBoard(radio=2)
    coord = HexCoordinate(0,0)
    board.colocar_carta(coord, card)
    expected = patron_circular(1)
    assert set(card.calcular_celdas_visibles(coord)) == set([coord + o for o in expected])

