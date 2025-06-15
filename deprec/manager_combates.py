"""
Manager que gestiona múltiples combates simultáneos
"""

import time
from typing import Dict, List, Optional, Set
from deprec.componente_base import ComponenteBaseTiempoReal
from deprec.combate_multiple import CombateMultiple, ResultadoCombateMultiple
from src.game.cartas.carta_base import CartaBase
from src.utils.helpers import log_evento


class ManagerCombates(ComponenteBaseTiempoReal):
   """Gestiona múltiples combates simultáneos"""

   def __init__(self):
       super().__init__("manager_combates")

       # Combates activos
       self.combates_activos: Dict[str, CombateMultiple] = {}

       # Resultados de combates terminados
       self.resultados_pendientes: List[ResultadoCombateMultiple] = []

       # Control de cartas
       self.cartas_en_combate: Set[int] = set()  # IDs de cartas que están en algún combate

       # Estadísticas globales
       self.total_combates_creados = 0
       self.total_combates_finalizados = 0
       self.tiempo_inicio_manager = time.time()

       # Configuración
       self.max_combates_simultaneos = 10
       self.auto_limpiar_resultados = True
       self.max_resultados_pendientes = 50

       log_evento("🎮 Manager de combates iniciado")

   def crear_combate(self, cartas_iniciales: List[CartaBase] = None) -> Optional[str]:
       """
       Crea un nuevo combate múltiple

       Args:
           cartas_iniciales: Lista opcional de cartas para agregar al combate

       Returns:
           str: ID del combate creado, None si falló
       """
       if len(self.combates_activos) >= self.max_combates_simultaneos:
           log_evento(f"⚠️ Límite de combates simultáneos alcanzado ({self.max_combates_simultaneos})")
           return None

       # Crear nuevo combate
       self.total_combates_creados += 1
       combate = CombateMultiple(f"combate_{self.total_combates_creados}")

       # Agregar cartas iniciales si se proporcionaron
       if cartas_iniciales:
           cartas_agregadas = 0
           for carta in cartas_iniciales:
               if self._puede_agregar_carta_a_combate(carta):
                   if combate.agregar_carta(carta):
                       self.cartas_en_combate.add(carta.id)
                       cartas_agregadas += 1

           log_evento(f"🥊 Combate {combate.id_componente} creado con {cartas_agregadas} cartas")

       # Registrar combate
       self.combates_activos[combate.id_componente] = combate

       return combate.id_componente

   def agregar_carta_a_combate(self, combate_id: str, carta: CartaBase) -> bool:
       """Agrega una carta a un combate específico"""
       if combate_id not in self.combates_activos:
           log_evento(f"❌ Combate {combate_id} no existe")
           return False

       if not self._puede_agregar_carta_a_combate(carta):
           return False

       combate = self.combates_activos[combate_id]

       if combate.agregar_carta(carta):
           self.cartas_en_combate.add(carta.id)
           return True

       return False

   def remover_carta_de_combate(self, carta_id: int) -> bool:
       """Remueve una carta de cualquier combate donde esté"""
       carta_removida = False

       for combate in self.combates_activos.values():
           if combate.esta_carta_en_combate(carta_id):
               if combate.remover_carta(carta_id):
                   carta_removida = True

       if carta_removida:
           self.cartas_en_combate.discard(carta_id)
           log_evento(f"➖ Carta {carta_id} removida de combates")

       return carta_removida

   def ordenar_ataque(self, atacante_id: int, objetivo_id: int) -> bool:
       """
       Ordena que una carta ataque a otra

       Si las cartas no están en el mismo combate, crea uno nuevo
       """
       # Buscar en qué combates están las cartas
       combate_atacante = self._encontrar_combate_de_carta(atacante_id)
       combate_objetivo = self._encontrar_combate_de_carta(objetivo_id)

       # Si ambas están en el mismo combate, ordenar ataque directo
       if combate_atacante and combate_objetivo and combate_atacante == combate_objetivo:
           return combate_atacante.ordenar_ataque(atacante_id, objetivo_id)

       # Si están en combates diferentes o alguna no está en combate,
       # crear nuevo combate o mover cartas
       return self._gestionar_ataque_entre_combates(atacante_id, objetivo_id)

   def _gestionar_ataque_entre_combates(self, atacante_id: int, objetivo_id: int) -> bool:
       """Gestiona ataque cuando las cartas están en combates diferentes"""
       # Por simplicidad, crear un nuevo combate con ambas cartas
       # (en una implementación más compleja, podrías fusionar combates)

       # Remover cartas de combates actuales
       self.remover_carta_de_combate(atacante_id)
       self.remover_carta_de_combate(objetivo_id)

       # Buscar las cartas (esto requeriría acceso a un registry de cartas)
       # Por ahora, devolver False - será manejado por sistema superior
       log_evento(f"⚠️ Ataque entre combates diferentes no implementado aún: {atacante_id} → {objetivo_id}")
       return False

   def obtener_combate_de_carta(self, carta_id: int) -> Optional[CombateMultiple]:
       """Obtiene el combate donde está una carta"""
       return self._encontrar_combate_de_carta(carta_id)

   def finalizar_combate(self, combate_id: str) -> Optional[ResultadoCombateMultiple]:
       """Finaliza un combate específico"""
       if combate_id not in self.combates_activos:
           return None

       combate = self.combates_activos[combate_id]
       resultado = combate.finalizar_combate()

       # Remover combate de activos
       del self.combates_activos[combate_id]
       self.total_combates_finalizados += 1

       # Limpiar cartas del registro
       for carta_id in resultado.cartas_participantes:
           self.cartas_en_combate.discard(carta_id)

       # Agregar resultado a pendientes
       self.resultados_pendientes.append(resultado)

       # Limpiar resultados si hay demasiados
       if (self.auto_limpiar_resultados and
               len(self.resultados_pendientes) > self.max_resultados_pendientes):
           self.resultados_pendientes = self.resultados_pendientes[-self.max_resultados_pendientes:]

       log_evento(f"🏁 Combate {combate_id} finalizado y removido")
       return resultado

   def _procesar_tick_interno(self, delta_time: float) -> bool:
       """Procesa todos los combates activos"""
       combates_a_remover = []

       for combate_id, combate in self.combates_activos.items():
           # CORRECCIÓN: Asegurar procesamiento real
           combate.procesar_tick(delta_time)

           # Verificar si debe terminar
           if combate._debe_terminar_combate():
               combates_a_remover.append(combate_id)

       # Finalizar combates terminados
       for combate_id in combates_a_remover:
           self.finalizar_combate(combate_id)

       return len(self.combates_activos) > 0 or len(combates_a_remover) > 0

   def _puede_agregar_carta_a_combate(self, carta: CartaBase) -> bool:
       """Verifica si una carta puede ser agregada a un combate"""
       if not carta.esta_viva():
           return False

       if carta.id in self.cartas_en_combate:
           log_evento(f"⚠️ Carta {carta.nombre} ya está en combate")
           return False

       return True

   def _encontrar_combate_de_carta(self, carta_id: int) -> Optional[CombateMultiple]:
       """Encuentra en qué combate está una carta"""
       for combate in self.combates_activos.values():
           if combate.esta_carta_en_combate(carta_id):
               return combate
       return None

   def obtener_combates_terminados(self) -> List[ResultadoCombateMultiple]:
       """Obtiene resultados de combates terminados y los marca como procesados"""
       resultados = self.resultados_pendientes.copy()

       if self.auto_limpiar_resultados:
           self.resultados_pendientes.clear()

       return resultados

   def obtener_estadisticas_globales(self) -> dict:
       """Obtiene estadísticas completas del manager - VERSIÓN CORREGIDA"""
       total_ataques = 0
       combates_details = []

       for combate_id, combate in self.combates_activos.items():
           ataques_combate = sum(estado.ataques_realizados
                                 for estado in combate.cartas_combate.values())
           total_ataques += ataques_combate

           combates_details.append({
               'id_combate': combate_id,
               'cartas_vivas': len([e for e in combate.cartas_combate.values()
                                    if e.carta.esta_viva()]),
               'ataques_ejecutados': ataques_combate,
               'tiempo_activo': time.time() - combate.tiempo_inicio
           })

       return {
           'combates_activos': len(self.combates_activos),
           'combates_finalizados': self.total_combates_finalizados,  # ✅ CORREGIDO
           'cartas_en_combate': sum(len(c.cartas_combate) for c in self.combates_activos.values()),
           'total_ataques_ejecutados': total_ataques,
           'tiempo_activo': time.time() - self.tiempo_inicio_manager,  # ✅ CORREGIDO
           'combates_details': combates_details,
           # ✅ PROPIEDADES AGREGADAS para los tests:
           'combates_creados': self.total_combates_creados,
           'resultados_pendientes': len(self.resultados_pendientes)
       }

   def limpiar_combates_inactivos(self) -> int:
       """Limpia combates que no tienen actividad"""
       combates_limpiados = 0
       combates_a_limpiar = []

       for combate_id, combate in self.combates_activos.items():
           # Si no hay cartas vivas o no hay actividad
           cartas_vivas = len(combate.obtener_cartas_vivas())
           if cartas_vivas == 0:
               combates_a_limpiar.append(combate_id)

       for combate_id in combates_a_limpiar:
           self.finalizar_combate(combate_id)
           combates_limpiados += 1

       if combates_limpiados > 0:
           log_evento(f"🧹 {combates_limpiados} combates inactivos limpiados")

       return combates_limpiados

   def configurar_manager(self, max_combates: int = None, auto_limpiar: bool = None,
                          max_resultados: int = None):
       """Configura parámetros del manager"""
       if max_combates is not None:
           self.max_combates_simultaneos = max_combates
           log_evento(f"🔧 Max combates simultáneos: {max_combates}")

       if auto_limpiar is not None:
           self.auto_limpiar_resultados = auto_limpiar
           log_evento(f"🔧 Auto-limpiar resultados: {auto_limpiar}")

       if max_resultados is not None:
           self.max_resultados_pendientes = max_resultados
           log_evento(f"🔧 Max resultados pendientes: {max_resultados}")

   def obtener_resumen_estado(self) -> str:
       """Obtiene un resumen del estado actual - VERSIÓN CORREGIDA"""
       stats = self.obtener_estadisticas_globales()

       lineas = []
       lineas.append(f"🎮 Manager de Combates")
       lineas.append(f"   Combates activos: {stats['combates_activos']}")
       lineas.append(f"   Cartas en combate: {stats['cartas_en_combate']}")
       lineas.append(f"   Total creados: {stats['combates_creados']}")  # ✅ CORREGIDO
       lineas.append(f"   Total finalizados: {stats['combates_finalizados']}")  # ✅ CORREGIDO
       lineas.append(f"   Resultados pendientes: {stats['resultados_pendientes']}")  # ✅ CORREGIDO

       if stats['combates_details']:
           lineas.append("   Combates activos:")
           for combate_detail in stats['combates_details']:
               lineas.append(f"     - {combate_detail['id_combate']}: "
                             f"{combate_detail['cartas_vivas']} cartas, "
                             f"{combate_detail['ataques_ejecutados']} ataques")

       return "\n".join(lineas)

   def __str__(self):
       return f"ManagerCombates({len(self.combates_activos)} activos, {len(self.cartas_en_combate)} cartas)"