# controlador_fase_enfrentamiento.py

from src.game.combate.fase.gestor_turnos import GestorTurnos
from src.utils.helpers import log_evento
from typing import Callable, Optional
import time


class ControladorFaseEnfrentamiento:
    def __init__(
        self,
        motor,
        jugadores_por_color: dict,
        secuencia_turnos: list,
        al_terminar_fase: Optional[Callable] = None,
        modo_testeo: bool = False
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
        self.modo_testeo = modo_testeo
        self.turno_activo = None
        self.fin_turno = None
        self.jugadores = [
            jugador for lista in jugadores_por_color.values() for jugador in lista
        ]
        self._evento_turno = None
        
    def iniciar_fase(self):
        log_evento("🎬 Iniciando fases de enfrentamiento")
        self._iniciar_turno_actual()

    def _iniciar_turno_actual(self):
        turno = self.turnos.turno_actual_info()
        self.turno_activo = turno["color"]
        duracion = 999999 if self.modo_testeo else turno["duracion"]
        self.fin_turno = time.time() + duracion
        log_evento(
            f"🕒 Turno {self.turnos.turno_actual + 1}/{self.turnos.total_turnos()}: {turno['color'].upper()} ({duracion}s)"
        )

        self._evento_turno = self.motor.programar_evento(
            callback=self._cambiar_turno,
            delay_segundos=duracion,
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

    def cambiar_turno_manual(self):
        self.turnos.avanzar_turno()
        if self.turnos.termino_fase():
            self.finalizar_fase()
        else:
            self.turno_activo = self.turnos.turno_actual_info()["color"]
            self.fin_turno = time.time() + self.turnos.turno_actual_info()["duracion"]
            log_evento(f"🔄 Cambio de turno manual: {self.turno_activo.upper()}")

    def finalizar_fase(self):
        if self.finalizada:
            return

        self.finalizada = True
        self.fin_turno = None
        log_evento("🏁 Fase de enfrentamiento finalizada")

        for jugador in self.jugadores:
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

            # Revivir cartas para la siguiente fase
            for carta in cartas:
                carta.revivir()


        if self.al_terminar_fase:
            self.al_terminar_fase()

    def obtener_turno_activo(self):
        if self.modo_testeo:
            return self.turno_activo
        return self.turnos.turno_actual_info()["color"]

    def obtener_jugadores_activos(self):
        return self.turnos.jugadores_activos()

    def obtener_tiempo_restante_turno(self) -> float:
        """Segundos restantes para que finalice el turno actual"""
        if self.fin_turno is None:
            return 0.0
        return max(0.0, self.fin_turno - time.time())

    def acelerar_temporizador(self, segundos: int = 2):
        """Reduce el tiempo restante del turno actual"""
        if self.fin_turno is None:
            return
        self.fin_turno = time.time() + segundos
        if self._evento_turno and self._evento_turno in self.motor.eventos_programados:
            self.motor.eventos_programados[self._evento_turno].tiempo_ejecucion = self.fin_turno

    def obtener_id_componente(self) -> str:
        return "fase_enfrentamiento"

    def procesar_tick(self, delta_tiempo: float):
        # Este controlador debe mantenerse activo mientras la fase esté en curso
        return not self.finalizada  # Retorna True mientras no haya terminado
