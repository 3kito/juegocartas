"""
IA de combate integrada que combina órdenes y comportamientos
Toma decisiones inteligentes para cartas en modo automático
"""

from typing import Dict, List, Optional
from enum import Enum
import random
from src.game.cartas.carta_base import CartaBase
from deprec.comportamientos import GestorComportamientos, AccionIA, TipoComportamiento
from src.game.combate.mapa_global import MapaGlobal
from src.game.tablero.tablero_hexagonal import Coordenada
from src.utils.helpers import log_evento


class ModoIA(Enum):
    """Modos de operación de la IA"""
    PASIVO = "pasivo"  # Solo comportamientos automáticos
    ASISTIDO = "asistido"  # Combina órdenes + comportamientos
    AGRESIVO = "agresivo"  # Prioriza combate y ataques
    DEFENSIVO = "defensivo"  # Prioriza supervivencia
    EXPLORADOR = "explorador"  # Prioriza movimiento y exploración


class EstadoDecision:
    """Estado de una decisión de IA"""

    def __init__(self, carta: CartaBase, accion: AccionIA, confianza: float):
        self.carta = carta
        self.accion = accion
        self.confianza = confianza  # 0.0 - 1.0
        self.razonamiento = []
        self.alternativas = []

    def agregar_razon(self, razon: str):
        """Agrega una razón al proceso de decisión"""
        self.razonamiento.append(razon)

    def __str__(self):
        return f"Decision({self.carta.nombre}: {self.accion.tipo}, confianza={self.confianza:.2f})"


class EvaluadorSituacion:
    """Evalúa la situación táctica del combate"""

    def __init__(self):
        self.umbrales = {
            'vida_critica': 0.25,
            'vida_baja': 0.5,
            'superioridad_numerica': 1.5,
            'distancia_segura': 3
        }

    def evaluar_situacion_carta(self, carta: CartaBase, aliados: List[CartaBase],
                                enemigos: List[CartaBase], mapa: MapaGlobal) -> Dict[str, any]:
        """Evalúa la situación específica de una carta"""
        situacion = {
            'vida_porcentaje': carta.vida_actual / carta.vida_maxima,
            'enemigos_cercanos': 0,
            'aliados_cercanos': 0,
            'posicion_segura': True,
            'puede_atacar': False,
            'debe_huir': False,
            'prioridad_curacion': False
        }

        if not carta.coordenada:
            return situacion

        # Contar aliados y enemigos cercanos
        for aliado in aliados:
            if aliado != carta and aliado.esta_viva() and aliado.coordenada:
                if carta.coordenada.distancia_a(aliado.coordenada) <= 2:
                    situacion['aliados_cercanos'] += 1

        enemigos_en_rango_ataque = []
        for enemigo in enemigos:
            if enemigo.esta_viva() and enemigo.coordenada:
                distancia = carta.coordenada.distancia_a(enemigo.coordenada)
                if distancia <= 2:
                    situacion['enemigos_cercanos'] += 1
                if distancia <= carta.rango_ataque_actual:
                    enemigos_en_rango_ataque.append(enemigo)
                    situacion['puede_atacar'] = True

        # Evaluar si la posición es segura
        if situacion['enemigos_cercanos'] > situacion['aliados_cercanos']:
            situacion['posicion_segura'] = False

        # Evaluar si debe huir
        if (situacion['vida_porcentaje'] <= self.umbrales['vida_critica'] and
                situacion['enemigos_cercanos'] > 0):
            situacion['debe_huir'] = True

        # Evaluar prioridad de curación
        if situacion['vida_porcentaje'] <= self.umbrales['vida_baja']:
            situacion['prioridad_curacion'] = True

        situacion['enemigos_atacables'] = len(enemigos_en_rango_ataque)

        return situacion

    def evaluar_situacion_global(self, cartas_propias: List[CartaBase],
                                 cartas_enemigas: List[CartaBase]) -> Dict[str, any]:
        """Evalúa la situación global del combate"""
        cartas_vivas_propias = [c for c in cartas_propias if c.esta_viva()]
        cartas_vivas_enemigas = [c for c in cartas_enemigas if c.esta_viva()]

        vida_total_propia = sum(c.vida_actual for c in cartas_vivas_propias)
        vida_total_enemiga = sum(c.vida_actual for c in cartas_vivas_enemigas)

        situacion_global = {
            'cartas_propias': len(cartas_vivas_propias),
            'cartas_enemigas': len(cartas_vivas_enemigas),
            'vida_total_propia': vida_total_propia,
            'vida_total_enemiga': vida_total_enemiga,
            'superioridad_numerica': len(cartas_vivas_propias) / max(1, len(cartas_vivas_enemigas)),
            'superioridad_vida': vida_total_propia / max(1, vida_total_enemiga),
            'situacion': 'equilibrada'
        }

        # Determinar situación general
        if situacion_global['superioridad_numerica'] >= self.umbrales['superioridad_numerica']:
            situacion_global['situacion'] = 'ventajosa'
        elif situacion_global['superioridad_numerica'] <= 1 / self.umbrales['superioridad_numerica']:
            situacion_global['situacion'] = 'desventajosa'

        return situacion_global


class AIMotorDecision:
    """Motor principal de decisiones de IA"""

    def __init__(self, mapa_global: MapaGlobal):
        self.mapa = mapa_global
        self.gestor_comportamientos = GestorComportamientos()
        self.evaluador = EvaluadorSituacion()
        self.modo_default = ModoIA.PASIVO

        # Configuración de IA
        self.factor_agresividad = 0.7
        self.factor_conservacion = 0.8
        self.usar_habilidades = True

        # Modos por jugador
        self.modos_jugadores: Dict[int, ModoIA] = {}

    def configurar_modo_jugador(self, jugador_id: int, modo: ModoIA):
        """Configura el modo de IA para un jugador específico"""
        self.modos_jugadores[jugador_id] = modo
        log_evento(f"🤖 Jugador {jugador_id} configurado en modo {modo.value}")

    def asignar_comportamiento_carta(self, carta_id: int, tipo: TipoComportamiento,
                                     parametros: Dict = None) -> bool:
        """Asigna un comportamiento específico a una carta"""
        return self.gestor_comportamientos.asignar_comportamiento(carta_id, tipo, parametros)

    def decidir_acciones_jugador(self, jugador_id: int, cartas_jugador: List[CartaBase],
                                 cartas_aliadas: List[CartaBase], cartas_enemigas: List[CartaBase]) -> List[
        EstadoDecision]:
        """Decide las acciones para todas las cartas de un jugador"""

        decisiones = []

        # Evaluar situación global
        situacion_global = self.evaluador.evaluar_situacion_global(cartas_jugador, cartas_enemigas)

        # Obtener modo del jugador
        modo_jugador = self.modos_jugadores.get(jugador_id, self.modo_default)

        for carta in cartas_jugador:
            if not carta.esta_viva():
                continue

            # Evaluar situación específica de la carta
            situacion_carta = self.evaluador.evaluar_situacion_carta(
                carta, cartas_aliadas, cartas_enemigas, self.mapa
            )

            # Decidir acción basada en situación y modo
            decision = self._decidir_accion_carta(
                carta, situacion_carta, situacion_global, modo_jugador,
                cartas_aliadas, cartas_enemigas
            )

            if decision:
                decisiones.append(decision)

        return decisiones

    def _decidir_accion_carta(self, carta: CartaBase, situacion: Dict, situacion_global: Dict,
                              modo: ModoIA, aliados: List[CartaBase], enemigos: List[CartaBase]) -> Optional[
        EstadoDecision]:
        """Decide la acción específica para una carta"""

        # Primero verificar comportamientos programados
        accion_comportamiento = self.gestor_comportamientos.evaluar_carta(
            carta, self.mapa, aliados, enemigos
        )

        # Si hay comportamiento programado con alta prioridad, usarlo
        if accion_comportamiento and accion_comportamiento.prioridad.value >= 4:
            decision = EstadoDecision(carta, accion_comportamiento, 0.9)
            decision.agregar_razon("Comportamiento programado de alta prioridad")
            return decision

        # Decidir según modo de IA
        if modo == ModoIA.DEFENSIVO:
            return self._decidir_defensivo(carta, situacion, aliados, enemigos)
        elif modo == ModoIA.AGRESIVO:
            return self._decidir_agresivo(carta, situacion, aliados, enemigos)
        elif modo == ModoIA.EXPLORADOR:
            return self._decidir_explorador(carta, situacion)
        else:  # PASIVO o default
            return self._decidir_pasivo(carta, situacion, aliados, enemigos, accion_comportamiento)

    def _decidir_defensivo(self, carta: CartaBase, situacion: Dict,
                           aliados: List[CartaBase], enemigos: List[CartaBase]) -> Optional[EstadoDecision]:
        """Toma decisiones defensivas"""

        # Prioridad 1: Huir si está en peligro crítico
        if situacion['debe_huir']:
            posicion_segura = self._encontrar_posicion_segura(carta, enemigos)
            if posicion_segura:
                accion = AccionIA("mover", posicion_segura, {'razon': 'huir_peligro'})
                decision = EstadoDecision(carta, accion, 0.95)
                decision.agregar_razon("Vida crítica, huyendo a posición segura")
                return decision

        # Prioridad 2: Usar habilidad de curación si disponible
        if situacion['prioridad_curacion'] and self.usar_habilidades:
            habilidad_curacion = self._buscar_habilidad_curacion(carta)
            if habilidad_curacion:
                accion = AccionIA("usar_habilidad", None, {'habilidad_id': habilidad_curacion})
                decision = EstadoDecision(carta, accion, 0.8)
                decision.agregar_razon("Usando habilidad de curación")
                return decision

        # Prioridad 3: Proteger aliado más débil
        aliado_debil = self._encontrar_aliado_mas_debil(carta, aliados)
        if aliado_debil:
            posicion_proteccion = self._calcular_posicion_proteccion(carta, aliado_debil)
            if posicion_proteccion:
                accion = AccionIA("mover", posicion_proteccion, {'razon': 'proteger_aliado'})
                decision = EstadoDecision(carta, accion, 0.6)
                decision.agregar_razon("Moviéndose para proteger aliado débil")
                return decision

        # Prioridad 4: Atacar defensivamente si es necesario
        if situacion['puede_atacar'] and not situacion['posicion_segura']:
            enemigo_mas_debil = self._encontrar_enemigo_mas_debil_en_rango(carta, enemigos)
            if enemigo_mas_debil:
                accion = AccionIA("atacar", enemigo_mas_debil, {'razon': 'defensa_activa'})
                decision = EstadoDecision(carta, accion, 0.5)
                decision.agregar_razon("Ataque defensivo contra enemigo débil")
                return decision

        return None

    def _decidir_agresivo(self, carta: CartaBase, situacion: Dict,
                          aliados: List[CartaBase], enemigos: List[CartaBase]) -> Optional[EstadoDecision]:
        """Toma decisiones agresivas"""

        # Prioridad 1: Atacar si puede
        if situacion['puede_atacar']:
            enemigo_prioritario = self._seleccionar_enemigo_prioritario(carta, enemigos)
            if enemigo_prioritario:
                accion = AccionIA("atacar", enemigo_prioritario, {'razon': 'ataque_agresivo'})
                decision = EstadoDecision(carta, accion, 0.9)
                decision.agregar_razon("Atacando enemigo prioritario")
                return decision

        # Prioridad 2: Moverse hacia enemigo más cercano
        enemigo_cercano = self._encontrar_enemigo_mas_cercano(carta, enemigos)
        if enemigo_cercano:
            posicion_acercamiento = self._calcular_posicion_acercamiento(carta, enemigo_cercano)
            if posicion_acercamiento:
                accion = AccionIA("mover", posicion_acercamiento, {'razon': 'perseguir_enemigo'})
                decision = EstadoDecision(carta, accion, 0.7)
                decision.agregar_razon("Persiguiendo enemigo más cercano")
                return decision

        # Prioridad 3: Usar habilidad ofensiva
        if self.usar_habilidades:
            habilidad_ofensiva = self._buscar_habilidad_ofensiva(carta)
            if habilidad_ofensiva:
                accion = AccionIA("usar_habilidad", None, {'habilidad_id': habilidad_ofensiva})
                decision = EstadoDecision(carta, accion, 0.6)
                decision.agregar_razon("Usando habilidad ofensiva")
                return decision

        return None

    def _decidir_explorador(self, carta: CartaBase, situacion: Dict) -> Optional[EstadoDecision]:
        """Toma decisiones de exploración"""

        # Moverse a posición aleatoria interesante
        posicion_exploracion = self._encontrar_posicion_exploracion(carta)
        if posicion_exploracion:
            accion = AccionIA("mover", posicion_exploracion, {'razon': 'explorar'})
            decision = EstadoDecision(carta, accion, 0.5)
            decision.agregar_razon("Explorando nueva área")
            return decision

        return None

    def _decidir_pasivo(self, carta: CartaBase, situacion: Dict, aliados: List[CartaBase],
                        enemigos: List[CartaBase], accion_comportamiento: Optional[AccionIA]) -> Optional[
        EstadoDecision]:
        """Toma decisiones pasivas usando comportamientos"""

        if accion_comportamiento:
            decision = EstadoDecision(carta, accion_comportamiento, 0.6)
            decision.agregar_razon("Siguiendo comportamiento automático")
            return decision

        # Comportamiento por defecto muy básico
        if situacion['puede_atacar'] and random.random() < self.factor_agresividad:
            enemigo_aleatorio = self._encontrar_enemigo_aleatorio(carta, enemigos)
            if enemigo_aleatorio:
                accion = AccionIA("atacar", enemigo_aleatorio, {'razon': 'ataque_automatico'})
                decision = EstadoDecision(carta, accion, 0.4)
                decision.agregar_razon("Ataque automático básico")
                return decision

        return None

    # === MÉTODOS AUXILIARES ===

    def _encontrar_posicion_segura(self, carta: CartaBase, enemigos: List[CartaBase]) -> Optional[Coordenada]:
        """Encuentra una posición segura lejos de enemigos"""
        if not carta.coordenada:
            return None

        posiciones_posibles = carta.coordenada.obtener_area(carta.rango_movimiento_actual)
        mejor_posicion = None
        mejor_distancia = 0

        for pos in posiciones_posibles:
            if pos in self.mapa.celdas and self.mapa.obtener_carta_en_posicion(pos) is None:
                distancia_min = min(
                    (pos.distancia_a(e.coordenada) for e in enemigos if e.esta_viva() and e.coordenada),
                    default=float('inf')
                )
                if distancia_min > mejor_distancia:
                    mejor_distancia = distancia_min
                    mejor_posicion = pos

        return mejor_posicion

    def _encontrar_enemigo_mas_cercano(self, carta: CartaBase, enemigos: List[CartaBase]) -> Optional[CartaBase]:
        """Encuentra el enemigo más cercano"""
        if not carta.coordenada:
            return None

        enemigos_validos = [(e, carta.coordenada.distancia_a(e.coordenada))
                            for e in enemigos if e.esta_viva() and e.coordenada]

        if enemigos_validos:
            enemigos_validos.sort(key=lambda x: x[1])
            return enemigos_validos[0][0]

        return None

    def _encontrar_aliado_mas_debil(self, carta: CartaBase, aliados: List[CartaBase]) -> Optional[CartaBase]:
        """Encuentra el aliado con menos vida"""
        aliados_validos = [a for a in aliados if a != carta and a.esta_viva()]

        if aliados_validos:
            return min(aliados_validos, key=lambda x: x.vida_actual / x.vida_maxima)

        return None

    def _seleccionar_enemigo_prioritario(self, carta: CartaBase, enemigos: List[CartaBase]) -> Optional[CartaBase]:
        """Selecciona enemigo prioritario (más débil en rango)"""
        if not carta.coordenada:
            return None

        enemigos_en_rango = [
            e for e in enemigos
            if e.esta_viva() and e.coordenada and
               carta.coordenada.distancia_a(e.coordenada) <= carta.rango_ataque_actual
        ]

        if enemigos_en_rango:
            return min(enemigos_en_rango, key=lambda x: x.vida_actual)

        return None

    def _calcular_posicion_acercamiento(self, carta: CartaBase, objetivo: CartaBase) -> Optional[Coordenada]:
        """Calcula posición para acercarse a un objetivo"""
        if not carta.coordenada or not objetivo.coordenada:
            return None

        posiciones_posibles = carta.coordenada.obtener_area(carta.rango_movimiento_actual)
        mejor_posicion = None
        menor_distancia = float('inf')

        for pos in posiciones_posibles:
            if pos in self.mapa.celdas and self.mapa.obtener_carta_en_posicion(pos) is None:
                distancia = pos.distancia_a(objetivo.coordenada)
                if distancia < menor_distancia:
                    menor_distancia = distancia
                    mejor_posicion = pos

        return mejor_posicion

    def _buscar_habilidad_curacion(self, carta: CartaBase) -> Optional[str]:
        """Busca habilidades de curación disponibles"""
        for i, habilidad in enumerate(carta.habilidades):
            if (habilidad.tipo == 'activa' and
                    carta.puede_usar_habilidad(i) and
                    'curac' in habilidad.nombre.lower()):
                return habilidad.nombre
        return None

    def _buscar_habilidad_ofensiva(self, carta: CartaBase) -> Optional[str]:
        """Busca habilidades ofensivas disponibles"""
        for i, habilidad in enumerate(carta.habilidades):
            if (habilidad.tipo == 'activa' and
                    carta.puede_usar_habilidad(i) and
                    any(palabra in habilidad.nombre.lower()
                        for palabra in ['ataque', 'daño', 'fuego', 'rayo', 'descarga'])):
                return habilidad.nombre
        return None

    def _encontrar_posicion_exploracion(self, carta: CartaBase) -> Optional[Coordenada]:
        """Encuentra una posición de exploración interesante"""
        if not carta.coordenada:
            return None

        posiciones_posibles = carta.coordenada.obtener_area(carta.rango_movimiento_actual)
        posiciones_libres = [
            pos for pos in posiciones_posibles
            if pos in self.mapa.celdas and self.mapa.obtener_carta_en_posicion(pos) is None
        ]

        if posiciones_libres:
            return random.choice(posiciones_libres)

        return None

    def _encontrar_enemigo_aleatorio(self, carta: CartaBase, enemigos: List[CartaBase]) -> Optional[CartaBase]:
        """Encuentra un enemigo aleatorio en rango"""
        if not carta.coordenada:
            return None

        enemigos_en_rango = [
            e for e in enemigos
            if e.esta_viva() and e.coordenada and
               carta.coordenada.distancia_a(e.coordenada) <= carta.rango_ataque_actual
        ]

        if enemigos_en_rango:
            return random.choice(enemigos_en_rango)

        return None

    def _encontrar_enemigo_mas_debil_en_rango(self, carta: CartaBase, enemigos: List[CartaBase]) -> Optional[CartaBase]:
        """Encuentra el enemigo más débil en rango de ataque"""
        return self._seleccionar_enemigo_prioritario(carta, enemigos)

    def _calcular_posicion_proteccion(self, carta: CartaBase, aliado: CartaBase) -> Optional[Coordenada]:
        """Calcula posición para proteger a un aliado"""
        if not carta.coordenada or not aliado.coordenada:
            return None

        # Buscar posiciones cerca del aliado
        posiciones_cerca = aliado.coordenada.obtener_vecinos()
        posiciones_validas = [
            pos for pos in posiciones_cerca
            if pos in self.mapa.celdas and self.mapa.obtener_carta_en_posicion(pos) is None
        ]

        if posiciones_validas:
            # Elegir la más cercana a nuestra carta
            return min(posiciones_validas,
                       key=lambda pos: carta.coordenada.distancia_a(pos))

        return None

    def obtener_estadisticas(self) -> Dict[str, any]:
        """Obtiene estadísticas del motor de IA"""
        stats_comportamientos = self.gestor_comportamientos.obtener_estadisticas()

        return {
            'modo_default': self.modo_default.value,
            'jugadores_configurados': len(self.modos_jugadores),
            'factor_agresividad': self.factor_agresividad,
            'factor_conservacion': self.factor_conservacion,
            'usar_habilidades': self.usar_habilidades,
            'comportamientos': stats_comportamientos
        }

    def __str__(self):
        return f"AIMotorDecision(modo={self.modo_default.value}, jugadores={len(self.modos_jugadores)})"