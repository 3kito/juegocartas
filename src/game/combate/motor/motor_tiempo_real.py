"""
Motor de tiempo real para procesamiento continuo de componentes
Maneja tick rate, callbacks programados y componentes activos
"""

import time
import threading
from typing import Dict, List, Optional, Callable, Any, Protocol
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from src.utils.helpers import log_evento


class EstadoMotor(Enum):
    """Estados del motor de tiempo real"""
    DETENIDO = "detenido"
    EJECUTANDO = "ejecutando"
    PAUSADO = "pausado"
    ERROR = "error"


@dataclass
class EventoProgramado:
    """Representa un evento programado para ejecutarse después de un delay"""
    id_evento: str
    callback: Callable
    tiempo_ejecucion: float
    parametros: Dict[str, Any]
    recurrente: bool = False
    intervalo: float = 0.0
    activo: bool = True


class ComponenteTiempoReal(Protocol):
    """Protocolo que deben implementar los componentes procesados en tiempo real"""

    def procesar_tick(self, delta_time: float) -> bool:
        """
        Procesa un tick del componente

        Args:
            delta_time: Tiempo transcurrido desde el último tick en segundos

        Returns:
            bool: True si el componente sigue activo, False si debe ser removido
        """
        ...

    def obtener_id_componente(self) -> str:
        """Retorna un ID único para este componente"""
        ...


class MotorTiempoReal:
    """Motor principal para procesamiento continuo en tiempo real"""

    def __init__(self, fps_objetivo: int = 10):
        # Configuración básica
        self.fps_objetivo = fps_objetivo
        self.intervalo_tick = 1.0 / fps_objetivo

        # Estado del motor
        self.estado = EstadoMotor.DETENIDO
        self.ejecutando = False
        self.pausado = False

        # Control de tiempo
        self.ultimo_tick = 0.0
        self.tiempo_inicio = 0.0
        self.total_ticks = 0
        self.fps_actual = 0.0

        # Componentes y eventos
        self.componentes_activos: Dict[str, ComponenteTiempoReal] = {}
        self.eventos_programados: Dict[str, EventoProgramado] = {}
        self.contador_eventos = 0

        # Threading
        self.hilo_motor: Optional[threading.Thread] = None
        self.lock = threading.Lock()

        # Estadísticas
        self.stats = {
            'ticks_procesados': 0,
            'componentes_procesados': 0,
            'eventos_ejecutados': 0,
            'tiempo_total_ejecucion': 0.0,
            'promedio_fps': 0.0
        }

    def iniciar(self) -> bool:
        """Inicia el motor de tiempo real"""
        if self.estado == EstadoMotor.EJECUTANDO:
            log_evento("⚠️ Motor ya está ejecutándose")
            return False

        try:
            self.estado = EstadoMotor.EJECUTANDO
            self.ejecutando = True
            self.pausado = False
            self.tiempo_inicio = time.time()
            self.ultimo_tick = self.tiempo_inicio

            # Iniciar hilo de procesamiento
            self.hilo_motor = threading.Thread(target=self._loop_principal, daemon=True)
            self.hilo_motor.start()

            log_evento(f"🚀 Motor de tiempo real iniciado ({self.fps_objetivo} FPS)")
            return True

        except Exception as e:
            self.estado = EstadoMotor.ERROR
            log_evento(f"❌ Error iniciando motor: {e}")
            return False

    def detener(self):
        """Detiene el motor de tiempo real"""
        if self.estado != EstadoMotor.EJECUTANDO:
            return

        log_evento("🛑 Deteniendo motor de tiempo real...")

        self.ejecutando = False
        self.estado = EstadoMotor.DETENIDO

        # Esperar que termine el hilo
        if self.hilo_motor and self.hilo_motor.is_alive():
            self.hilo_motor.join(timeout=2.0)

        self._actualizar_estadisticas_finales()
        log_evento(f"✅ Motor detenido. Total ticks: {self.stats['ticks_procesados']}")

    def pausar(self):
        """Pausa el procesamiento del motor"""
        if self.estado == EstadoMotor.EJECUTANDO:
            self.pausado = True
            self.estado = EstadoMotor.PAUSADO
            log_evento("⏸️ Motor pausado")

    def reanudar(self):
        """Reanuda el procesamiento del motor"""
        if self.estado == EstadoMotor.PAUSADO:
            self.pausado = False
            self.estado = EstadoMotor.EJECUTANDO
            self.ultimo_tick = time.time()  # Resetear tiempo para evitar salto grande
            log_evento("▶️ Motor reanudado")

    def agregar_componente(self, componente: ComponenteTiempoReal) -> bool:
        """Agrega un componente para procesamiento continuo"""
        try:
            id_componente = componente.obtener_id_componente()

            with self.lock:
                if id_componente in self.componentes_activos:
                    log_evento(f"⚠️ Componente {id_componente} ya existe")
                    return False

                self.componentes_activos[id_componente] = componente

            log_evento(f"➕ Componente agregado: {id_componente}")
            return True

        except Exception as e:
            log_evento(f"❌ Error agregando componente: {e}")
            return False

    def remover_componente(self, id_componente: str) -> bool:
        """Remueve un componente del procesamiento"""
        with self.lock:
            if id_componente in self.componentes_activos:
                del self.componentes_activos[id_componente]
                log_evento(f"➖ Componente removido: {id_componente}")
                return True

        return False

    def programar_evento(self, callback: Callable, delay_segundos: float,
                         parametros: Dict[str, Any] = None,
                         recurrente: bool = False,
                         intervalo: float = 0.0) -> str:
        """
        Programa un evento para ejecutarse después de un delay

        Args:
            callback: Función a ejecutar
            delay_segundos: Delay en segundos antes de ejecutar
            parametros: Parámetros para pasar al callback
            recurrente: Si el evento debe repetirse
            intervalo: Intervalo entre repeticiones (solo si recurrente=True)

        Returns:
            str: ID del evento programado
        """
        self.contador_eventos += 1
        id_evento = f"evento_{self.contador_eventos}"

        tiempo_ejecucion = time.time() + delay_segundos

        evento = EventoProgramado(
            id_evento=id_evento,
            callback=callback,
            tiempo_ejecucion=tiempo_ejecucion,
            parametros=parametros or {},
            recurrente=recurrente,
            intervalo=intervalo
        )

        with self.lock:
            self.eventos_programados[id_evento] = evento

        log_evento(f"⏰ Evento programado: {id_evento} (en {delay_segundos}s)")
        return id_evento

    def cancelar_evento(self, id_evento: str) -> bool:
        """Cancela un evento programado"""
        with self.lock:
            if id_evento in self.eventos_programados:
                self.eventos_programados[id_evento].activo = False
                log_evento(f"🚫 Evento cancelado: {id_evento}")
                return True

        return False

    def _loop_principal(self):
        """Loop principal del motor (ejecutado en hilo separado)"""
        log_evento(f"🔄 Loop principal iniciado (Objetivo: {self.fps_objetivo} FPS)")

        try:
            while self.ejecutando:
                inicio_tick = time.time()

                if not self.pausado:
                    self._procesar_tick()
                else:
                    # Si está pausado, esperar un poco y continuar
                    time.sleep(0.1)
                    continue

                # Control de frame rate
                tiempo_procesamiento = time.time() - inicio_tick
                tiempo_espera = max(0, self.intervalo_tick - tiempo_procesamiento)

                if tiempo_espera > 0:
                    time.sleep(tiempo_espera)

                # Actualizar estadísticas de FPS
                self._actualizar_fps()

        except Exception as e:
            log_evento(f"❌ Error en loop principal: {e}")
            self.estado = EstadoMotor.ERROR

        log_evento("🏁 Loop principal terminado")

    def _procesar_tick(self):
        """Procesa un tick completo del sistema"""
        tiempo_actual = time.time()
        delta_time = tiempo_actual - self.ultimo_tick
        self.ultimo_tick = tiempo_actual

        # Procesar componentes activos
        self._procesar_componentes(delta_time)

        # Procesar eventos programados
        self._procesar_eventos()

        # Actualizar contadores
        self.total_ticks += 1
        self.stats['ticks_procesados'] += 1

    def _procesar_componentes(self, delta_time: float):
        """Procesa todos los componentes activos"""
        componentes_a_remover = []

        with self.lock:
            componentes = list(self.componentes_activos.items())

        for id_componente, componente in componentes:
            try:
                # Procesar componente
                sigue_activo = componente.procesar_tick(delta_time)

                if not sigue_activo:
                    componentes_a_remover.append(id_componente)

                self.stats['componentes_procesados'] += 1

            except Exception as e:
                log_evento(f"❌ Error procesando componente {id_componente}: {e}")
                componentes_a_remover.append(id_componente)

        # Remover componentes inactivos
        for id_componente in componentes_a_remover:
            self.remover_componente(id_componente)

    def _procesar_eventos(self):
        """Procesa eventos programados que deben ejecutarse"""
        tiempo_actual = time.time()
        eventos_a_remover = []
        eventos_a_reprogramar = []

        with self.lock:
            eventos = list(self.eventos_programados.items())

        for id_evento, evento in eventos:
            if not evento.activo:
                eventos_a_remover.append(id_evento)
                continue

            if tiempo_actual >= evento.tiempo_ejecucion:
                try:
                    # Ejecutar callback
                    evento.callback(**evento.parametros)
                    self.stats['eventos_ejecutados'] += 1

                    if evento.recurrente and evento.intervalo > 0:
                        # Reprogramar evento recurrente
                        evento.tiempo_ejecucion = tiempo_actual + evento.intervalo
                        eventos_a_reprogramar.append(evento)
                    else:
                        eventos_a_remover.append(id_evento)

                except Exception as e:
                    log_evento(f"❌ Error ejecutando evento {id_evento}: {e}")
                    eventos_a_remover.append(id_evento)

        # Limpiar eventos completados
        with self.lock:
            for id_evento in eventos_a_remover:
                self.eventos_programados.pop(id_evento, None)

    def _actualizar_fps(self):
        """Actualiza las estadísticas de FPS"""
        if self.total_ticks % 10 == 0:  # Actualizar cada 10 ticks
            tiempo_transcurrido = time.time() - self.tiempo_inicio
            if tiempo_transcurrido > 0:
                self.fps_actual = self.total_ticks / tiempo_transcurrido

    def _actualizar_estadisticas_finales(self):
        """Actualiza estadísticas finales al detener el motor"""
        tiempo_total = time.time() - self.tiempo_inicio
        self.stats['tiempo_total_ejecucion'] = tiempo_total

        if tiempo_total > 0:
            self.stats['promedio_fps'] = self.stats['ticks_procesados'] / tiempo_total

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas actuales del motor"""
        tiempo_ejecucion = time.time() - self.tiempo_inicio if self.tiempo_inicio > 0 else 0

        return {
            'estado': self.estado.value,
            'fps_objetivo': self.fps_objetivo,
            'fps_actual': self.fps_actual,
            'componentes_activos': len(self.componentes_activos),
            'eventos_programados': len(self.eventos_programados),
            'tiempo_ejecucion': tiempo_ejecucion,
            'total_ticks': self.total_ticks,
            'stats_detalladas': self.stats.copy()
        }

    def configurar_fps(self, nuevo_fps: int):
        """Cambia el FPS objetivo del motor"""
        if nuevo_fps < 1 or nuevo_fps > 60:
            log_evento(f"⚠️ FPS inválido: {nuevo_fps} (debe estar entre 1-60)")
            return

        self.fps_objetivo = nuevo_fps
        self.intervalo_tick = 1.0 / nuevo_fps
        log_evento(f"🔧 FPS objetivo cambiado a: {nuevo_fps}")

    def obtener_componentes_activos(self) -> List[str]:
        """Obtiene lista de IDs de componentes activos"""
        with self.lock:
            return list(self.componentes_activos.keys())

    def obtener_eventos_programados(self) -> List[str]:
        """Obtiene lista de IDs de eventos programados"""
        with self.lock:
            return [id_evento for id_evento, evento in self.eventos_programados.items()
                    if evento.activo]

    def tick(self):
        """Ejecuta un ciclo de actualización manual (solo para testing)."""
        self._procesar_tick()
    def __str__(self):
        return f"MotorTiempoReal(estado={self.estado.value}, fps={self.fps_actual:.1f}, componentes={len(self.componentes_activos)})"

    def __repr__(self):
        return f"MotorTiempoReal(fps_objetivo={self.fps_objetivo}, total_ticks={self.total_ticks})"