"""
Sistema de comportamientos preconfigurados y IA básica para cartas
Maneja las acciones automáticas cuando los jugadores están en modo pasivo
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from abc import ABC, abstractmethod
from src.game.cartas.carta_base import CartaBase
from src.game.tablero.tablero_hexagonal import Coordenada
from src.game.combate import MapaGlobal
from src.utils.helpers import log_evento


class TipoComportamiento(Enum):
    """Tipos de comportamientos preconfigurados"""
    AGRESIVO = "agresivo"
    DEFENSIVO = "defensivo"
    NEUTRAL = "neutral"
    HUIR = "huir"
    IR_A_POSICION = "ir_a_posicion"
    SEGUIR_ALIADO = "seguir_aliado"
    PROTEGER_OBJETIVO = "proteger_objetivo"
    PATRULLAR = "patrullar"


class PrioridadAccion(Enum):
    """Prioridades para las acciones de IA"""
    CRITICA = 5
    ALTA = 4
    MEDIA = 3
    BAJA = 2
    MUY_BAJA = 1


class AccionIA:
    """Representa una acción que puede tomar la IA"""

    def __init__(self, tipo: str, objetivo: Any = None, parametros: Dict[str, Any] = None,
                 prioridad: PrioridadAccion = PrioridadAccion.MEDIA):
        self.tipo = tipo
        self.objetivo = objetivo
        self.parametros = parametros or {}
        self.prioridad = prioridad
        self.costo_estimado = self.parametros.get('costo', 1.0)
        self.tiempo_estimado = self.parametros.get('tiempo', 1.0)

    def __str__(self):
        return f"AccionIA({self.tipo}, prioridad={self.prioridad.name})"


class ComportamientoBase(ABC):
    """Clase base para todos los comportamientos"""

    def __init__(self, tipo: TipoComportamiento, parametros: Dict[str, Any] = None):
        self.tipo = tipo
        self.parametros = parametros or {}
        self.activo = True

    @abstractmethod
    def evaluar_accion(self, carta: CartaBase, mapa: MapaGlobal,
                       cartas_aliadas: List[CartaBase], cartas_enemigas: List[CartaBase]) -> Optional[AccionIA]:
        """Evalúa y retorna la mejor acción para la carta según este comportamiento"""
        pass

    @abstractmethod
    def obtener_prioridad_base(self) -> PrioridadAccion:
        """Retorna la prioridad base de este comportamiento"""
        pass


class ComportamientoAgresivo(ComportamientoBase):
    """Comportamiento agresivo: busca y ataca enemigos cercanos"""

    def __init__(self, parametros: Dict[str, Any] = None):
        super().__init__(TipoComportamiento.AGRESIVO, parametros)
        self.rango_busqueda = self.parametros.get('rango_busqueda', 3)

    def evaluar_accion(self, carta: CartaBase, mapa: MapaGlobal,
                       cartas_aliadas: List[CartaBase], cartas_enemigas: List[CartaBase]) -> Optional[AccionIA]:

        if not carta.esta_viva() or not cartas_enemigas:
            return None

        # Buscar enemigo más cercano
        enemigo_cercano = self._encontrar_enemigo_mas_cercano(carta, cartas_enemigas, mapa)

        if enemigo_cercano:
            carta_enemiga, distancia = enemigo_cercano

            # Si está en rango de ataque, atacar
            if distancia <= carta.rango_ataque_actual:
                return AccionIA(
                    tipo="atacar",
                    objetivo=carta_enemiga,
                    parametros={'distancia': distancia},
                    prioridad=PrioridadAccion.ALTA
                )

            # Si no está en rango, moverse hacia el enemigo
            elif distancia <= self.rango_busqueda:
                posicion_objetivo = self._calcular_posicion_acercarse(carta, carta_enemiga, mapa)
                if posicion_objetivo:
                    return AccionIA(
                        tipo="mover",
                        objetivo=posicion_objetivo,
                        parametros={'razon': 'perseguir_enemigo'},
                        prioridad=PrioridadAccion.MEDIA
                    )

        return None

    def obtener_prioridad_base(self) -> PrioridadAccion:
        return PrioridadAccion.ALTA

    def _encontrar_enemigo_mas_cercano(self, carta: CartaBase, enemigos: List[CartaBase],
                                       mapa: MapaGlobal) -> Optional[Tuple[CartaBase, int]]:
        """Encuentra el enemigo más cercano"""
        if not carta.coordenada:
            return None

        enemigos_con_distancia = []
        for enemigo in enemigos:
            if enemigo.esta_viva() and enemigo.coordenada:
                distancia = carta.coordenada.distancia_a(enemigo.coordenada)
                enemigos_con_distancia.append((enemigo, distancia))

        if enemigos_con_distancia:
            enemigos_con_distancia.sort(key=lambda x: x[1])
            return enemigos_con_distancia[0]

        return None

    def _calcular_posicion_acercarse(self, carta: CartaBase, objetivo: CartaBase,
                                     mapa: MapaGlobal) -> Optional[Coordenada]:
        """Calcula una posición para acercarse al objetivo"""
        if not carta.coordenada or not objetivo.coordenada:
            return None

        # Buscar posiciones adyacentes al objetivo
        posiciones_cercanas = objetivo.coordenada.obtener_vecinos()

        # Filtrar posiciones válidas y libres
        posiciones_validas = []
        for pos in posiciones_cercanas:
            if pos in mapa.celdas and mapa.obtener_carta_en_posicion(pos) is None:
                distancia_desde_carta = carta.coordenada.distancia_a(pos)
                posiciones_validas.append((pos, distancia_desde_carta))

        if posiciones_validas:
            # Elegir la posición más cercana a nuestra carta
            posiciones_validas.sort(key=lambda x: x[1])
            return posiciones_validas[0][0]

        return None


class ComportamientoDefensivo(ComportamientoBase):
    """Comportamiento defensivo: protege aliados y evita combate directo"""

    def __init__(self, parametros: Dict[str, Any] = None):
        super().__init__(TipoComportamiento.DEFENSIVO, parametros)
        self.umbral_vida_critica = self.parametros.get('umbral_vida', 0.3)

    def evaluar_accion(self, carta: CartaBase, mapa: MapaGlobal,
                       cartas_aliadas: List[CartaBase], cartas_enemigas: List[CartaBase]) -> Optional[AccionIA]:

        if not carta.esta_viva():
            return None

        # Si tiene poca vida, priorizar huida
        porcentaje_vida = carta.vida_actual / carta.vida_maxima
        if porcentaje_vida <= self.umbral_vida_critica:
            posicion_segura = self._encontrar_posicion_segura(carta, cartas_enemigas, mapa)
            if posicion_segura:
                return AccionIA(
                    tipo="mover",
                    objetivo=posicion_segura,
                    parametros={'razon': 'huir_vida_baja'},
                    prioridad=PrioridadAccion.CRITICA
                )

        # Buscar aliado que necesite protección
        aliado_en_peligro = self._encontrar_aliado_en_peligro(carta, cartas_aliadas, cartas_enemigas)
        if aliado_en_peligro:
            posicion_proteccion = self._calcular_posicion_proteccion(carta, aliado_en_peligro, mapa)
            if posicion_proteccion:
                return AccionIA(
                    tipo="mover",
                    objetivo=posicion_proteccion,
                    parametros={'razon': 'proteger_aliado'},
                    prioridad=PrioridadAccion.ALTA
                )

        # Si hay enemigos muy cerca, atacar defensivamente
        enemigos_cercanos = self._encontrar_enemigos_en_rango(carta, cartas_enemigas, 2)
        if enemigos_cercanos:
            # Atacar al enemigo más débil
            enemigo_mas_debil = min(enemigos_cercanos, key=lambda x: x.vida_actual)
            return AccionIA(
                tipo="atacar",
                objetivo=enemigo_mas_debil,
                parametros={'razon': 'defensa_activa'},
                prioridad=PrioridadAccion.MEDIA
            )

        return None

    def obtener_prioridad_base(self) -> PrioridadAccion:
        return PrioridadAccion.MEDIA

    def _encontrar_posicion_segura(self, carta: CartaBase, enemigos: List[CartaBase],
                                   mapa: MapaGlobal) -> Optional[Coordenada]:
        """Encuentra una posición segura lejos de enemigos"""
        if not carta.coordenada:
            return None

        # Buscar posiciones en rango de movimiento
        posiciones_posibles = carta.coordenada.obtener_area(carta.rango_movimiento_actual)

        mejor_posicion = None
        mejor_distancia = 0

        for pos in posiciones_posibles:
            if pos in mapa.celdas and mapa.obtener_carta_en_posicion(pos) is None:
                # Calcular distancia mínima a enemigos
                distancia_min_enemigo = float('inf')
                for enemigo in enemigos:
                    if enemigo.esta_viva() and enemigo.coordenada:
                        dist = pos.distancia_a(enemigo.coordenada)
                        distancia_min_enemigo = min(distancia_min_enemigo, dist)

                # Preferir posiciones más lejas de enemigos
                if distancia_min_enemigo > mejor_distancia:
                    mejor_distancia = distancia_min_enemigo
                    mejor_posicion = pos

        return mejor_posicion

    def _encontrar_aliado_en_peligro(self, carta: CartaBase, aliados: List[CartaBase],
                                     enemigos: List[CartaBase]) -> Optional[CartaBase]:
        """Encuentra un aliado que necesite protección"""
        aliados_en_peligro = []

        for aliado in aliados:
            if not aliado.esta_viva() or aliado == carta:
                continue

            # Verificar si hay enemigos cerca del aliado
            enemigos_cerca = 0
            for enemigo in enemigos:
                if enemigo.esta_viva() and enemigo.coordenada and aliado.coordenada:
                    if enemigo.coordenada.distancia_a(aliado.coordenada) <= 2:
                        enemigos_cerca += 1

            if enemigos_cerca > 0:
                porcentaje_vida = aliado.vida_actual / aliado.vida_maxima
                prioridad = (1 - porcentaje_vida) + (enemigos_cerca * 0.2)
                aliados_en_peligro.append((aliado, prioridad))

        if aliados_en_peligro:
            aliados_en_peligro.sort(key=lambda x: x[1], reverse=True)
            return aliados_en_peligro[0][0]

        return None

    def _calcular_posicion_proteccion(self, carta: CartaBase, aliado: CartaBase,
                                      mapa: MapaGlobal) -> Optional[Coordenada]:
        """Calcula una posición para proteger a un aliado"""
        if not carta.coordenada or not aliado.coordenada:
            return None

        # Buscar posiciones cerca del aliado
        posiciones_cerca = aliado.coordenada.obtener_vecinos()

        mejor_posicion = None
        mejor_puntuacion = -1

        for pos in posiciones_cerca:
            if pos in mapa.celdas and mapa.obtener_carta_en_posicion(pos) is None:
                # Puntuación basada en cercanía a aliado y accesibilidad
                distancia_a_carta = carta.coordenada.distancia_a(pos)
                if distancia_a_carta <= carta.rango_movimiento_actual:
                    puntuacion = 10 - distancia_a_carta  # Preferir posiciones más cercanas
                    if puntuacion > mejor_puntuacion:
                        mejor_puntuacion = puntuacion
                        mejor_posicion = pos

        return mejor_posicion

    def _encontrar_enemigos_en_rango(self, carta: CartaBase, enemigos: List[CartaBase],
                                     rango: int) -> List[CartaBase]:
        """Encuentra enemigos dentro de un rango específico"""
        if not carta.coordenada:
            return []

        enemigos_en_rango = []
        for enemigo in enemigos:
            if enemigo.esta_viva() and enemigo.coordenada:
                if carta.coordenada.distancia_a(enemigo.coordenada) <= rango:
                    enemigos_en_rango.append(enemigo)

        return enemigos_en_rango


class ComportamientoIrAPosicion(ComportamientoBase):
    """Comportamiento para ir a una posición específica"""

    def __init__(self, parametros: Dict[str, Any] = None):
        super().__init__(TipoComportamiento.IR_A_POSICION, parametros)
        self.posicion_objetivo = self.parametros.get('posicion_objetivo')
        self.tolerancia = self.parametros.get('tolerancia', 1)

    def evaluar_accion(self, carta: CartaBase, mapa: MapaGlobal,
                       cartas_aliadas: List[CartaBase], cartas_enemigas: List[CartaBase]) -> Optional[AccionIA]:

        if not carta.esta_viva() or not self.posicion_objetivo or not carta.coordenada:
            return None

        distancia_al_objetivo = carta.coordenada.distancia_a(self.posicion_objetivo)

        # Si ya está cerca del objetivo, no hacer nada
        if distancia_al_objetivo <= self.tolerancia:
            self.activo = False  # Comportamiento completado
            return None

        # Calcular siguiente paso hacia el objetivo
        siguiente_posicion = self._calcular_siguiente_paso(carta, mapa)
        if siguiente_posicion:
            return AccionIA(
                tipo="mover",
                objetivo=siguiente_posicion,
                parametros={'razon': 'ir_a_posicion_objetivo'},
                prioridad=PrioridadAccion.MEDIA
            )

        return None

    def obtener_prioridad_base(self) -> PrioridadAccion:
        return PrioridadAccion.MEDIA

    def _calcular_siguiente_paso(self, carta: CartaBase, mapa: MapaGlobal) -> Optional[Coordenada]:
        """Calcula el siguiente paso hacia la posición objetivo"""
        if not carta.coordenada:
            return None

        # Buscar posiciones en rango de movimiento
        posiciones_posibles = carta.coordenada.obtener_area(carta.rango_movimiento_actual)

        mejor_posicion = None
        menor_distancia = float('inf')

        for pos in posiciones_posibles:
            if pos in mapa.celdas and mapa.obtener_carta_en_posicion(pos) is None:
                distancia_al_objetivo = pos.distancia_a(self.posicion_objetivo)
                if distancia_al_objetivo < menor_distancia:
                    menor_distancia = distancia_al_objetivo
                    mejor_posicion = pos

        return mejor_posicion


class GestorComportamientos:
    """Gestor principal de comportamientos de IA"""

    def __init__(self):
        self.comportamientos_por_carta: Dict[int, List[ComportamientoBase]] = {}
        self.comportamientos_default = {
            TipoComportamiento.AGRESIVO: ComportamientoAgresivo,
            TipoComportamiento.DEFENSIVO: ComportamientoDefensivo,
            TipoComportamiento.IR_A_POSICION: ComportamientoIrAPosicion
        }

    def asignar_comportamiento(self, carta_id: int, tipo: TipoComportamiento,
                               parametros: Dict[str, Any] = None) -> bool:
        """Asigna un comportamiento a una carta"""
        try:
            if tipo not in self.comportamientos_default:
                log_evento(f"❌ Tipo de comportamiento desconocido: {tipo}")
                return False

            comportamiento_class = self.comportamientos_default[tipo]
            comportamiento = comportamiento_class(parametros)

            if carta_id not in self.comportamientos_por_carta:
                self.comportamientos_por_carta[carta_id] = []

            self.comportamientos_por_carta[carta_id].append(comportamiento)

            log_evento(f"🤖 Comportamiento {tipo.value} asignado a carta {carta_id}")
            return True

        except Exception as e:
            log_evento(f"❌ Error asignando comportamiento: {e}")
            return False

    def limpiar_comportamientos(self, carta_id: int):
        """Limpia todos los comportamientos de una carta"""
        if carta_id in self.comportamientos_por_carta:
            del self.comportamientos_por_carta[carta_id]
            log_evento(f"🧹 Comportamientos limpiados para carta {carta_id}")

    def evaluar_carta(self, carta: CartaBase, mapa: MapaGlobal,
                      cartas_aliadas: List[CartaBase], cartas_enemigas: List[CartaBase]) -> Optional[AccionIA]:
        """Evalúa todos los comportamientos de una carta y retorna la mejor acción"""

        if not carta.esta_viva():
            return None

        carta_id = getattr(carta, 'id', None)
        if carta_id is None or carta_id not in self.comportamientos_por_carta:
            # Usar comportamiento default (neutral/agresivo)
            comportamiento_default = ComportamientoAgresivo()
            return comportamiento_default.evaluar_accion(carta, mapa, cartas_aliadas, cartas_enemigas)

        mejor_accion = None
        mejor_prioridad = PrioridadAccion.MUY_BAJA

        # Evaluar todos los comportamientos activos
        comportamientos_activos = [comp for comp in self.comportamientos_por_carta[carta_id] if comp.activo]

        for comportamiento in comportamientos_activos:
            accion = comportamiento.evaluar_accion(carta, mapa, cartas_aliadas, cartas_enemigas)

            if accion and accion.prioridad.value > mejor_prioridad.value:
                mejor_accion = accion
                mejor_prioridad = accion.prioridad

        # Limpiar comportamientos inactivos
        self.comportamientos_por_carta[carta_id] = comportamientos_activos

        return mejor_accion

    def procesar_todas_las_cartas(self, cartas_jugador: List[CartaBase], mapa: MapaGlobal,
                                  cartas_aliadas: List[CartaBase], cartas_enemigas: List[CartaBase]) -> Dict[
        CartaBase, AccionIA]:
        """Procesa todas las cartas de un jugador y retorna acciones recomendadas"""
        acciones = {}

        for carta in cartas_jugador:
            if carta.esta_viva():
                accion = self.evaluar_carta(carta, mapa, cartas_aliadas, cartas_enemigas)
                if accion:
                    acciones[carta] = accion

        return acciones

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del gestor de comportamientos"""
        total_cartas = len(self.comportamientos_por_carta)
        comportamientos_por_tipo = {}
        total_comportamientos = 0

        for carta_id, comportamientos in self.comportamientos_por_carta.items():
            total_comportamientos += len(comportamientos)
            for comp in comportamientos:
                tipo = comp.tipo.value
                comportamientos_por_tipo[tipo] = comportamientos_por_tipo.get(tipo, 0) + 1

        return {
            'cartas_con_comportamientos': total_cartas,
            'total_comportamientos': total_comportamientos,
            'comportamientos_por_tipo': comportamientos_por_tipo,
            'tipos_disponibles': list(self.comportamientos_default.keys())
        }

    def __str__(self):
        stats = self.obtener_estadisticas()
        return f"GestorComportamientos({stats['cartas_con_comportamientos']} cartas, {stats['total_comportamientos']} comportamientos)"