#!/usr/bin/env python3
"""
Auto-battler - Punto de entrada principal
"""

import time

from src.core.motor_juego import MotorJuego
from src.core.jugador import Jugador
from src.utils.helpers import log_evento


def main():
    """Ejecuta una simulación automática con jugadores predeterminados."""
    print("=" * 50)
    print("🎮 AUTO-BATTLER - FASE PYTHON 🎮")
    print("=" * 50)
    print()

    try:
        jugadores = [Jugador(i + 1, f"Jugador {i+1}") for i in range(2)]
        motor = MotorJuego(jugadores)
        motor.iniciar()
        while len(motor.jugadores_vivos) > 1 and motor.ronda <= 5:
            motor.controlador_preparacion.finalizar_fase()
            while motor.fase_actual != "preparacion" and len(motor.jugadores_vivos) > 1:
                time.sleep(0.1)

        if motor.jugadores_vivos:
            print(f"🏆 Ganador: {motor.jugadores_vivos[0].nombre}")
        else:
            print("Empate.")
    except Exception as e:
        print(f"❌ Error durante la simulación: {e}")
        import traceback
        traceback.print_exc()


def main_con_opciones():
    """Versión con opciones interactivas"""
    print("=" * 50)
    print("🎮 AUTO-BATTLER - FASE PYTHON 🎮")
    print("=" * 50)
    print()

    # Pedir número de jugadores
    while True:
        try:
            num_jugadores = input("Número de jugadores (2-8, default 4): ").strip()
            if num_jugadores == "":
                num_jugadores = 4
            else:
                num_jugadores = int(num_jugadores)

            if 2 <= num_jugadores <= 8:
                break
            else:
                print("❌ Debe ser entre 2 y 8 jugadores")
        except ValueError:
            print("❌ Ingresa un número válido")

    print()
    jugadores = [Jugador(i + 1, f"Jugador {i+1}") for i in range(num_jugadores)]
    motor = MotorJuego(jugadores)
    motor.iniciar()
    while len(motor.jugadores_vivos) > 1 and motor.ronda <= 5:
        motor.controlador_preparacion.finalizar_fase()
        while motor.fase_actual != "preparacion" and len(motor.jugadores_vivos) > 1:
            time.sleep(0.1)


def juego_manual():
    """Interfaz CLI simple para controlar a ambos jugadores."""
    print("=" * 50)
    print("🖥️  MODO MANUAL")
    print("=" * 50)

    nombres = []
    for i in range(2):
        n = input(f"Nombre para el jugador {i+1} (Enter para 'Jugador {i+1}'): ")
        nombres.append(n.strip() or f"Jugador {i+1}")

    jugadores = [Jugador(i + 1, nombre) for i, nombre in enumerate(nombres)]
    motor = MotorJuego(jugadores)
    motor.iniciar()

    while len(motor.jugadores_vivos) > 1 and motor.ronda <= 5:
        print(f"\n--- RONDA {motor.ronda} ---")
        for jugador in motor.jugadores_vivos:
            tienda = motor.get_tienda_para(jugador.id)
            if not tienda:
                continue
            while True:
                print(f"\n{jugador.nombre} - Oro {jugador.oro}")
                for info in tienda.mostrar_cartas():
                    print(info)
                opcion = input("Indice para comprar, r para reroll, Enter para pasar: ")
                if opcion.strip() == "":
                    break
                if opcion.lower() == "r":
                    print(tienda.hacer_reroll())
                    continue
                try:
                    idx = int(opcion)
                except ValueError:
                    print("Índice inválido")
                    continue
                print(tienda.comprar_carta(idx))
        motor.controlador_preparacion.finalizar_fase()
        while motor.fase_actual != "preparacion" and len(motor.jugadores_vivos) > 1:
            time.sleep(0.1)

    if motor.jugadores_vivos:
        print(f"🏆 Ganador: {motor.jugadores_vivos[0].nombre}")
    else:
        print("Empate.")


if __name__ == "__main__":
    # Usar main() para ejecución automática o juego_manual() para interactivo
    main()

    # Descomentar la siguiente línea si quieres versión interactiva:
    # juego_manual()
