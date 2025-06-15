import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.game.combate.fase.controlador_fase_enfrentamiento import ControladorFaseEnfrentamiento
from src.game.combate.fase.gestor_turnos import GestorTurnos
from unittest.mock import Mock

def test_turno_se_avanza_correctamente():
    jugadores_por_color = {
        "rojo": ["jugador1"],
        "azul": ["jugador2"]
    }
    secuencia = [
        {"color": "rojo", "duracion": 1},
        {"color": "azul", "duracion": 1}
    ]
    gestor = GestorTurnos(jugadores_por_color, secuencia)
    assert gestor.turno_actual_info()["color"] == "rojo"
    gestor.avanzar_turno()
    assert gestor.turno_actual_info()["color"] == "azul"
    assert gestor.termino_fase() is False
    gestor.avanzar_turno()
    assert gestor.termino_fase() is True

def test_controlador_termina_fase_correctamente():
    jugadores = {"rojo": [], "azul": []}
    secuencia = [{"color": "rojo", "duracion": 0.01}, {"color": "azul", "duracion": 0.01}]
    gestor = GestorTurnos(jugadores, secuencia)

    mock_motor = Mock()
    mock_motor.programar_evento = lambda *args, **kwargs: None
    mock_motor.detener = lambda: setattr(mock_motor, "detenido", True)
    mock_motor.detenido = False

    llamada = {"termino": False}

    controlador = ControladorFaseEnfrentamiento(
        motor=mock_motor,
        jugadores_por_color=jugadores,
        secuencia_turnos=secuencia
    )
    # Inyectar el callback manualmente (no estaba en constructor)
    controlador.finalizar_fase = lambda: llamada.update({"termino": True}) or mock_motor.detener()

    # Simular paso de turnos
    controlador._iniciar_turno_actual()
    controlador._cambiar_turno()
    controlador._cambiar_turno()

    assert llamada["termino"] is True
    assert mock_motor.detenido is True

if __name__ == "__main__":
    test_turno_se_avanza_correctamente()
    test_controlador_termina_fase_correctamente()
    print("✅ Test unitarios de turnos pasaron correctamente.")
