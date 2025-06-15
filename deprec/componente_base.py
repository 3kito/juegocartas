"""
Clases base para componentes que se procesan en tiempo real
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum
import time
from src.utils.helpers import log_evento


class EstadoComponente(Enum):
    """Estados posibles de un componente"""
    ACTIVO = "activo"
    PAUSADO = "pausado"
    TERMINADO = "terminado"
    ERROR = "error"


class ComponenteBaseTiempoReal(ABC):
    """Clase base para todos los componentes de tiempo real"""

    def __init__(self, id_componente: str):
        self.id_componente = id_componente
        self.estado = EstadoComponente.ACTIVO
        self.tiempo_creacion = time.time()
        self.tiempo_ultimo_tick = 0.0
        self.total_ticks_procesados = 0
        self.tiempo_total_procesamiento = 0.0

        # Configuración
        self.max_ticks = -1  # -1 = infinito
        self.intervalo_minimo = 0.0  # Tiempo mínimo entre ticks

        # Estadísticas
        self.stats = {
            'ticks_procesados': 0,
            'tiempo_procesamiento_total': 0.0,
            'tiempo_procesamiento_promedio': 0.0,
            'errores': 0
        }

    def procesar_tick(self, delta_time: float) -> bool:
        """
        Método principal llamado por el motor
        NO sobreescribir este método, usar _procesar_tick_interno
        """
        if self.estado != EstadoComponente.ACTIVO:
            return self.estado != EstadoComponente.TERMINADO

        # Verificar intervalo mínimo
        tiempo_actual = time.time()
        if self.intervalo_minimo > 0:
            if tiempo_actual - self.tiempo_ultimo_tick < self.intervalo_minimo:
                return True  # Saltar este tick

        # Verificar límite de ticks
        if self.max_ticks > 0 and self.total_ticks_procesados >= self.max_ticks:
            self._terminar_componente()
            return False

        try:
            inicio_procesamiento = time.time()

            # Llamar al método específico del componente
            resultado = self._procesar_tick_interno(delta_time)

            # Actualizar estadísticas
            tiempo_procesamiento = time.time() - inicio_procesamiento
            self._actualizar_estadisticas(tiempo_procesamiento)

            self.tiempo_ultimo_tick = tiempo_actual
            self.total_ticks_procesados += 1

            return resultado

        except Exception as e:
            self.stats['errores'] += 1
            log_evento(f"❌ Error en componente {self.id_componente}: {e}")

            if self.stats['errores'] >= 5:  # Límite de errores
                self._terminar_componente()
                return False

            return True  # Continuar a pesar del error

    @abstractmethod
    def _procesar_tick_interno(self, delta_time: float) -> bool:
        """
        Lógica específica del componente

        Args:
            delta_time: Tiempo desde último tick

        Returns:
            bool: True si debe continuar, False si debe terminar
        """
        pass

    def obtener_id_componente(self) -> str:
        """Retorna el ID único del componente"""
        return self.id_componente

    def pausar(self):
        """Pausa el procesamiento del componente"""
        if self.estado == EstadoComponente.ACTIVO:
            self.estado = EstadoComponente.PAUSADO
            log_evento(f"⏸️ Componente {self.id_componente} pausado")

    def reanudar(self):
        """Reanuda el procesamiento del componente"""
        if self.estado == EstadoComponente.PAUSADO:
            self.estado = EstadoComponente.ACTIVO
            log_evento(f"▶️ Componente {self.id_componente} reanudado")

    def terminar(self):
        """Termina el componente manualmente"""
        self._terminar_componente()

    def _terminar_componente(self):
        """Marca el componente como terminado"""
        if self.estado != EstadoComponente.TERMINADO:
            self.estado = EstadoComponente.TERMINADO
            self._al_terminar()
            log_evento(f"🔚 Componente {self.id_componente} terminado")

    def _al_terminar(self):
        """Método llamado cuando el componente termina (opcional de sobreescribir)"""
        pass

    def _actualizar_estadisticas(self, tiempo_procesamiento: float):
        """Actualiza las estadísticas del componente"""
        self.stats['ticks_procesados'] += 1
        self.stats['tiempo_procesamiento_total'] += tiempo_procesamiento

        if self.stats['ticks_procesados'] > 0:
            self.stats['tiempo_procesamiento_promedio'] = (
                    self.stats['tiempo_procesamiento_total'] / self.stats['ticks_procesados']
            )

    def configurar_limite_ticks(self, max_ticks: int):
        """Configura el límite máximo de ticks"""
        self.max_ticks = max_ticks

    def configurar_intervalo_minimo(self, intervalo: float):
        """Configura el intervalo mínimo entre ticks"""
        self.intervalo_minimo = intervalo

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del componente"""
        tiempo_vida = time.time() - self.tiempo_creacion

        return {
            'id': self.id_componente,
            'estado': self.estado.value,
            'tiempo_vida': tiempo_vida,
            'total_ticks': self.total_ticks_procesados,
            'max_ticks': self.max_ticks,
            'intervalo_minimo': self.intervalo_minimo,
            'stats': self.stats.copy()
        }

    def esta_activo(self) -> bool:
        """Verifica si el componente está activo"""
        return self.estado == EstadoComponente.ACTIVO

    def esta_terminado(self) -> bool:
        """Verifica si el componente ha terminado"""
        return self.estado == EstadoComponente.TERMINADO

    def __str__(self):
        return f"{self.__class__.__name__}({self.id_componente}, {self.estado.value})"

    def __repr__(self):
        return f"{self.__class__.__name__}(id='{self.id_componente}', ticks={self.total_ticks_procesados})"


class ComponenteSimple(ComponenteBaseTiempoReal):
    """Componente simple para tareas básicas con callback"""

    def __init__(self, id_componente: str, callback_tick, parametros: Dict[str, Any] = None):
        super().__init__(id_componente)
        self.callback_tick = callback_tick
        self.parametros = parametros or {}

    def _procesar_tick_interno(self, delta_time: float) -> bool:
        """Ejecuta el callback configurado"""
        try:
            if self.callback_tick:
                return self.callback_tick(delta_time, **self.parametros)
            return True
        except Exception as e:
            log_evento(f"❌ Error en callback de {self.id_componente}: {e}")
            return False


class ComponenteTemporizado(ComponenteBaseTiempoReal):
    """Componente que se ejecuta por un tiempo específico"""

    def __init__(self, id_componente: str, duracion_segundos: float, callback_tick=None):
        super().__init__(id_componente)
        self.duracion_segundos = duracion_segundos
        self.tiempo_limite = self.tiempo_creacion + duracion_segundos
        self.callback_tick = callback_tick

    def _procesar_tick_interno(self, delta_time: float) -> bool:
        """Verifica si aún está dentro del tiempo límite"""
        tiempo_actual = time.time()

        if tiempo_actual >= self.tiempo_limite:
            return False  # Tiempo agotado

        # Ejecutar callback si existe
        if self.callback_tick:
            try:
                return self.callback_tick(delta_time, tiempo_restante=self.tiempo_limite - tiempo_actual)
            except Exception as e:
                log_evento(f"❌ Error en callback temporizado {self.id_componente}: {e}")
                return False

        return True

    def obtener_tiempo_restante(self) -> float:
        """Obtiene el tiempo restante en segundos"""
        return max(0, self.tiempo_limite - time.time())

    def esta_vencido(self) -> bool:
        """Verifica si el tiempo se agotó"""
        return time.time() >= self.tiempo_limite


class ComponentePeriodico(ComponenteBaseTiempoReal):
    """Componente que ejecuta una acción cada cierto intervalo"""

    def __init__(self, id_componente: str, intervalo_segundos: float, callback_periodico,
                 max_ejecuciones: int = -1):
        super().__init__(id_componente)
        self.intervalo_segundos = intervalo_segundos
        self.callback_periodico = callback_periodico
        self.max_ejecuciones = max_ejecuciones
        self.ejecuciones_realizadas = 0
        self.proxima_ejecucion = self.tiempo_creacion + intervalo_segundos

    def _procesar_tick_interno(self, delta_time: float) -> bool:
        """Ejecuta el callback si es momento de hacerlo"""
        tiempo_actual = time.time()

        if tiempo_actual >= self.proxima_ejecucion:
            try:
                # Ejecutar callback
                resultado = self.callback_periodico(
                    ejecucion_num=self.ejecuciones_realizadas + 1,
                    delta_time=delta_time
                )

                self.ejecuciones_realizadas += 1
                self.proxima_ejecucion = tiempo_actual + self.intervalo_segundos

                # Verificar límite de ejecuciones
                if (self.max_ejecuciones > 0 and
                        self.ejecuciones_realizadas >= self.max_ejecuciones):
                    return False

                # Si el callback retorna False, terminar
                if resultado is False:
                    return False

            except Exception as e:
                log_evento(f"❌ Error en callback periódico {self.id_componente}: {e}")
                return False

        return True

    def obtener_tiempo_hasta_proxima(self) -> float:
        """Tiempo hasta la próxima ejecución"""
        return max(0, self.proxima_ejecucion - time.time())


class GestorComponentes:
    """Gestor auxiliar para manejar múltiples componentes"""

    def __init__(self):
        self.componentes: Dict[str, ComponenteBaseTiempoReal] = {}

    def crear_componente_simple(self, id_componente: str, callback_tick,
                                parametros: Dict[str, Any] = None) -> ComponenteSimple:
        """Crea y registra un componente simple"""
        componente = ComponenteSimple(id_componente, callback_tick, parametros)
        self.componentes[id_componente] = componente
        return componente

    def crear_componente_temporizado(self, id_componente: str, duracion_segundos: float,
                                     callback_tick=None) -> ComponenteTemporizado:
        """Crea y registra un componente temporizado"""
        componente = ComponenteTemporizado(id_componente, duracion_segundos, callback_tick)
        self.componentes[id_componente] = componente
        return componente

    def crear_componente_periodico(self, id_componente: str, intervalo_segundos: float,
                                   callback_periodico, max_ejecuciones: int = -1) -> ComponentePeriodico:
        """Crea y registra un componente periódico"""
        componente = ComponentePeriodico(id_componente, intervalo_segundos,
                                         callback_periodico, max_ejecuciones)
        self.componentes[id_componente] = componente
        return componente

    def obtener_componente(self, id_componente: str) -> Optional[ComponenteBaseTiempoReal]:
        """Obtiene un componente por ID"""
        return self.componentes.get(id_componente)

    def remover_componente(self, id_componente: str) -> bool:
        """Remueve un componente"""
        if id_componente in self.componentes:
            del self.componentes[id_componente]
            return True
        return False

    def obtener_componentes_activos(self) -> Dict[str, ComponenteBaseTiempoReal]:
        """Obtiene solo los componentes activos"""
        return {id_comp: comp for id_comp, comp in self.componentes.items()
                if comp.esta_activo()}

    def obtener_estadisticas_globales(self) -> Dict[str, Any]:
        """Obtiene estadísticas de todos los componentes"""
        total_componentes = len(self.componentes)
        componentes_activos = len(self.obtener_componentes_activos())

        return {
            'total_componentes': total_componentes,
            'componentes_activos': componentes_activos,
            'componentes_terminados': total_componentes - componentes_activos,
            'componentes_por_tipo': self._contar_por_tipo()
        }

    def _contar_por_tipo(self) -> Dict[str, int]:
        """Cuenta componentes por tipo"""
        conteo = {}
        for comp in self.componentes.values():
            tipo = comp.__class__.__name__
            conteo[tipo] = conteo.get(tipo, 0) + 1
        return conteo