#!/usr/bin/env python3
"""
Auto-battler - Punto de entrada principal
"""

from src.core.motor_juego import MotorJuego
from src.utils.helpers import log_evento


def main():
    """Función principal del juego"""
    print("=" * 50)
    print("🎮 AUTO-BATTLER - FASE PYTHON 🎮")
    print("=" * 50)
    print()

    try:
        # Crear y configurar el motor
        motor = MotorJuego()

        # Ejecutar simulación con 4 jugadores por defecto
        num_jugadores = 4
        print(f"Iniciando simulación con {num_jugadores} jugadores...")
        print()

        motor.iniciar_simulacion(num_jugadores)

        print()
        print("=" * 50)
        print("✅ Simulación completada exitosamente")
        print("=" * 50)

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
    motor = MotorJuego()
    motor.iniciar_simulacion(num_jugadores)


if __name__ == "__main__":
    # Usar main() para ejecución automática o main_con_opciones() para interactiva
    main()

    # Descomentar la siguiente línea si quieres versión interactiva:
    # main_con_opciones()