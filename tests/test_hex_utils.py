import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.hex_utils import pixel_to_hex, hex_to_pixel
from src.game.tablero.coordenada import CoordenadaHexagonal

@pytest.mark.parametrize("size,offset", [(10,(0,0)), (20,(5,5)), (30,(10,15))])
def test_round_trip(size, offset):
    coords = [CoordenadaHexagonal(q,r) for q in range(-3,4) for r in range(-3,4) if -q - r >= -3 and -q - r <=3]
    for c in coords:
        x, y = hex_to_pixel(c, size, offset)
        assert pixel_to_hex(x, y, size, offset) == c
