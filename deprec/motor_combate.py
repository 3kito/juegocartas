# src/game/combate/motor_combate.py
"""
Motor principal del sistema de combate automático
"""

import random
from typing import List, Tuple, Dict, Optional
from src.core.jugador import Jugador
from src.game.cartas.carta_base import CartaBase
from src.game.combate.calculadora_dano import CalculadoraDano
from src.game.tablero.tablero_hexagonal import Coordenada
from src.utils.helpers import log_evento


class ResultadoCombate:
    """Resultado de un combate entre dos jugadores"""

    def __init__(self, jugador1: Jugador, jugador2: Jugador):
        self.jugador1 = jugador1
        self.jugador2 = jugador2
        self.ganador: Optional[Jugador] = None
        self.perdedor: Optional[Jugador] = None
        self.dano_infligido = 0
        self.turnos_totales = 0
        self.cartas_eliminadas = []
        self.tiempo_combate = 0

    def determinar_ganador(self):
        """Determina el ganador basado en cartas supervivientes"""
        cartas_vivas_j1 = sum(1 for _, carta in self.jugador1.obtener_cartas_tablero()
                              if carta.esta_viva())
        cartas_vivas_j2 = sum(1 for _, carta in self.jugador2.obtener_cartas_tablero()
                              if carta.esta_viva())

        if cartas_vivas_j1 > cartas_vivas_j2:
            self.ganador = self.jugador1
            self.perdedor = self.jugador2
        elif cartas_vivas_j2 > cartas_vivas_j1:
            self.ganador = self.jugador2
            self.perdedor = self.jugador1
        else:
            # Empate - determinar por vida total restante
            vida_j1 = sum(carta.vida_actual for _, carta in self.jugador1.obtener_cartas_tablero())
            vida_j2 = sum(carta.vida_actual for _, carta in self.jugador2.obtener_cartas_tablero())

            if vida_j1 > vida_j2:
                self.ganador = self.jugador1
                self.perdedor = self.jugador2
            else:
                self.ganador = self.jugador2
                self.perdedor = self.jugador1


class MotorCombate:
    """Motor principal para simular combates automáticos"""

    def __init__(self):
        self.calculadora = CalculadoraDano()
        self.MAX_TURNOS = 50  # Límite de seguridad
        self.turno_actual = 0

    def simular_combate(self, jugador1: Jugador, jugador2: Jugador) -> ResultadoCombate:
        """
        Simula un combate completo entre dos jugadores

        Returns:
            ResultadoCombate con toda la información del enfrentamiento
        """
        log_evento(f"🥊 INICIANDO COMBATE: {jugador1.nombre} vs {jugador2.nombre}")

        resultado = ResultadoCombate(jugador1, jugador2)
        self.turno_actual = 0

        # Preparar cartas para combate
        self._preparar_cartas_para_combate(jugador1)
        self._preparar_cartas_para_combate(jugador2)

        # Loop principal de combate
        while (self._hay_cartas_vivas(jugador1) and
               self._hay_cartas_vivas(jugador2) and
               self.turno_actual < self.MAX_TURNOS):
            self.turno_actual += 1
            log_evento(f"--- Turno {self.turno_actual} ---")

            # Ejecutar turno para ambos jugadores
            self._ejecutar_turno_jugador(jugador1, jugador2)
            self._ejecutar_turno_jugador(jugador2, jugador1)

            # Limpiar cartas muertas
            self._limpiar_cartas_muertas(jugador1)
            self._limpiar_cartas_muertas(jugador2)

        # Finalizar combate
        resultado.turnos_totales = self.turno_actual
        resultado.determinar_ganador()

        self._finalizar_combate(resultado)
        return resultado

    def _preparar_cartas_para_combate(self, jugador: Jugador):
        """Prepara las cartas del jugador para el combate"""
        for coord, carta in jugador.obtener_cartas_tablero():
            if isinstance(carta, CartaBase):
                carta.iniciar_turno()
                carta.coordenada = coord  # Asignar coordenada actual

    def _hay_cartas_vivas(self, jugador: Jugador) -> bool:
        """Verifica si el jugador tiene cartas vivas"""
        for _, carta in jugador.obtener_cartas_tablero():
            if isinstance(carta, CartaBase) and carta.esta_viva():
                return True
        return False

    def _ejecutar_turno_jugador(self, jugador: Jugador, enemigo: Jugador):
        """Ejecuta el turno de todas las cartas de un jugador"""
        cartas_propias = [(coord, carta) for coord, carta in jugador.obtener_cartas_tablero()
                          if isinstance(carta, CartaBase) and carta.esta_viva()]

        # Ordenar por iniciativa (velocidad/daño total)
        cartas_propias.sort(key=lambda x: x[1].obtener_dano_total(), reverse=True)

        for coord, carta in cartas_propias:
            if carta.esta_viva() and carta.puede_actuar:
                self._ejecutar_turno_carta(carta, jugador, enemigo)
                carta.finalizar_turno()

    def _ejecutar_turno_carta(self, carta: CartaBase, jugador_propio: Jugador, jugador_enemigo: Jugador):
        """Ejecuta el turno de una carta específica"""
        # IA muy básica: atacar al enemigo más cercano
        objetivo = self._encontrar_objetivo_mas_cercano(carta, jugador_enemigo)

        if objetivo:
            coord_objetivo, carta_objetivo = objetivo
            distancia = carta.coordenada.distancia_a(coord_objetivo)

            # Verificar si puede atacar
            if self.calculadora.puede_atacar(carta, carta_objetivo, distancia):
                self._ejecutar_ataque(carta, carta_objetivo)
            else:
                log_evento(
                    f"  {carta.nombre} no puede atacar (distancia: {distancia}, rango: {carta.rango_ataque_actual})")
        else:
            log_evento(f"  {carta.nombre} no encuentra objetivos")

    def _encontrar_objetivo_mas_cercano(self, carta: CartaBase, jugador_enemigo: Jugador) -> Optional[
        Tuple[Coordenada, CartaBase]]:
        """Encuentra el enemigo más cercano a la carta"""
        objetivos_validos = []

        for coord, carta_enemiga in jugador_enemigo.obtener_cartas_tablero():
            if isinstance(carta_enemiga, CartaBase) and carta_enemiga.esta_viva():
                distancia = carta.coordenada.distancia_a(coord)
                objetivos_validos.append((distancia, coord, carta_enemiga))

        if not objetivos_validos:
            return None

        # Ordenar por distancia (más cercano primero)
        objetivos_validos.sort(key=lambda x: x[0])
        _, coord, carta_objetivo = objetivos_validos[0]

        return (coord, carta_objetivo)

    def _ejecutar_ataque(self, atacante: CartaBase, defensor: CartaBase):
        """Ejecuta un ataque entre dos cartas"""
        # Determinar tipo de ataque (físico vs mágico)
        tipo_ataque = "magico" if atacante.dano_magico_actual > atacante.dano_fisico_actual else "fisico"

        # Calcular daño
        resultado = self.calculadora.calcular_dano(atacante, defensor, tipo_ataque)

        # Log del ataque
        critico_texto = " (CRÍTICO)" if resultado['es_critico'] else ""
        log_evento(f"  ⚔️ {atacante.nombre} ataca a {defensor.nombre}: "
                   f"{resultado['dano_aplicado']} daño {tipo_ataque}{critico_texto}")

        if resultado['objetivo_eliminado']:
            log_evento(f"    💀 {defensor.nombre} eliminada")

    def _limpiar_cartas_muertas(self, jugador: Jugador):
        """Remueve cartas muertas del tablero"""
        coords_a_limpiar = []

        for coord, carta in jugador.obtener_cartas_tablero():
            if isinstance(carta, CartaBase) and not carta.esta_viva():
                coords_a_limpiar.append(coord)

        for coord in coords_a_limpiar:
            carta_muerta = jugador.quitar_carta_del_tablero(coord)
            if carta_muerta:
                log_evento(f"  🗑️ {carta_muerta.nombre} removida del tablero")

    def _finalizar_combate(self, resultado: ResultadoCombate):
        """Finaliza el combate y muestra resultados"""
        if resultado.ganador:
            log_evento(f"🏆 GANADOR: {resultado.ganador.nombre}")
            log_evento(f"   Turnos: {resultado.turnos_totales}")

            # Calcular daño al perdedor
            cartas_ganadoras = sum(1 for _, carta in resultado.ganador.obtener_cartas_tablero()
                                   if isinstance(carta, CartaBase) and carta.esta_viva())

            dano_base = random.randint(10, 20)
            dano_bonus = cartas_ganadoras * 2
            dano_total = dano_base + dano_bonus

            resultado.perdedor.recibir_dano(dano_total)
            resultado.dano_infligido = dano_total

            log_evento(f"   {resultado.perdedor.nombre} recibe {dano_total} daño "
                       f"({dano_base} base + {dano_bonus} por {cartas_ganadoras} cartas)")
        else:
            log_evento("🤝 Combate terminó en empate")