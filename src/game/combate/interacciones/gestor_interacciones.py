# interacciones/gestor_interacciones.py

from typing import List
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

    def __init__(self, tablero=None, motor=None, on_step=None):
        self.interacciones_pendientes: List[Interaccion] = []
        self.tablero = tablero
        self.motor = motor
        self.on_step = on_step

    def registrar_interaccion(self, interaccion: Interaccion):
        log_evento(f"📨 Interacción registrada: {interaccion}", "DEBUG")
        self.interacciones_pendientes.append(interaccion)

    def procesar_tick(self, delta_time: float) -> bool:
        # 🔁 Generar interacciones u órdenes manuales
        log_evento("🔄 GestorInteracciones.procesar_tick() ejecutándose", "DEBUG")
        if not self.tablero:
            return True

        log_evento(
            f"📊 Revisando {len([c for c in self.tablero.celdas.values() if c])} cartas en tablero",
            "DEBUG",
        )

        cartas_activas = {
            carta.id: carta
            for carta in self.tablero.celdas.values()
            if carta is not None
        }

        log_evento(
            f"🚩 Tick de interacciones con {len(cartas_activas)} cartas",
            "DEBUG",
        )

        for carta in cartas_activas.values():
            log_evento(
                f"🔍 Revisando carta {carta.nombre} - tiene_orden_manual: {carta.tiene_orden_manual()}",
                "TRACE",
            )
            if carta.puede_actuar:
                if carta.tiene_orden_manual():
                    log_evento(
                        f"📝 ORDEN DETECTADA en {carta.nombre}: {carta.orden_actual}",
                        "DEBUG",
                    )
                    log_evento(
                        f"↪️ Ejecutando _procesar_orden_manual para {carta.nombre}",
                        "DEBUG",
                    )
                    self._procesar_orden_manual(carta)
                else:
                    nuevas = generar_interacciones_para(carta, self.tablero)
                    self.interacciones_pendientes.extend(nuevas)

        if not self.interacciones_pendientes:
            return True

        for interaccion in self.interacciones_pendientes:
            fuente = cartas_activas.get(interaccion.fuente_id)
            objetivo = cartas_activas.get(interaccion.objetivo_id)

            if not fuente or not objetivo:
                continue

            if interaccion.tipo == TipoInteraccion.ATAQUE:
                self._procesar_ataque(interaccion, fuente, objetivo)

        self.interacciones_pendientes.clear()
        return True

    def _procesar_ataque(self, interaccion: Interaccion, fuente, objetivo):
        dano = calcular_dano(fuente, objetivo, interaccion)
        aplicado = objetivo.recibir_dano(dano)
        fuente.registrar_ataque()

        log_evento(
            f"⚔️ {fuente.nombre} golpea a {objetivo.nombre} por {aplicado} daño (vida restante: {objetivo.vida_actual})"
        )

        fuente.stats_combate["dano_infligido"] += aplicado
        if not objetivo.esta_viva():
            fuente.stats_combate["enemigos_eliminados"] += 1
        else:
            if (
                getattr(objetivo, "tablero", None)
                and getattr(objetivo, "coordenada", None)
                and getattr(fuente, "coordenada", None)
                and objetivo.coordenada.distancia(fuente.coordenada)
                <= objetivo.rango_ataque_actual
                and objetivo.puede_actuar
                and objetivo.puede_atacar()
            ):
                from src.game.combate.ia.ia_utilidades import atacar_si_en_rango

                atacar_si_en_rango(objetivo, fuente)

        if self.on_step:
            try:
                self.on_step()
            except TypeError:
                self.on_step()

    def _procesar_orden_manual(self, carta):
        """Ejecuta la orden manual asignada a la carta"""
        orden = carta.orden_actual
        if not orden:
            return

        log_evento(
            f"⚙️ Procesando orden manual para {carta.nombre}: tipo={orden.get('tipo')}, progreso={orden.get('progreso')}",
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
                    on_step=self.on_step,
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
                log_evento(
                    f"🎯 Orden de ataque contra {objetivo.nombre} para {carta.nombre}",
                    "DEBUG",
                )
                iniciar_ataque_continuo(
                    carta,
                    objetivo,
                    self.tablero,
                    self.motor,
                    on_step=self.on_step,
                )
                orden["progreso"] = "completada"

        elif orden["tipo"] == "cambiar_comportamiento":
            nuevo = orden.get("datos_adicionales", {}).get("nuevo_comportamiento")
            if nuevo:
                log_evento(
                    f"🔄 Cambiando comportamiento de {carta.nombre} a '{nuevo}'",
                    "DEBUG",
                )
                carta.modo_control = nuevo
            orden["progreso"] = "completada"

        if orden["progreso"] == "completada":
            log_evento(
                f"✅ Orden '{orden.get('tipo')}' completada para {carta.nombre}",
                "DEBUG",
            )
            carta.limpiar_orden_manual()


    def obtener_estadisticas(self):
        cartas_en_tablero = (
            len([c for c in self.tablero.celdas.values() if c is not None])
            if self.tablero
            else 0
        )
        return {
            "interacciones_en_cola": len(self.interacciones_pendientes),
            "cartas_registradas": cartas_en_tablero,
        }

    def obtener_id_componente(self) -> str:
        return f"interacciones_{id(self)}"


# Exponer la clase en builtins para compatibilidad con algunos tests
import builtins
builtins.GestorInteracciones = GestorInteracciones
