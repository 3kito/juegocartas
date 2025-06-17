# interacciones/gestor_interacciones.py

from typing import List
from src.game.cartas.estado_carta import EstadoCarta  # Cada carta tiene un estado de combate
from src.game.combate.calcular_dano.calculadora_dano import calcular_dano
from src.game.combate.ia.ia_motor import generar_interacciones_para
from src.game.combate.interacciones.interaccion_modelo import Interaccion, TipoInteraccion
from src.game.combate.ia.ia_utilidades import (
    mover_carta_con_pathfinding,
    atacar_si_en_rango,
    iniciar_ataque_continuo,
)
from src.utils.helpers import log_evento


class GestorInteracciones:
    """
    Procesador central de interacciones entre cartas.
    Se ejecuta como componente dentro del motor de tiempo real.
    """

    def __init__(self, tablero=None, motor=None):
        self.interacciones_pendientes: List[Interaccion] = []
        self.estados_cartas: dict[int, EstadoCarta] = {}  # ID de carta → EstadoCarta
        self.tablero = tablero
        self.motor = motor
    def registrar_estado_carta(self, estado: EstadoCarta):
        self.estados_cartas[estado.id_carta] = estado

    def registrar_interaccion(self, interaccion: Interaccion):
        log_evento(f"📨 Interacción registrada: {interaccion}")
        self.interacciones_pendientes.append(interaccion)

    def procesar_tick(self, delta_time: float) -> bool:
        # 🔁 Generar interacciones u órdenes manuales
        log_evento(
            f"🚩 Tick de interacciones con {len(self.estados_cartas)} cartas", "DEBUG"
        )
        for estado in self.estados_cartas.values():
            carta = estado.carta
            if self.tablero and carta.puede_actuar:
                if carta.tiene_orden_manual():
                    log_evento(
                        f"🔎 {carta.nombre} tiene orden manual pendiente", "DEBUG"
                    )
                    self._procesar_orden_manual(estado)
                else:
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

    def _procesar_orden_manual(self, estado: EstadoCarta):
        """Ejecuta la orden manual asignada a la carta"""
        carta = estado.carta
        orden = carta.orden_actual
        if not orden:
            return

        log_evento(
            f"📝 Procesando orden '{orden.get('tipo')}' para {carta.nombre}",
            "DEBUG",
        )

        if orden["progreso"] == "pendiente":
            orden["progreso"] = "ejecutando"

        if orden["tipo"] == "mover":
            destino = orden.get("objetivo")
            if destino is None:
                orden["progreso"] = "completada"
            else:
                log_evento(
                    f"🧭 Orden de movimiento a {destino} para {carta.nombre}",
                    "DEBUG",
                )
                log_evento(
                    f"📌 Ejecutando pathfinding de {carta.nombre}", "DEBUG"
                )
                exito = mover_carta_con_pathfinding(
                    carta,
                    destino,
                    self.tablero,
                    motor=self.motor,
                )
                log_evento(
                    f"⏳ Movimiento programado ({'ok' if exito else 'fallo'})",
                    "DEBUG",
                )
                # La orden se marca completada inmediatamente; el movimiento
                # continuará mediante eventos del motor
                orden["progreso"] = "completada"

        elif orden["tipo"] == "atacar":
            objetivo = orden.get("objetivo")
            if objetivo is None or not objetivo.esta_viva():
                orden["progreso"] = "completada"
            else:
                iniciar_ataque_continuo(carta, objetivo, self.tablero, self.motor)
                orden["progreso"] = "completada"

        elif orden["tipo"] == "cambiar_comportamiento":
            nuevo = orden.get("datos_adicionales", {}).get("nuevo_comportamiento")
            if nuevo:
                carta.modo_control = nuevo
            orden["progreso"] = "completada"

        if orden["progreso"] == "completada":
            log_evento(
                f"✅ Orden '{orden.get('tipo')}' completada para {carta.nombre}",
                "DEBUG",
            )
            carta.limpiar_orden_manual()


    def obtener_estadisticas(self):
        return {
            "interacciones_en_cola": len(self.interacciones_pendientes),
            "cartas_registradas": len(self.estados_cartas)
        }

    def obtener_id_componente(self) -> str:
        return "interacciones"


# Exponer la clase en builtins para compatibilidad con algunos tests
import builtins
builtins.GestorInteracciones = GestorInteracciones
