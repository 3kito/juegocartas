import time
import pytest
from src.core.motor_juego import MotorJuego
from src.core.jugador import Jugador
from src.game.cartas.carta_base import CartaBase


def crear_jugador(id_jugador, cantidad_cartas=2):
    jugador = Jugador(id_jugador=id_jugador)
    for i in range(cantidad_cartas):
        datos_mock = {"nombre": f"Carta{id_jugador}-{i}", "tier": 1}
        carta = CartaBase(datos_carta=datos_mock)
        jugador.agregar_carta_al_banco(carta)
    return jugador


def test_motor_juego_fase_combate_funciona():
    # 🧪 Fase 1: Crear jugadores
    try:
        jugador1 = crear_jugador("J1")
        jugador2 = crear_jugador("J2")
    except Exception as e:
        pytest.fail(f"Fallo en la creación de jugadores: {e}")

    # 🧪 Fase 2: Iniciar motor de juego
    try:
        motor = MotorJuego(jugadores=[jugador1, jugador2])
    except Exception as e:
        pytest.fail(f"Fallo al instanciar el motor de juego: {e}")

    # 🧪 Fase 3: Iniciar fases de combate
    try:
        motor.iniciar()
    except Exception as e:
        pytest.fail(f"Fallo al iniciar la fases de combate: {e}")

    # 🧪 Fase 4: Esperar transición a fases preparación
    tiempo_limite = time.time() + 10  # tiempo máximo de espera
    while motor.fase_actual != "preparacion" and time.time() < tiempo_limite:
        time.sleep(0.01)

    # 🧪 Fase 5: Verificación final
    assert motor.fase_actual == "preparacion", "El juego no volvió a fases preparación"
