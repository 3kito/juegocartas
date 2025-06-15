import pytest
from src.core.jugador import Jugador
from src.game.tablero.tablero_hexagonal import TableroHexagonal
from src.game.cartas.carta_base import CartaBase
from src.game.combate.fase.controlador_fase_enfrentamiento import ControladorFaseEnfrentamiento


def crear_carta(nombre, vida_max, vida_actual):
    carta = CartaBase({
        "id": 999,
        "nombre": nombre,
        "tier": 1,
        "costo": 1,
        "stats": {
            "vida": vida_max,
            "dano_fisico": 10,
            "dano_magico": 5
        }
    })
    carta.vida_actual = vida_actual
    return carta


def simular_enfrentamiento(jugador):
    controlador = ControladorFaseEnfrentamiento(
        motor=None,
        jugadores_por_color={"azul": [jugador]},
        secuencia_turnos=[],
        al_terminar_fase=None
    )
    controlador.finalizar_fase()


def test_vida_se_resta_50_por_ciento():
    jugador = Jugador(1, "Test 50%")
    jugador.vida = 100
    jugador.tablero = TableroHexagonal()

    cartas = [
        crear_carta("San Martín", 125, 100),
        crear_carta("Newton", 75, 50),
        crear_carta("Tesla", 75, 0),
        crear_carta("Curie", 25, 0),
    ]

    coords = jugador.tablero.coordenadas_libres()[:4]
    for coord, carta in zip(coords, cartas):
        jugador.tablero.colocar_carta(coord, carta)

    simular_enfrentamiento(jugador)
    assert jugador.vida == 85, f"Esperaba 85, obtuvo {jugador.vida}"


def test_vida_se_resta_0_por_ciento():
    jugador = Jugador(2, "Test 0%")
    jugador.vida = 100
    jugador.tablero = TableroHexagonal()

    cartas = [
        crear_carta("Einstein", 100, 100),
        crear_carta("Copérnico", 100, 100),
    ]

    coords = jugador.tablero.coordenadas_libres()[:2]
    for coord, carta in zip(coords, cartas):
        jugador.tablero.colocar_carta(coord, carta)

    simular_enfrentamiento(jugador)
    assert jugador.vida == 100, f"Esperaba 100, obtuvo {jugador.vida}"


def test_vida_se_resta_100_por_ciento():
    jugador = Jugador(3, "Test 100%")
    jugador.vida = 100
    jugador.tablero = TableroHexagonal()

    cartas = [
        crear_carta("Tesla", 50, 0),
        crear_carta("Darwin", 50, 0),
    ]

    coords = jugador.tablero.coordenadas_libres()[:2]
    for coord, carta in zip(coords, cartas):
        jugador.tablero.colocar_carta(coord, carta)

    simular_enfrentamiento(jugador)
    assert jugador.vida == 70, f"Esperaba 70, obtuvo {jugador.vida}"
