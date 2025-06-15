"""
Configuración centralizada para el sistema de tiempo real
"""

from dataclasses import dataclass
from typing import Dict, Any
import json
import os
from src.utils.helpers import log_evento, cargar_json, guardar_json


@dataclass
class ConfiguracionMotor:
    """Configuración del motor de tiempo real"""
    fps_objetivo: int = 10
    max_componentes: int = 100
    max_eventos_programados: int = 200
    timeout_hilo_segundos: float = 2.0
    intervalo_stats_segundos: float = 1.0
    max_errores_por_componente: int = 5


@dataclass
class ConfiguracionComponentes:
    """Configuración para componentes"""
    intervalo_minimo_default: float = 0.0
    max_ticks_default: int = -1
    timeout_procesamiento_segundos: float = 0.1
    auto_limpiar_terminados: bool = True


@dataclass
class ConfiguracionTurnos:
    """Configuración específica para el sistema de turnos"""
    duracion_turno_segundos: int = 30
    tiempo_transicion_segundos: float = 2.0
    max_turnos_por_partida: int = 50
    fps_durante_combate: int = 10
    fps_durante_transicion: int = 5


class ConfiguradorTiempoReal:
    """Manejador de configuración para el sistema de tiempo real"""

    def __init__(self, archivo_config: str = "config/tiempo_real.json"):
        self.archivo_config = archivo_config
        self.motor = ConfiguracionMotor()
        self.componentes = ConfiguracionComponentes()
        self.turnos = ConfiguracionTurnos()

        # Intentar cargar configuración existente
        self.cargar_configuracion()

    def cargar_configuracion(self) -> bool:
        """Carga configuración desde archivo"""
        try:
            if not os.path.exists(self.archivo_config):
                log_evento(f"📋 Archivo de config no existe, usando valores por defecto")
                self.guardar_configuracion()  # Crear archivo con defaults
                return True

            datos = cargar_json(self.archivo_config)
            if not datos:
                log_evento(f"⚠️ Error cargando configuración, usando defaults")
                return False

            # Cargar configuración del motor
            if 'motor' in datos:
                motor_data = datos['motor']
                self.motor.fps_objetivo = motor_data.get('fps_objetivo', self.motor.fps_objetivo)
                self.motor.max_componentes = motor_data.get('max_componentes', self.motor.max_componentes)
                self.motor.max_eventos_programados = motor_data.get('max_eventos_programados',
                                                                    self.motor.max_eventos_programados)
                self.motor.timeout_hilo_segundos = motor_data.get('timeout_hilo_segundos',
                                                                  self.motor.timeout_hilo_segundos)
                self.motor.intervalo_stats_segundos = motor_data.get('intervalo_stats_segundos',
                                                                     self.motor.intervalo_stats_segundos)
                self.motor.max_errores_por_componente = motor_data.get('max_errores_por_componente',
                                                                       self.motor.max_errores_por_componente)

            # Cargar configuración de componentes
            if 'componentes' in datos:
                comp_data = datos['componentes']
                self.componentes.intervalo_minimo_default = comp_data.get('intervalo_minimo_default',
                                                                          self.componentes.intervalo_minimo_default)
                self.componentes.max_ticks_default = comp_data.get('max_ticks_default',
                                                                   self.componentes.max_ticks_default)
                self.componentes.timeout_procesamiento_segundos = comp_data.get('timeout_procesamiento_segundos',
                                                                                self.componentes.timeout_procesamiento_segundos)
                self.componentes.auto_limpiar_terminados = comp_data.get('auto_limpiar_terminados',
                                                                         self.componentes.auto_limpiar_terminados)

            # Cargar configuración de turnos
            if 'turnos' in datos:
                turnos_data = datos['turnos']
                self.turnos.duracion_turno_segundos = turnos_data.get('duracion_turno_segundos',
                                                                      self.turnos.duracion_turno_segundos)
                self.turnos.tiempo_transicion_segundos = turnos_data.get('tiempo_transicion_segundos',
                                                                         self.turnos.tiempo_transicion_segundos)
                self.turnos.max_turnos_por_partida = turnos_data.get('max_turnos_por_partida',
                                                                     self.turnos.max_turnos_por_partida)
                self.turnos.fps_durante_combate = turnos_data.get('fps_durante_combate',
                                                                  self.turnos.fps_durante_combate)
                self.turnos.fps_durante_transicion = turnos_data.get('fps_durante_transicion',
                                                                     self.turnos.fps_durante_transicion)

            log_evento(f"✅ Configuración cargada desde {self.archivo_config}")
            return True

        except Exception as e:
            log_evento(f"❌ Error cargando configuración: {e}")
            return False

    def guardar_configuracion(self) -> bool:
        """Guarda la configuración actual al archivo"""
        try:
            datos = {
                'motor': {
                    'fps_objetivo': self.motor.fps_objetivo,
                    'max_componentes': self.motor.max_componentes,
                    'max_eventos_programados': self.motor.max_eventos_programados,
                    'timeout_hilo_segundos': self.motor.timeout_hilo_segundos,
                    'intervalo_stats_segundos': self.motor.intervalo_stats_segundos,
                    'max_errores_por_componente': self.motor.max_errores_por_componente
                },
                'componentes': {
                    'intervalo_minimo_default': self.componentes.intervalo_minimo_default,
                    'max_ticks_default': self.componentes.max_ticks_default,
                    'timeout_procesamiento_segundos': self.componentes.timeout_procesamiento_segundos,
                    'auto_limpiar_terminados': self.componentes.auto_limpiar_terminados
                },
                'turnos': {
                    'duracion_turno_segundos': self.turnos.duracion_turno_segundos,
                    'tiempo_transicion_segundos': self.turnos.tiempo_transicion_segundos,
                    'max_turnos_por_partida': self.turnos.max_turnos_por_partida,
                    'fps_durante_combate': self.turnos.fps_durante_combate,
                    'fps_durante_transicion': self.turnos.fps_durante_transicion
                }
            }

            return guardar_json(datos, self.archivo_config)

        except Exception as e:
            log_evento(f"❌ Error guardando configuración: {e}")
            return False

    def configurar_motor(self, fps_objetivo: int = None, max_componentes: int = None,
                         max_eventos: int = None) -> bool:
        """Configura parámetros del motor"""
        try:
            if fps_objetivo is not None:
                if not (1 <= fps_objetivo <= 60):
                    raise ValueError(f"FPS debe estar entre 1-60, recibido: {fps_objetivo}")
                self.motor.fps_objetivo = fps_objetivo

            if max_componentes is not None:
                if max_componentes < 1:
                    raise ValueError(f"max_componentes debe ser > 0")
                self.motor.max_componentes = max_componentes

            if max_eventos is not None:
                if max_eventos < 1:
                    raise ValueError(f"max_eventos debe ser > 0")
                self.motor.max_eventos_programados = max_eventos

            log_evento(f"🔧 Configuración del motor actualizada")
            return True

        except Exception as e:
            log_evento(f"❌ Error configurando motor: {e}")
            return False

    def configurar_turnos(self, duracion_turno: int = None, tiempo_transicion: float = None,
                          fps_combate: int = None) -> bool:
        """Configura parámetros del sistema de turnos"""
        try:
            if duracion_turno is not None:
                if not (5 <= duracion_turno <= 300):
                    raise ValueError(f"Duración turno debe estar entre 5-300s")
                self.turnos.duracion_turno_segundos = duracion_turno

            if tiempo_transicion is not None:
                if not (0.1 <= tiempo_transicion <= 10.0):
                    raise ValueError(f"Tiempo transición debe estar entre 0.1-10s")
                self.turnos.tiempo_transicion_segundos = tiempo_transicion

            if fps_combate is not None:
                if not (1 <= fps_combate <= 60):
                    raise ValueError(f"FPS combate debe estar entre 1-60")
                self.turnos.fps_durante_combate = fps_combate

            log_evento(f"🔧 Configuración de turnos actualizada")
            return True

        except Exception as e:
            log_evento(f"❌ Error configurando turnos: {e}")
            return False

    def obtener_config_completa(self) -> Dict[str, Any]:
        """Obtiene toda la configuración como diccionario"""
        return {
            'motor': {
                'fps_objetivo': self.motor.fps_objetivo,
                'max_componentes': self.motor.max_componentes,
                'max_eventos_programados': self.motor.max_eventos_programados,
                'timeout_hilo_segundos': self.motor.timeout_hilo_segundos,
                'intervalo_stats_segundos': self.motor.intervalo_stats_segundos,
                'max_errores_por_componente': self.motor.max_errores_por_componente
            },
            'componentes': {
                'intervalo_minimo_default': self.componentes.intervalo_minimo_default,
                'max_ticks_default': self.componentes.max_ticks_default,
                'timeout_procesamiento_segundos': self.componentes.timeout_procesamiento_segundos,
                'auto_limpiar_terminados': self.componentes.auto_limpiar_terminados
            },
            'turnos': {
                'duracion_turno_segundos': self.turnos.duracion_turno_segundos,
                'tiempo_transicion_segundos': self.turnos.tiempo_transicion_segundos,
                'max_turnos_por_partida': self.turnos.max_turnos_por_partida,
                'fps_durante_combate': self.turnos.fps_durante_combate,
                'fps_durante_transicion': self.turnos.fps_durante_transicion
            }
        }

    def resetear_a_defaults(self):
        """Resetea toda la configuración a valores por defecto"""
        self.motor = ConfiguracionMotor()
        self.componentes = ConfiguracionComponentes()
        self.turnos = ConfiguracionTurnos()
        log_evento("🔄 Configuración reseteada a valores por defecto")

    def validar_configuracion(self) -> bool:
        """Valida que la configuración actual sea coherente"""
        try:
            # Validar motor
            if not (1 <= self.motor.fps_objetivo <= 60):
                raise ValueError(f"FPS objetivo inválido: {self.motor.fps_objetivo}")

            if self.motor.max_componentes < 1:
                raise ValueError(f"max_componentes debe ser > 0")

            # Validar turnos
            if self.turnos.duracion_turno_segundos < 5:
                raise ValueError(f"Duración turno muy corta: {self.turnos.duracion_turno_segundos}")

            if self.turnos.tiempo_transicion_segundos < 0.1:
                raise ValueError(f"Tiempo transición muy corto")

            # Validar coherencia entre configuraciones
            if self.turnos.fps_durante_combate > self.motor.fps_objetivo * 2:
                log_evento("⚠️ FPS de combate muy alto comparado con FPS objetivo")

            log_evento("✅ Configuración validada correctamente")
            return True

        except Exception as e:
            log_evento(f"❌ Configuración inválida: {e}")
            return False


# Instancia global del configurador (singleton)
configurador_tiempo_real = ConfiguradorTiempoReal()