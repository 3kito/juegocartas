# controlador_fase_enfrentamiento.py

from src.game.combate.fase.gestor_turnos import GestorTurnos
from src.utils.helpers import log_evento
from typing import Callable, Optional


class ControladorFaseEnfrentamiento:
    def __init__(
        self,
        motor,
        jugadores_por_color: dict,
        secuencia_turnos: list,
        al_terminar_fase: Optional[Callable] = None
    ):
        """
        motor: instancia de MotorTiempoReal
        jugadores_por_color: {"rojo": [jugadorA, jugadorB], "azul": [...]}
        secuencia_turnos: lista de dicts con color y duracion, ej:
            [{"color": "rojo", "duracion": 15}, {"color": "azul", "duracion": 30}, ...]
        al_terminar_fase: callback opcional que se llama cuando la fases termina
        """
        self.finalizada = False
        self.motor = motor
        self.turnos = GestorTurnos(jugadores_por_color, secuencia_turnos)
        self.al_terminar_fase = al_terminar_fase
        self.jugadores = [
            jugador for lista in jugadores_por_color.values() for jugador in lista
        ]
        
    def iniciar_fase(self):
        log_evento("🎬 Iniciando fases de enfrentamiento")
        self._iniciar_turno_actual()

    def _iniciar_turno_actual(self):
        turno = self.turnos.turno_actual_info()
        log_evento(f"🕒 Turno {self.turnos.turno_actual + 1}/{self.turnos.total_turnos()}: {turno['color'].upper()} ({turno['duracion']}s)")

        self.motor.programar_evento(
            callback=self._cambiar_turno,
            delay_segundos=turno["duracion"]
        )

    def _cambiar_turno(self):
        print("cambiando turno")
        self.turnos.avanzar_turno()
        if self.turnos.termino_fase():
            print("no quedan turnos")
            self.finalizar_fase()
        else:
            print("quedan turnos")
            self._iniciar_turno_actual()

    def finalizar_fase(self):
        if self.finalizada:
            return

        self.finalizada = True
        log_evento("🏁 Fase de enfrentamiento finalizada")

        for jugador in self.jugadores:
            if not hasattr(jugador, 'tablero'):
                continue
            cartas = jugador.tablero.obtener_cartas()
            vida_max = sum(c.vida_maxima for c in cartas)
            vida_actual = sum(c.vida_actual for c in cartas if c.esta_viva())

            if vida_max == 0:
                continue  # Evita división por cero si no hay cartas

            porcentaje_perdido = 1 - (vida_actual / vida_max)
            danio = round(30 * porcentaje_perdido)

            if danio > 0:
                jugador.recibir_dano(danio)
                log_evento(f"💔 {jugador.nombre} pierde {danio} de vida (vida restante: {vida_actual}/{vida_max})")
            else:
                log_evento(f"🛡️ {jugador.nombre} no recibe daño (vida intacta)")


        if self.al_terminar_fase:
            self.al_terminar_fase()

    def obtener_jugadores_activos(self):
        return self.turnos.jugadores_activos()

    def obtener_id_componente(self) -> str:
        return "fase_enfrentamiento"

    def procesar_tick(self, delta_tiempo: float):
        # Este controlador debe mantenerse activo mientras la fase esté en curso
        return not self.finalizada  # Retorna True mientras no haya terminado
