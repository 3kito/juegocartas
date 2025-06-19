import os
from src.core.jugador import Jugador
from src.core.motor_juego import MotorJuego
from src.utils.helpers import log_evento


def crear_jugadores(n):
    return [Jugador(i + 1, f"Bot{i + 1}") for i in range(n)]


def iniciar_juego(n):
    jugadores = crear_jugadores(n)
    motor = MotorJuego(jugadores=jugadores)
    motor.modo_testeo = True
    motor.config.modo_testeo = True
    motor.iniciar()
    return motor


def mostrar_estado(motor):
    log_evento(f"Fase: {motor.fase_actual} | Ronda: {motor.ronda}")
    for j in motor.jugadores_vivos:
        estado = j.obtener_resumen_estado()
        log_evento(
            f"J{estado['id']} {estado['nombre']} V:{estado['vida']} O:{estado['oro']} N:{estado['nivel']}"
        )


def main():
    os.environ["LOG_TO_FILE"] = "1"
    motor = None
    print("Modo debug iniciado. Escriba 'help' para comandos.")
    while True:
        try:
            linea = input("debug> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not linea:
            continue
        partes = linea.split()
        cmd = partes[0].lower()

        if cmd == "help":
            print("Comandos disponibles:")
            print("  start [n]      - iniciar juego con n jugadores (default 2)")
            print("  step           - avanzar al siguiente paso")
            print("  info           - mostrar estado actual")
            print("  buy j i        - jugador j compra carta i de su tienda")
            print("  reroll j       - jugador j hace reroll en su tienda")
            print("  bid j id monto - jugador j oferta en subasta")
            print("  quit           - salir")
        elif cmd == "start":
            n = int(partes[1]) if len(partes) > 1 else 2
            motor = iniciar_juego(n)
        elif cmd == "step":
            if motor:
                motor.ejecutar_siguiente_paso()
            else:
                print("No hay juego activo")
        elif cmd == "info":
            if motor:
                mostrar_estado(motor)
            else:
                print("No hay juego activo")
        elif cmd == "buy" and len(partes) >= 3:
            if motor and motor.controlador_preparacion:
                j = int(partes[1])
                i = int(partes[2])
                res = motor.controlador_preparacion.realizar_compra_tienda(j, i)
                log_evento(res)
            else:
                print("Comando no disponible")
        elif cmd == "reroll" and len(partes) >= 2:
            if motor and motor.controlador_preparacion:
                j = int(partes[1])
                res = motor.controlador_preparacion.realizar_reroll_tienda(j)
                log_evento(res)
            else:
                print("Comando no disponible")
        elif cmd == "bid" and len(partes) >= 4:
            if motor and motor.controlador_preparacion:
                j = int(partes[1])
                cid = partes[2]
                monto = int(partes[3])
                res = motor.controlador_preparacion.realizar_oferta_subasta(j, cid, monto)
                log_evento(res)
            else:
                print("Comando no disponible")
        elif cmd in {"quit", "exit"}:
            break
        else:
            print("Comando desconocido")

    if motor and hasattr(motor, "motor") and motor.motor:
        motor.motor.detener()
    log_evento("Debug finalizado", "SUCCESS")


if __name__ == "__main__":
    main()
