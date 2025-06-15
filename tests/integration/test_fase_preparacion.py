import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.core.jugador import Jugador
from src.game.fases.controlador_preparacion import ControladorFasePreparacion
from src.game.cartas.carta_base import CartaBase
from src.game.tablero.tablero_hexagonal import TableroHexagonal


def crear_carta_mock(nombre, tier=1):
    return CartaBase({
        "id": 999,
        "nombre": nombre,
        "tier": tier,
        "costo": 1,
        "stats": {
            "vida": 100,
            "dano_fisico": 10,
            "dano_magico": 5
        }
    })


@pytest.fixture
def jugador_preparado():
    jugador = Jugador(1, "TestPlayer")
    jugador.oro = 20
    jugador.tablero = TableroHexagonal()

    carta1 = crear_carta_mock("Tesla")
    carta2 = crear_carta_mock("Tesla")
    carta3 = crear_carta_mock("Tesla")

    coords = jugador.tablero.coordenadas_libres()[:2]
    jugador.tablero.colocar_carta(coords[0], carta1)
    jugador.tablero.colocar_carta(coords[1], carta2)
    jugador.agregar_carta_al_banco(carta3)

    return jugador


def test_creacion_tienda_y_subasta(jugador_preparado):
    controlador = ControladorFasePreparacion([jugador_preparado])
    controlador.iniciar_fase(ronda=1)

    assert jugador_preparado.id in controlador.tiendas_individuales
    assert controlador.subastas is not None
    assert len(controlador.subastas.cartas_subastadas) > 0


def test_fusion_aplicada_correctamente(jugador_preparado):
    controlador = ControladorFasePreparacion([jugador_preparado])
    controlador.iniciar_fase(ronda=1)

    cartas_tablero = [c for c in jugador_preparado.tablero.celdas.values() if c]
    cartas_banco = [c for c in jugador_preparado.cartas_banco if c]
    total_cartas = cartas_tablero + cartas_banco

    assert len(total_cartas) == 1, "Debe quedar una carta fusionada"
    fusionada = total_cartas[0]
    assert fusionada.tier == 2, "La carta fusionada debe tener tier 2"


def test_subasta_funciona_y_descuenta_oro(jugador_preparado):
    controlador = ControladorFasePreparacion([jugador_preparado])
    controlador.iniciar_fase(ronda=1)

    oro_inicial = jugador_preparado.oro
    ofertas_exitosas = 0

    for carta_id in controlador.subastas.cartas_subastadas:
        r = controlador.subastas.ofertar(jugador_preparado, carta_id, 3)
        assert r.startswith("✅")
        ofertas_exitosas += 1

    controlador.subastas.resolver_subastas()

    ganadas = [c for c in jugador_preparado.cartas_banco if c and not c.nombre.startswith("Tesla")]
    assert len(ganadas) == ofertas_exitosas
    assert jugador_preparado.oro == oro_inicial - 3 * ofertas_exitosas
