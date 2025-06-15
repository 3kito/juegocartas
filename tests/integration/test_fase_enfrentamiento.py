import time
from src.game.combate.fase.controlador_fase_enfrentamiento import ControladorFaseEnfrentamiento
from src.game.combate.fase.gestor_turnos import GestorTurnos
from src.game.combate.motor.motor_tiempo_real import MotorTiempoReal


def test_integration_fase_enfrentamiento_termina():
    jugadores_por_color = {
        "rojo": ["jugador1"],
        "azul": ["jugador2"]
    }

    secuencia = [
        {"color": "rojo", "duracion": 0.05},
        {"color": "azul", "duracion": 0.05}
    ]

    motor = MotorTiempoReal(fps_objetivo=10)
    bandera = {"terminado": False}

    def finalizar():
        bandera["terminado"] = True

    controlador = ControladorFaseEnfrentamiento(
        motor=motor,
        jugadores_por_color=jugadores_por_color,
        secuencia_turnos=secuencia,
        al_terminar_fase=finalizar
    )

    motor.agregar_componente(controlador)
    controlador.iniciar_fase()
    motor.iniciar()

    # Esperar hasta que se llame a finalizar() o se agote el tiempo
    tiempo_limite = time.time() + 1  # 1 segundo máx
    while not bandera["terminado"] and time.time() < tiempo_limite:
        time.sleep(0.01)

    assert bandera["terminado"] is True
    print("✅ Test de integración de fases enfrentamiento: OK")

if __name__ == "__main__":
    test_integration_fase_enfrentamiento_termina()
