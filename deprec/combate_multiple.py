"""
Sistema de combate múltiple que maneja N vs N
Permite múltiples atacantes contra múltiples objetivos
INTEGRADO con sistema de IA automática
"""

import time
import uuid
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from deprec.componente_base import ComponenteBaseTiempoReal
from deprec.estado_combate_carta import EstadoCombateCarta, RegistroAtaque
from src.game.cartas.carta_base import CartaBase
from src.utils.helpers import log_evento


@dataclass
class ResultadoCombateMultiple:
    """Resultado de un sistema de combate múltiple"""
    cartas_participantes: List[int] = field(default_factory=list)
    cartas_eliminadas: List[int] = field(default_factory=list)
    cartas_supervivientes: List[int] = field(default_factory=list)
    duracion_segundos: float = 0.0
    ataques_totales: int = 0
    dano_total_infligido: int = 0
    tiempo_inicio: float = 0.0
    tiempo_fin: float = 0.0


class CombateMultiple(ComponenteBaseTiempoReal):
    """Sistema unificado de combate múltiple N vs N con IA integrada"""

    def __init__(self, id_combate: str = None):
        if id_combate is None:
            id_combate = f"combate_{uuid.uuid4().hex[:8]}"

        super().__init__(id_combate)

        # Estados de cartas en combate
        self.cartas_combate: Dict[int, EstadoCombateCarta] = {}

        # Cola de ataques programados
        self.ataques_programados: List[RegistroAtaque] = []

        # Control del combate
        self.tiempo_inicio = time.time()
        self.combate_activo = True
        self.max_duracion_segundos = 300  # 5 minutos máximo

        # Estadísticas
        self.total_ataques_ejecutados = 0
        self.total_dano_infligido = 0
        self.cartas_eliminadas: Set[int] = set()

        # NUEVO: Integración con sistema de IA
        self.motor_ia = None  # Se inicializará cuando sea necesario
        self.comportamientos_activos: Dict[int, str] = {}  # {carta_id: tipo_comportamiento}
        self.ultima_evaluacion_ia = 0.0
        self.intervalo_evaluacion_ia = 0.5  # Evaluar IA cada 0.5 segundos

        log_evento(f"🥊 Combate múltiple iniciado: {id_combate}")

    def _inicializar_motor_ia(self):
        """Inicializa el motor de IA cuando es necesario"""
        if self.motor_ia is None:
            try:
                from deprec.ai_combate import AIMotorDecision
                # Crear mapa dummy para el motor IA (requerido por constructor)
                from src.game.combate import MapaGlobal
                mapa_dummy = MapaGlobal(tamaño=3)
                self.motor_ia = AIMotorDecision(mapa_dummy)
                log_evento(f"🤖 Motor IA inicializado para combate {self.id_componente}")
            except Exception as e:
                log_evento(f"⚠️ No se pudo inicializar motor IA: {e}")
                self.motor_ia = False  # Marcar como fallido para no reintentar

    def agregar_carta(self, carta: CartaBase) -> bool:
        """Agrega una carta al sistema de combate"""
        if not carta.esta_viva():
            return False

        if carta.id in self.cartas_combate:
            log_evento(f"⚠️ Carta {carta.nombre} ya está en combate")
            return False

        estado = EstadoCombateCarta(carta)
        self.cartas_combate[carta.id] = estado

        log_evento(f"➕ {carta.nombre} agregada al combate {self.id_componente}")
        return True

    def remover_carta(self, carta_id: int) -> bool:
        """Remueve una carta del sistema de combate"""
        if carta_id not in self.cartas_combate:
            return False

        estado = self.cartas_combate[carta_id]

        # Limpiar referencias a esta carta
        self._limpiar_referencias_carta(carta_id)

        # Limpiar comportamientos IA
        if carta_id in self.comportamientos_activos:
            del self.comportamientos_activos[carta_id]

        # Remover del combate
        del self.cartas_combate[carta_id]

        log_evento(f"➖ {estado.carta.nombre} removida del combate")
        return True

    def ordenar_ataque(self, atacante_id: int, objetivo_id: int) -> bool:
        """Ordena que una carta ataque a otra Y asigna comportamiento automático"""
        if atacante_id not in self.cartas_combate:
            log_evento(f"❌ Atacante {atacante_id} no está en combate")
            return False

        if objetivo_id not in self.cartas_combate:
            log_evento(f"❌ Objetivo {objetivo_id} no está en combate")
            return False

        estado_atacante = self.cartas_combate[atacante_id]
        estado_objetivo = self.cartas_combate[objetivo_id]

        if not estado_atacante.carta.esta_viva():
            return False

        if not estado_objetivo.carta.esta_viva():
            return False

        # 1. Programar el primer ataque inmediato
        tiempo_ejecucion = estado_atacante.programar_ataque(objetivo_id)

        if tiempo_ejecucion > 0:
            # Crear registro de ataque
            registro = RegistroAtaque(
                atacante_id=atacante_id,
                objetivo_id=objetivo_id,
                tiempo_ejecucion=tiempo_ejecucion,
                id_ataque=f"atk_{uuid.uuid4().hex[:6]}"
            )

            # Agregar a cola de ataques
            self.ataques_programados.append(registro)
            self.ataques_programados.sort(key=lambda x: x.tiempo_ejecucion)

            # Actualizar relaciones
            estado_objetivo.agregar_atacante(atacante_id)

            # 2. NUEVO: Asignar comportamiento automático agresivo
            self._asignar_comportamiento_ataque_continuo(atacante_id, objetivo_id)

            log_evento(f"📋 Ataque programado: {estado_atacante.carta.nombre} → {estado_objetivo.carta.nombre}")
            return True

        return False

    def _asignar_comportamiento_ataque_continuo(self, atacante_id: int, objetivo_id: int):
        """Asigna comportamiento automático para continuar atacando"""
        # Marcar como comportamiento activo
        self.comportamientos_activos[atacante_id] = f"agresivo_vs_{objetivo_id}"

        # Inicializar motor IA si es necesario
        self._inicializar_motor_ia()

        if self.motor_ia and self.motor_ia is not False:
            try:
                from deprec.comportamientos import TipoComportamiento

                # Configurar parámetros para comportamiento agresivo específico
                parametros = {
                    'objetivo_especifico': objetivo_id,
                    'rango_busqueda': 10,  # Rango amplio para perseguir
                    'prioridad_alta': True
                }

                # Asignar comportamiento al motor de IA
                exito = self.motor_ia.asignar_comportamiento_carta(
                    atacante_id,
                    TipoComportamiento.AGRESIVO,
                    parametros
                )

                if exito:
                    log_evento(f"🤖 Comportamiento agresivo asignado a carta {atacante_id}")
                    log_evento(f"🤖 IA activada: Carta {atacante_id} atacará continuamente a {objetivo_id}")
                else:
                    log_evento(f"⚠️ No se pudo activar IA para carta {atacante_id}")

            except Exception as e:
                log_evento(f"⚠️ Error asignando comportamiento IA: {e}")
        else:
            # Fallback sin motor IA - solo marcar comportamiento
            log_evento(f"🤖 Comportamiento agresivo asignado a carta {atacante_id}")
            log_evento(f"🤖 IA activada: Carta {atacante_id} atacará continuamente a {objetivo_id}")

    def cancelar_ataques_carta(self, carta_id: int):
        """Cancela todos los ataques programados de una carta"""
        # Remover ataques de la cola
        ataques_originales = len(self.ataques_programados)
        self.ataques_programados = [
            atk for atk in self.ataques_programados
            if atk.atacante_id != carta_id
        ]

        ataques_cancelados = ataques_originales - len(self.ataques_programados)

        # Limpiar comportamiento IA
        if carta_id in self.comportamientos_activos:
            del self.comportamientos_activos[carta_id]

        if ataques_cancelados > 0:
            log_evento(f"🚫 {ataques_cancelados} ataques cancelados para carta {carta_id}")

    def _procesar_tick_interno(self, delta_time: float) -> bool:
        """Procesa un tick del sistema de combate"""
        tiempo_actual = time.time()

        # DEBUG: Log cada 2 segundos para ver qué pasa
        if int(tiempo_actual) % 2 == 0 and int(tiempo_actual) != getattr(self, '_ultimo_debug', 0):
            self._ultimo_debug = int(tiempo_actual)
            log_evento(f"🔍 DEBUG: {self.obtener_estado_debug()}")

        # Verificar duración máxima
        if tiempo_actual - self.tiempo_inicio > self.max_duracion_segundos:
            log_evento(f"⏰ Combate {self.id_componente} terminado por tiempo límite")
            return False

        # Actualizar estados de todas las cartas
        self._actualizar_estados_cartas(tiempo_actual)

        # NUEVO: Procesar IA automática para generar nuevos ataques
        self._procesar_ia_automatica(tiempo_actual)

        # Procesar ataques programados
        self._procesar_ataques_programados(tiempo_actual)

        # Limpiar cartas muertas
        self._limpiar_cartas_muertas()

        # Verificar si el combate debe continuar
        return self._debe_continuar_combate()

    def _actualizar_estados_cartas(self, tiempo_actual: float):
        """Actualiza los estados de todas las cartas"""
        for estado in self.cartas_combate.values():
            estado.actualizar_tiempo(tiempo_actual)

    def _procesar_ia_automatica(self, tiempo_actual: float):
        """Procesa IA automática para generar nuevos ataques"""
        # Solo evaluar cada cierto intervalo
        if tiempo_actual - self.ultima_evaluacion_ia < self.intervalo_evaluacion_ia:
            return

        self.ultima_evaluacion_ia = tiempo_actual

        if not self.comportamientos_activos:
            return  # No hay comportamientos activos

        # CORRECCIÓN: Ser más agresivo generando ataques
        for carta_id, comportamiento in list(self.comportamientos_activos.items()):
            if carta_id not in self.cartas_combate:
                continue

            estado_carta = self.cartas_combate[carta_id]
            if not estado_carta.carta.esta_viva():
                del self.comportamientos_activos[carta_id]
                continue

            # MEJORADO: Verificar con más frecuencia si puede atacar
            if estado_carta.puede_atacar(tiempo_actual):
                if comportamiento.startswith("agresivo_vs_"):
                    objetivo_id = int(comportamiento.split("_")[-1])

                    if (objetivo_id in self.cartas_combate and
                            self.cartas_combate[objetivo_id].carta.esta_viva()):

                        # ASEGURAR que se programa el ataque
                        exito = self._programar_ataque_ia(carta_id, objetivo_id)
                        if exito:
                            # Log más frecuente para debugging
                            if len(self.ataques_programados) % 5 == 1:
                                log_evento(f"🤖 IA programa ataque: {carta_id} → {objetivo_id}")
                    else:
                        # Buscar nuevo objetivo
                        nuevo_objetivo = self._buscar_nuevo_objetivo(carta_id)
                        if nuevo_objetivo:
                            self.comportamientos_activos[carta_id] = f"agresivo_vs_{nuevo_objetivo}"
                            self._programar_ataque_ia(carta_id, nuevo_objetivo)
                        else:
                            del self.comportamientos_activos[carta_id]

    def _buscar_nuevo_objetivo(self, atacante_id: int) -> Optional[int]:
        """Busca un nuevo objetivo para una carta con comportamiento agresivo"""
        if atacante_id not in self.cartas_combate:
            return None

        # Buscar cualquier carta viva que no sea el atacante
        for carta_id, estado in self.cartas_combate.items():
            if carta_id != atacante_id and estado.carta.esta_viva():
                return carta_id

        return None

    def _programar_ataque_ia(self, atacante_id: int, objetivo_id: int):
        """Programa un ataque generado por IA (sin logs excesivos)"""
        if atacante_id not in self.cartas_combate or objetivo_id not in self.cartas_combate:
            return False

        estado_atacante = self.cartas_combate[atacante_id]

        # Programar el ataque
        tiempo_ejecucion = estado_atacante.programar_ataque(objetivo_id)

        if tiempo_ejecucion > 0:
            # Crear registro de ataque
            registro = RegistroAtaque(
                atacante_id=atacante_id,
                objetivo_id=objetivo_id,
                tiempo_ejecucion=tiempo_ejecucion,
                id_ataque=f"ia_{uuid.uuid4().hex[:6]}"
            )

            # Agregar a cola de ataques
            self.ataques_programados.append(registro)
            self.ataques_programados.sort(key=lambda x: x.tiempo_ejecucion)

            # Actualizar relaciones
            self.cartas_combate[objetivo_id].agregar_atacante(atacante_id)

            # Solo log ocasional para no spam
            if len(self.ataques_programados) % 10 == 1:  # Log cada 10 ataques
                log_evento(f"🤖 IA programa ataque: {atacante_id} → {objetivo_id}")

            return True

        return False

    def _procesar_ataques_programados(self, tiempo_actual: float):
        """Procesa ataques que deben ejecutarse"""
        ataques_a_ejecutar = []
        ataques_restantes = []

        # Separar ataques listos de los pendientes
        for ataque in self.ataques_programados:
            if tiempo_actual >= ataque.tiempo_ejecucion:
                ataques_a_ejecutar.append(ataque)
            else:
                ataques_restantes.append(ataque)

        # Actualizar cola
        self.ataques_programados = ataques_restantes

        # Ejecutar ataques
        for ataque in ataques_a_ejecutar:
            self._ejecutar_ataque(ataque, tiempo_actual)

    def _ejecutar_ataque(self, registro: RegistroAtaque, tiempo_actual: float):
        """Ejecuta un ataque específico - VERSIÓN CORREGIDA"""
        try:
            # Verificar que ambas cartas siguen en combate
            if (registro.atacante_id not in self.cartas_combate or
                    registro.objetivo_id not in self.cartas_combate):
                return

            estado_atacante = self.cartas_combate[registro.atacante_id]
            estado_objetivo = self.cartas_combate[registro.objetivo_id]

            # Verificar que ambas siguen vivas
            if not estado_atacante.carta.esta_viva() or not estado_objetivo.carta.esta_viva():
                return

            # CORRECCIÓN: Usar calculadora de daño real
            from src.game.combate import CalculadoraDano
            calculadora = CalculadoraDano()

            resultado = calculadora.calcular_dano(
                estado_atacante.carta,
                estado_objetivo.carta,
                "fisico"
            )

            # Registrar estadísticas en estados
            estado_atacante.ataques_realizados += 1
            estado_objetivo.ataques_recibidos += 1

            # Registrar estadísticas globales del combate
            self.total_ataques_ejecutados += 1
            self.total_dano_infligido += resultado['dano_aplicado']

            log_evento(f"⚔️ {estado_atacante.carta.nombre} → {estado_objetivo.carta.nombre}: "
                       f"{resultado['dano_aplicado']} daño {resultado['tipo_ataque']}")

            # IMPORTANTE: Verificar si el objetivo murió
            if not estado_objetivo.carta.esta_viva():
                log_evento(f"💀 {estado_objetivo.carta.nombre} ha sido eliminada")
                self.cartas_eliminadas.add(registro.objetivo_id)
                self._remover_carta_muerta(registro.objetivo_id)

        except Exception as e:
            log_evento(f"❌ Error ejecutando ataque: {e}")

    def _limpiar_cartas_muertas(self):
        """Remueve cartas muertas del combate"""
        cartas_a_remover = []

        for carta_id, estado in self.cartas_combate.items():
            if not estado.carta.esta_viva():
                cartas_a_remover.append(carta_id)

        for carta_id in cartas_a_remover:
            if carta_id not in self.cartas_eliminadas:  # Evitar doble procesamiento
                self._remover_carta_muerta(carta_id)

    def _remover_carta_muerta(self, carta_id: int):
        """Remueve una carta muerta del combate"""
        if carta_id in self.cartas_combate:
            carta_nombre = self.cartas_combate[carta_id].carta.nombre

            # Marcar como eliminada
            self.cartas_eliminadas.add(carta_id)

            # Limpiar referencias
            self._limpiar_referencias_carta(carta_id)

            # Limpiar comportamientos IA
            if carta_id in self.comportamientos_activos:
                del self.comportamientos_activos[carta_id]

            # Remover del combate
            del self.cartas_combate[carta_id]

            log_evento(f"💀 {carta_nombre} eliminada")
            log_evento(f"➖ {carta_nombre} removida del combate")

    def _limpiar_referencias_carta(self, carta_id: int):
        """Limpia todas las referencias a una carta"""
        # Cancelar ataques de/hacia esta carta
        self.ataques_programados = [
            atk for atk in self.ataques_programados
            if atk.atacante_id != carta_id and atk.objetivo_id != carta_id
        ]

        # Limpiar referencias en otros estados
        for estado in self.cartas_combate.values():
            estado.remover_atacante(carta_id)

    def _debe_continuar_combate(self) -> bool:
        """Verifica si el combate debe continuar"""
        if not self.combate_activo:
            return False

        cartas_vivas = [
            estado for estado in self.cartas_combate.values()
            if estado.carta.esta_viva()
        ]

        # Si hay menos de 2 cartas vivas, terminar combate
        if len(cartas_vivas) < 2:
            log_evento(f"🏁 Combate {self.id_componente} terminado - menos de 2 cartas vivas")
            return False

        # MEJORADO: Verificar actividad real del combate
        hay_ataques_programados = len(self.ataques_programados) > 0
        hay_cartas_en_combate = any(estado.esta_en_combate() for estado in cartas_vivas)
        hay_comportamientos_activos = len(self.comportamientos_activos) > 0

        # Si hay cualquier tipo de actividad, continuar
        if hay_ataques_programados or hay_cartas_en_combate or hay_comportamientos_activos:
            return True

        # CORRECCIÓN: Dar más tiempo antes de auto-terminar
        tiempo_vida = time.time() - self.tiempo_inicio

        if tiempo_vida < 5.0:  # Dar al menos 5 segundos de vida mínima
            return True

        # Solo terminar después de tiempo sin actividad
        log_evento(f"💤 Combate {self.id_componente} terminado - sin actividad por {tiempo_vida:.1f}s")
        return False

    def _debe_terminar_combate(self) -> bool:
        """Verifica si el combate debe terminar (método público para manager)"""
        cartas_vivas = sum(1 for estado in self.cartas_combate.values()
                           if estado.carta.esta_viva())
        if cartas_vivas < 2:
            return True
        return not self._debe_continuar_combate()

    def obtener_cartas_vivas(self) -> List[EstadoCombateCarta]:
        """Obtiene lista de cartas vivas en combate"""
        return [
            estado for estado in self.cartas_combate.values()
            if estado.carta.esta_viva()
        ]

    def obtener_cartas_atacando(self, objetivo_id: int) -> List[EstadoCombateCarta]:
        """Obtiene cartas que están atacando a un objetivo específico"""
        atacantes = []
        for estado in self.cartas_combate.values():
            if objetivo_id in estado.atacando_a and estado.carta.esta_viva():
                atacantes.append(estado)
        return atacantes

    def esta_carta_en_combate(self, carta_id: int) -> bool:
        """Verifica si una carta está en este combate"""
        return carta_id in self.cartas_combate

    def obtener_estadisticas_combate(self) -> Dict:
        """Obtiene estadísticas del combate"""
        tiempo_actual = time.time()
        duracion = tiempo_actual - self.tiempo_inicio

        cartas_vivas = len(self.obtener_cartas_vivas())
        cartas_total = len(self.cartas_combate)

        return {
            "id_combate": self.id_componente,
            "duracion_segundos": duracion,
            "cartas_totales": cartas_total,
            "cartas_vivas": cartas_vivas,
            "cartas_eliminadas": len(self.cartas_eliminadas),
            "ataques_ejecutados": self.total_ataques_ejecutados,
            "ataques_programados": len(self.ataques_programados),
            "dano_total": self.total_dano_infligido,
            "combate_activo": self.combate_activo,
            "comportamientos_ia_activos": len(self.comportamientos_activos)
        }

    def finalizar_combate(self) -> ResultadoCombateMultiple:
        """Finaliza el combate y retorna resultado"""
        tiempo_actual = time.time()

        resultado = ResultadoCombateMultiple(
            cartas_participantes=list(self.cartas_combate.keys()),
            cartas_eliminadas=list(self.cartas_eliminadas),
            cartas_supervivientes=[
                carta_id for carta_id, estado in self.cartas_combate.items()
                if estado.carta.esta_viva()
            ],
            duracion_segundos=tiempo_actual - self.tiempo_inicio,
            ataques_totales=self.total_ataques_ejecutados,
            dano_total_infligido=self.total_dano_infligido,
            tiempo_inicio=self.tiempo_inicio,
            tiempo_fin=tiempo_actual
        )

        self.combate_activo = False

        log_evento(f"🏁 Combate {self.id_componente} finalizado:")
        log_evento(f"   Duración: {resultado.duracion_segundos:.1f}s")
        log_evento(f"   Ataques: {resultado.ataques_totales}")
        log_evento(f"   Supervivientes: {len(resultado.cartas_supervivientes)}")

        return resultado

    def obtener_estado_debug(self) -> str:
        """Obtiene estado detallado para debugging"""
        cartas_vivas = len([e for e in self.cartas_combate.values() if e.carta.esta_viva()])
        ataques_prog = len(self.ataques_programados)
        cartas_combate_activo = len([e for e in self.cartas_combate.values() if e.esta_en_combate()])
        comportamientos = len(self.comportamientos_activos)
        tiempo_vida = time.time() - self.tiempo_inicio

        return (f"Combate {self.id_componente}: "
                f"vivas={cartas_vivas}, ataques={ataques_prog}, "
                f"en_combate={cartas_combate_activo}, ia_activa={comportamientos}, "
                f"vida={tiempo_vida:.1f}s, activo={self.combate_activo}")

    def __str__(self):
        return f"CombateMultiple({self.id_componente}, {len(self.cartas_combate)} cartas, {len(self.comportamientos_activos)} IA activa)"