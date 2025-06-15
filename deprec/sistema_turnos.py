"""
Sistema de turnos dual: rojos activos vs azules activos
MODIFICADO para integrar combates continuos
"""

import time
from typing import Dict, Optional, Set
from enum import Enum
from src.game.combate.mapa_global import MapaGlobal
from src.game.combate.motor.motor_tiempo_real import MotorTiempoReal
from deprec.manager_combates import ManagerCombates
from src.utils.helpers import log_evento


class EstadoTurno(Enum):
    """Estados posibles del sistema de turnos"""
    ROJOS_ACTIVOS = "rojos_activos"
    AZULES_ACTIVOS = "azules_activos"
    TRANSICION = "transicion"
    FINALIZADO = "finalizado"


class SistemaTurnosConCombateContinuo:
    """Sistema de turnos integrado con combates continuos"""

    def __init__(self, mapa_global: MapaGlobal):
        self.mapa = mapa_global

        # Estado del sistema
        self.estado_actual = EstadoTurno.ROJOS_ACTIVOS
        self.turno_numero = 1
        self.tiempo_inicio_turno = 0

        # Configuración (después mover a config)
        self.duracion_turno_segundos = 30
        self.max_turnos = 50  # Límite de seguridad

        # Jugadores activos/pasivos
        self.jugadores_activos: Set[int] = set()
        self.jugadores_pasivos: Set[int] = set()

        # NUEVO: Integración con motor de tiempo real
        self.motor_tiempo_real: Optional[MotorTiempoReal] = None
        self.manager_combates: Optional[ManagerCombates] = None

        # Control de finalización
        self.juego_terminado = False
        self.ganador_color = None

    def iniciar_sistema(self, motor_tiempo_real: MotorTiempoReal) -> bool:
        """Inicia el sistema de turnos con motor de tiempo real"""
        log_evento(f"🎮 Iniciando Sistema de Turnos con Combate Continuo")
        log_evento(f"   Duración por turno: {self.duracion_turno_segundos}s")
        log_evento(f"   Máximo turnos: {self.max_turnos}")

        # Configurar motor de tiempo real
        self.motor_tiempo_real = motor_tiempo_real

        # Crear y configurar manager de combates
        self.manager_combates = ManagerCombates()

        # Agregar manager al motor de tiempo real
        if not self.motor_tiempo_real.agregar_componente(self.manager_combates):
            log_evento("❌ No se pudo agregar manager de combates al motor")
            return False

        # Verificar que hay jugadores en ambos colores
        jugadores_rojos = self.mapa.obtener_jugadores_activos("roja")
        jugadores_azules = self.mapa.obtener_jugadores_activos("azul")

        if not jugadores_rojos and not jugadores_azules:
            log_evento("❌ No hay jugadores posicionados en el mapa")
            return False

        log_evento(f"🔴 Jugadores rojos: {jugadores_rojos}")
        log_evento(f"🔵 Jugadores azules: {jugadores_azules}")

        # Iniciar con rojos activos
        self._cambiar_a_estado(EstadoTurno.ROJOS_ACTIVOS)
        return True

    def _cambiar_a_estado(self, nuevo_estado: EstadoTurno):
        """Cambia el estado del sistema y configura jugadores activos/pasivos"""
        estado_anterior = self.estado_actual
        self.estado_actual = nuevo_estado
        self.tiempo_inicio_turno = time.time()

        log_evento(f"🔄 Cambio de estado: {estado_anterior.value} → {nuevo_estado.value}")

        if nuevo_estado == EstadoTurno.ROJOS_ACTIVOS:
            self.jugadores_activos = set(self.mapa.obtener_jugadores_activos("roja"))
            self.jugadores_pasivos = set(self.mapa.obtener_jugadores_activos("azul"))
            log_evento(f"🔴 TURNO {self.turno_numero}: Rojos activos ({len(self.jugadores_activos)} jugadores)")

        elif nuevo_estado == EstadoTurno.AZULES_ACTIVOS:
            self.jugadores_activos = set(self.mapa.obtener_jugadores_activos("azul"))
            self.jugadores_pasivos = set(self.mapa.obtener_jugadores_activos("roja"))
            log_evento(f"🔵 TURNO {self.turno_numero}: Azules activos ({len(self.jugadores_activos)} jugadores)")

        elif nuevo_estado == EstadoTurno.TRANSICION:
            self.jugadores_activos.clear()
            self.jugadores_pasivos.clear()
            log_evento("⏸️ En transición...")

        elif nuevo_estado == EstadoTurno.FINALIZADO:
            self.jugadores_activos.clear()
            self.jugadores_pasivos.clear()
            self.juego_terminado = True
            log_evento("🏁 Sistema de turnos finalizado")

        # Log de jugadores activos
        if self.jugadores_activos:
            log_evento(f"   Activos: {list(self.jugadores_activos)}")
        if self.jugadores_pasivos:
            log_evento(f"   Pasivos: {list(self.jugadores_pasivos)}")

    def ejecutar_turno(self) -> bool:
        """Ejecuta un turno completo y retorna True si debe continuar"""
        if self.juego_terminado:
            return False

        # Verificar límite de turnos
        if self.turno_numero > self.max_turnos:
            log_evento(f"⚠️ Límite de turnos alcanzado ({self.max_turnos})")
            self._finalizar_juego("limite_turnos")
            return False

        # Verificar condiciones de victoria
        if self._verificar_condiciones_victoria():
            return False

        # Ejecutar según estado actual
        if self.estado_actual in [EstadoTurno.ROJOS_ACTIVOS, EstadoTurno.AZULES_ACTIVOS]:
            return self._ejecutar_fase_activa()
        elif self.estado_actual == EstadoTurno.TRANSICION:
            return self._ejecutar_transicion()
        else:
            return False

    def _ejecutar_fase_activa(self) -> bool:
        """Ejecuta la fases donde un color está activo"""
        tiempo_transcurrido = time.time() - self.tiempo_inicio_turno
        tiempo_restante = self.duracion_turno_segundos - tiempo_transcurrido

        # NUEVO: Procesar resultados de combates terminados
        if self.manager_combates:
            self._procesar_resultados_combates()

        # Log periódico de tiempo (cada 5 segundos)
        if int(tiempo_transcurrido) % 5 == 0 and tiempo_restante > 0:
            combates_activos = len(self.manager_combates.combates_activos) if self.manager_combates else 0
            log_evento(f"⏰ Tiempo restante: {tiempo_restante:.1f}s - Combates activos: {combates_activos}")

        # Verificar si el tiempo se agotó
        if tiempo_transcurrido >= self.duracion_turno_segundos:
            log_evento(f"⏱️ Tiempo agotado para turno {self.turno_numero}")
            self._finalizar_turno_activo()
            return True

        # MODIFICADO: Los combates continúan automáticamente via motor de tiempo real
        # Solo procesamos órdenes de jugadores activos
        self._procesar_ordenes_jugadores_activos()

        return True

    def _procesar_ordenes_jugadores_activos(self):
        """Procesa órdenes de jugadores activos (simulado por ahora)"""
        # Por ahora solo un log ocasional para no spam
        import random
        if random.random() < 0.05:  # 5% chance por ciclo
            if self.jugadores_activos and self.manager_combates:
                stats = self.manager_combates.obtener_estadisticas_globales()
                if stats['combates_activos'] < 3:  # Crear más combates ocasionalmente
                    log_evento(f"  👤 Simulando nueva orden de combate...")

    def _procesar_resultados_combates(self):
        """Procesa resultados de combates que han terminado"""
        if not self.manager_combates:
            return

        resultados = self.manager_combates.obtener_combates_terminados()

        for resultado in resultados:
            log_evento(f"🏁 Combate terminado - Duración: {resultado.duracion_segundos:.1f}s, "
                       f"Supervivientes: {len(resultado.cartas_supervivientes)}")

            # Aquí se aplicarían los efectos del combate
            # (daño a jugadores, recompensas, etc.)
            # Por ahora solo loggeamos

    def _finalizar_turno_activo(self):
        """Finaliza el turno activo y pasa al siguiente"""
        color_actual = "rojos" if self.estado_actual == EstadoTurno.ROJOS_ACTIVOS else "azules"

        # NUEVO: Log de estado de combates
        if self.manager_combates:
            stats = self.manager_combates.obtener_estadisticas_globales()
            log_evento(f"🔚 Finalizando turno de {color_actual} - Combates activos: {stats['combates_activos']}")

        # IMPORTANTE: Los combates NO se detienen al cambiar turno
        # Continúan corriendo en el motor de tiempo real

        # Cambiar al otro color
        if self.estado_actual == EstadoTurno.ROJOS_ACTIVOS:
            self._cambiar_a_estado(EstadoTurno.AZULES_ACTIVOS)
        else:
            # Completamos un ciclo completo (rojo + azul)
            self.turno_numero += 1
            self._cambiar_a_estado(EstadoTurno.ROJOS_ACTIVOS)

    def _ejecutar_transicion(self) -> bool:
        """Ejecuta período de transición entre turnos"""
        # Por ahora transición instantánea
        # Aquí se podrían resolver efectos automáticos, etc.
        log_evento("🔄 Procesando transición...")
        return True

    def _verificar_condiciones_victoria(self) -> bool:
        """Verifica si algún color ha ganado"""
        jugadores_rojos = self.mapa.obtener_jugadores_activos("roja")
        jugadores_azules = self.mapa.obtener_jugadores_activos("azul")

        # Verificar si un color se quedó sin jugadores
        if not jugadores_rojos and jugadores_azules:
            self._finalizar_juego("victoria_azules")
            return True
        elif not jugadores_azules and jugadores_rojos:
            self._finalizar_juego("victoria_rojos")
            return True
        elif not jugadores_rojos and not jugadores_azules:
            self._finalizar_juego("empate")
            return True

        return False

    def _finalizar_juego(self, razon: str):
        """Finaliza el juego con una razón específica"""
        log_evento(f"🏁 Finalizando juego: {razon}")

        if razon == "victoria_rojos":
            self.ganador_color = "roja"
            log_evento("🔴 ¡VICTORIA DE LOS ROJOS!")
        elif razon == "victoria_azules":
            self.ganador_color = "azul"
            log_evento("🔵 ¡VICTORIA DE LOS AZULES!")
        elif razon == "empate":
            self.ganador_color = None
            log_evento("🤝 ¡EMPATE!")
        elif razon == "limite_turnos":
            self.ganador_color = None
            log_evento("⏰ Juego terminado por límite de turnos")

        # NUEVO: Finalizar todos los combates
        if self.manager_combates:
            combates_finalizados = 0
            for combate_id in list(self.manager_combates.combates_activos.keys()):
                self.manager_combates.finalizar_combate(combate_id)
                combates_finalizados += 1

            if combates_finalizados > 0:
                log_evento(f"🛑 {combates_finalizados} combates finalizados")

        self._cambiar_a_estado(EstadoTurno.FINALIZADO)

    def ordenar_ataque(self, jugador_id: int, atacante_carta_id: int, objetivo_carta_id: int) -> bool:
        """
        NUEVO: Ordena un ataque entre cartas (interfaz para jugadores)
        """
        if not self.esta_jugador_activo(jugador_id):
            log_evento(f"❌ Jugador {jugador_id} no puede dar órdenes (no está activo)")
            return False

        if not self.manager_combates:
            log_evento("❌ Manager de combates no disponible")
            return False

        # Delegar al manager de combates
        return self.manager_combates.ordenar_ataque(atacante_carta_id, objetivo_carta_id)

    def esta_jugador_activo(self, jugador_id: int) -> bool:
        """Verifica si un jugador puede dar órdenes actualmente"""
        return jugador_id in self.jugadores_activos

    def esta_jugador_pasivo(self, jugador_id: int) -> bool:
        """Verifica si un jugador está en modo pasivo"""
        return jugador_id in self.jugadores_pasivos

    def obtener_tiempo_restante(self) -> float:
        """Obtiene el tiempo restante del turno actual"""
        if self.estado_actual in [EstadoTurno.ROJOS_ACTIVOS, EstadoTurno.AZULES_ACTIVOS]:
            tiempo_transcurrido = time.time() - self.tiempo_inicio_turno
            return max(0, self.duracion_turno_segundos - tiempo_transcurrido)
        return 0

    def obtener_estado_sistema(self) -> Dict:
        """Obtiene el estado completo del sistema"""
        stats_combate = {}
        if self.manager_combates:
            stats_combate = self.manager_combates.obtener_estadisticas_globales()

        return {
            'estado_actual': self.estado_actual.value,
            'turno_numero': self.turno_numero,
            'tiempo_restante': self.obtener_tiempo_restante(),
            'jugadores_activos': list(self.jugadores_activos),
            'jugadores_pasivos': list(self.jugadores_pasivos),
            'juego_terminado': self.juego_terminado,
            'ganador_color': self.ganador_color,
            'duracion_turno': self.duracion_turno_segundos,
            'combates': stats_combate
        }

    def __str__(self):
        return f"SistemaTurnos(turno={self.turno_numero}, estado={self.estado_actual.value})"