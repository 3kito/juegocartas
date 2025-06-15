"""
Estado de combate individual para cada carta
Maneja atacantes múltiples y objetivos múltiples
"""

import time
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from enum import Enum
from src.game.cartas.carta_base import CartaBase
from src.utils.helpers import log_evento


class EstadoAtaque(Enum):
    """Estados de ataque de una carta"""
    DISPONIBLE = "disponible"
    EN_COOLDOWN = "en_cooldown"
    ATACANDO = "atacando"
    INTERRUMPIDO = "interrumpido"


@dataclass
class RegistroAtaque:
    """Registro de un ataque programado"""
    atacante_id: int
    objetivo_id: int
    tiempo_ejecucion: float
    tipo_ataque: str = "fisico"
    fuerza_ataque: float = 1.0
    id_ataque: str = ""


class EstadoCombateCarta:
    """Estado de combate para una carta individual"""

    def __init__(self, carta: CartaBase):
        self.carta = carta
        self.carta_id = carta.id

        # Estado de ataque
        self.estado_ataque = EstadoAtaque.DISPONIBLE
        self.ultimo_ataque = 0.0
        self.proximo_ataque_disponible = 0.0
        self.velocidad_ataque = self.calcular_velocidad_ataque()

        # Relaciones de combate
        self.atacando_a: Set[int] = set()  # IDs de cartas que estoy atacando
        self.siendo_atacada_por: Set[int] = set()  # IDs de cartas que me atacan

        # Estadísticas de combate
        self.ataques_realizados = 0
        self.ataques_recibidos = 0
        self.dano_total_infligido = 0
        self.dano_total_recibido = 0
        self.tiempo_en_combate = 0.0

        # Control de tiempo
        self.tiempo_inicio_combate = time.time()
        self.tiempo_ultimo_update = time.time()

    def calcular_velocidad_ataque(self) -> float:
        """Calcula velocidad de ataque basada en stats de la carta - VERSIÓN CORREGIDA"""
        # CORRECCIÓN: Fórmula que realmente diferencia velocidades
        dano_total = (self.carta.dano_fisico_actual + self.carta.dano_magico_actual)

        # NUEVA FÓRMULA: Menos daño = más velocidad, más daño = menos velocidad
        if dano_total <= 15:
            # Cartas de poco daño: velocidad alta (0.8-1.0 ataques/segundo)
            self.velocidad_ataque = 0.8 + (15 - dano_total) / 15 * 0.2
        elif dano_total <= 30:
            # Cartas de daño medio: velocidad media (0.4-0.8 ataques/segundo)
            self.velocidad_ataque = 0.4 + (30 - dano_total) / 15 * 0.4
        else:
            # Cartas de mucho daño: velocidad baja (0.2-0.4 ataques/segundo)
            self.velocidad_ataque = 0.2 + max(0, (50 - dano_total)) / 20 * 0.2

        # Asegurar que esté en rango válido
        self.velocidad_ataque = max(0.2, min(1.0, self.velocidad_ataque))

        return self.velocidad_ataque

    def puede_atacar(self, tiempo_actual: float = None) -> bool:
        """Verifica si la carta puede realizar un ataque"""
        if tiempo_actual is None:
            tiempo_actual = time.time()

        if not self.carta.esta_viva():
            return False

        if not self.carta.puede_actuar:
            return False

        if self.estado_ataque != EstadoAtaque.DISPONIBLE:
            return False

        if tiempo_actual < self.proximo_ataque_disponible:
            return False

        return True

    def programar_ataque(self, objetivo_id: int, tiempo_actual: float = None) -> float:
        """Programa un ataque contra un objetivo"""
        if tiempo_actual is None:
            tiempo_actual = time.time()

        if not self.puede_atacar(tiempo_actual):
            return -1  # No puede atacar

        # CORREGIDO: Calcular tiempo de ejecución correctamente
        intervalo_ataque = 1.0 / self.velocidad_ataque
        tiempo_ejecucion = tiempo_actual + 0.1  # Pequeño delay inicial

        # Marcar como atacando
        self.estado_ataque = EstadoAtaque.ATACANDO
        self.atacando_a.add(objetivo_id)

        # Programar próximo ataque disponible
        self.proximo_ataque_disponible = tiempo_ejecucion + intervalo_ataque

        log_evento(f"🎯 {self.carta.nombre} programa ataque a {objetivo_id} para +{0.1:.1f}s")

        return tiempo_ejecucion

    def ejecutar_ataque(self, objetivo: 'EstadoCombateCarta', tiempo_actual: float = None) -> Dict:
        """Ejecuta un ataque contra el objetivo"""
        if tiempo_actual is None:
            tiempo_actual = time.time()

        if not objetivo.carta.esta_viva():
            return {"exito": False, "razon": "objetivo_muerto"}

        # Calcular daño
        from src.game.combate import CalculadoraDano
        calculadora = CalculadoraDano()

        # Determinar tipo de ataque
        tipo_ataque = "magico" if self.carta.dano_magico_actual > self.carta.dano_fisico_actual else "fisico"

        # Ejecutar ataque
        resultado_dano = calculadora.calcular_dano(self.carta, objetivo.carta, tipo_ataque)

        # Actualizar estadísticas
        self.ataques_realizados += 1
        self.dano_total_infligido += resultado_dano['dano_aplicado']

        objetivo.ataques_recibidos += 1
        objetivo.dano_total_recibido += resultado_dano['dano_aplicado']

        # Actualizar estado
        self.estado_ataque = EstadoAtaque.EN_COOLDOWN
        self.ultimo_ataque = tiempo_actual

        resultado = {
            "exito": True,
            "atacante": self.carta.nombre,
            "objetivo": objetivo.carta.nombre,
            "dano_aplicado": resultado_dano['dano_aplicado'],
            "tipo_ataque": tipo_ataque,
            "critico": resultado_dano['es_critico'],
            "objetivo_eliminado": not objetivo.carta.esta_viva()
        }

        log_evento(
            f"⚔️ {self.carta.nombre} → {objetivo.carta.nombre}: {resultado_dano['dano_aplicado']} daño {tipo_ataque}")

        if not objetivo.carta.esta_viva():
            log_evento(f"💀 {objetivo.carta.nombre} eliminada")
            self._limpiar_objetivo_muerto(objetivo.carta_id)

        return resultado

    def agregar_atacante(self, atacante_id: int):
        """Registra que una carta nos está atacando"""
        self.siendo_atacada_por.add(atacante_id)
        log_evento(f"🛡️ {self.carta.nombre} siendo atacada por {atacante_id}")

    def remover_atacante(self, atacante_id: int):
        """Remueve un atacante de la lista"""
        self.siendo_atacada_por.discard(atacante_id)
        if atacante_id in self.atacando_a:
            self.atacando_a.discard(atacante_id)

    def cambiar_objetivo(self, objetivo_anterior: int, objetivo_nuevo: int):
        """Cambia el objetivo de ataque"""
        self.atacando_a.discard(objetivo_anterior)
        self.atacando_a.add(objetivo_nuevo)
        log_evento(f"🔄 {self.carta.nombre} cambia objetivo: {objetivo_anterior} → {objetivo_nuevo}")

    def _limpiar_objetivo_muerto(self, objetivo_id: int):
        """Limpia referencias a un objetivo que murió"""
        self.atacando_a.discard(objetivo_id)

    def actualizar_tiempo(self, tiempo_actual: float = None):
        """Actualiza el tiempo y estado de la carta"""
        if tiempo_actual is None:
            tiempo_actual = time.time()

        # Actualizar tiempo en combate
        delta_time = tiempo_actual - self.tiempo_ultimo_update
        self.tiempo_en_combate += delta_time
        self.tiempo_ultimo_update = tiempo_actual

        # Actualizar estado de ataque
        if self.estado_ataque == EstadoAtaque.EN_COOLDOWN:
            if tiempo_actual >= self.proximo_ataque_disponible:
                self.estado_ataque = EstadoAtaque.DISPONIBLE
        elif self.estado_ataque == EstadoAtaque.ATACANDO:
            # Si está atacando pero no hay objetivos, volver a disponible
            if not self.atacando_a or not any(obj for obj in self.atacando_a):
                self.estado_ataque = EstadoAtaque.DISPONIBLE

    def esta_en_combate(self) -> bool:
        """Verifica si la carta está activamente en combate"""
        # CORREGIDO: Considerar también si tiene ataques programados
        tiene_objetivos = len(self.atacando_a) > 0
        tiene_atacantes = len(self.siendo_atacada_por) > 0
        esta_atacando = self.estado_ataque == EstadoAtaque.ATACANDO

        return tiene_objetivos or tiene_atacantes or esta_atacando

    def obtener_tiempo_hasta_proximo_ataque(self, tiempo_actual: float = None) -> float:
        """Obtiene el tiempo hasta que pueda atacar de nuevo"""
        if tiempo_actual is None:
            tiempo_actual = time.time()

        return max(0, self.proximo_ataque_disponible - tiempo_actual)

    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas del estado de combate"""
        return {
            "carta_id": self.carta_id,
            "carta_nombre": self.carta.nombre,
            "estado_ataque": self.estado_ataque.value,
            "velocidad_ataque": self.velocidad_ataque,
            "atacando_a": list(self.atacando_a),
            "siendo_atacada_por": list(self.siendo_atacada_por),
            "ataques_realizados": self.ataques_realizados,
            "ataques_recibidos": self.ataques_recibidos,
            "dano_infligido": self.dano_total_infligido,
            "dano_recibido": self.dano_total_recibido,
            "tiempo_en_combate": self.tiempo_en_combate,
            "tiempo_hasta_ataque": self.obtener_tiempo_hasta_proximo_ataque(),
            "en_combate": self.esta_en_combate()
        }

    def limpiar_estado(self):
        """Limpia el estado de combate (al salir de combate)"""
        self.atacando_a.clear()
        self.siendo_atacada_por.clear()
        self.estado_ataque = EstadoAtaque.DISPONIBLE
        log_evento(f"🧹 Estado de combate limpiado para {self.carta.nombre}")

    def __str__(self):
        return f"EstadoCombate({self.carta.nombre}, {self.estado_ataque.value}, atacando={len(self.atacando_a)})"

    def __repr__(self):
        return f"EstadoCombateCarta(id={self.carta_id}, estado={self.estado_ataque.value})"