# interacciones/gestor_interacciones.py

from typing import List
from src.game.cartas.estado_carta import EstadoCarta  # Cada carta tiene un estado de combate
from src.game.combate.calcular_dano.calculadora_dano import calcular_dano
from src.game.combate.ia.ia_motor import generar_interacciones_para
from src.game.combate.interacciones.interaccion_modelo import Interaccion, TipoInteraccion
from src.utils.helpers import log_evento


class GestorInteracciones:
    """
    Procesador central de interacciones entre cartas.
    Se ejecuta como componente dentro del motor de tiempo real.
    """

    def __init__(self, tablero=None):
        self.interacciones_pendientes: List[Interaccion] = []
        self.estados_cartas: dict[int, EstadoCarta] = {}  # ID de carta → EstadoCarta
        self.tablero = tablero
    def registrar_estado_carta(self, estado: EstadoCarta):
        self.estados_cartas[estado.id_carta] = estado

    def registrar_interaccion(self, interaccion: Interaccion):
        log_evento(f"📨 Interacción registrada: {interaccion}")
        self.interacciones_pendientes.append(interaccion)

    def procesar_tick(self, delta_time: float) -> bool:
        # 🔁 Generar interacciones automáticas de cartas activas
        for estado in self.estados_cartas.values():
            carta = estado.carta
            if self.tablero and carta.puede_actuar and not carta.tiene_orden_manual():
                nuevas = generar_interacciones_para(carta, self.tablero)
                self.interacciones_pendientes.extend(nuevas)

        if not self.interacciones_pendientes:
            return True

        for interaccion in self.interacciones_pendientes:
            fuente = self.estados_cartas.get(interaccion.fuente_id)
            objetivo = self.estados_cartas.get(interaccion.objetivo_id)

            if not fuente or not objetivo:
                continue

            if interaccion.tipo == TipoInteraccion.ATAQUE:
                self._procesar_ataque(interaccion, fuente, objetivo)

        self.interacciones_pendientes.clear()
        return True

    def _procesar_ataque(self, interaccion: Interaccion, fuente: EstadoCarta, objetivo: EstadoCarta):
        # Registrar en log
        log_evento(f"⚔️ {fuente.nombre} ataca a {objetivo.nombre}")

        # Aplicar daño
        dano = calcular_dano(fuente, objetivo, interaccion)
        objetivo.recibir_dano(dano)


    def obtener_estadisticas(self):
        return {
            "interacciones_en_cola": len(self.interacciones_pendientes),
            "cartas_registradas": len(self.estados_cartas)
        }

    def obtener_id_componente(self) -> str:
        return "interacciones"
