import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.core.jugador import Jugador
from src.game.cartas.carta_base import CartaBase


def test_quitar_carta_del_tablero_pasa_a_banco():
    j = Jugador(1)
    carta = CartaBase.crear_basica(1, nombre="A")
    coord = j.tablero.obtener_coordenadas_disponibles()[0]
    j.colocar_carta_en_tablero(carta, coord)
    j.quitar_carta_del_tablero(coord)
    assert carta in j.cartas_banco
    assert j.tablero.obtener_carta_en(coord) is None

