from src.game.tienda.tienda_individual import TiendaIndividual
from src.game.tienda.sistema_subastas import SistemaSubastas
from src.utils.helpers import log_evento
from src.data.config.game_config import GameConfig
import time


class ControladorFasePreparacion:
    def __init__(self, jugadores: list, motor=None, config=None, modo_testeo: bool = False):
        self.jugadores = jugadores
        self.motor = motor
        self.config = config or GameConfig()
        self.modo_testeo = modo_testeo
        self.tiendas_individuales = {}
        self.subastas = None
        self.finalizada = False
        self.fin_fase = None
        self._temporizador = None

    def iniciar_fase(self, ronda: int):
        log_evento(f"📦 Fase de preparación iniciada (Ronda {ronda})")

        self.entregar_oro()
        self.generar_tiendas()
        self.generar_subasta_publica()
        self.iniciar_temporizador()

    def entregar_oro(self):
        for jugador in self.jugadores:
            jugador.oro += self.config.oro_por_ronda
            log_evento(f"💰 {jugador.nombre} recibe {self.config.oro_por_ronda} de oro (Total: {jugador.oro})")

    def generar_tiendas(self):
        for jugador in self.jugadores:
            tienda = TiendaIndividual(jugador, cantidad_cartas=5)
            self.tiendas_individuales[jugador.id] = tienda
            log_evento(f"🛒 Tienda creada para {jugador.nombre}")

    def generar_subasta_publica(self):
        cartas_subasta = max(2, len(self.jugadores))
        self.subastas = SistemaSubastas(self.jugadores, modo_testeo=self.modo_testeo, config=self.config)
        self.subastas.generar_subasta(cartas_subasta)

    def iniciar_temporizador(self):
        """Inicia un temporizador automático para finalizar la fase"""
        motor = None
        if hasattr(self.motor, "programar_evento"):
            motor = self.motor
        elif hasattr(self.motor, "motor") and hasattr(self.motor.motor, "programar_evento"):
            motor = self.motor.motor

        duracion = 999999 if self.modo_testeo else self.config.fase_preparacion_segundos

        if motor:
            self._temporizador = motor.programar_evento(self.finalizar_fase, duracion)
            log_evento(f"⏰ Temporizador de preparación: {duracion}s")
        else:
            try:
                import threading

                self._temporizador = threading.Timer(duracion, self.finalizar_fase)
                self._temporizador.start()
                log_evento(f"⏰ Temporizador de preparación (threading) {duracion}s")
            except Exception as e:
                log_evento(f"❌ No se pudo iniciar temporizador: {e}")

        self.fin_fase = time.time() + duracion

    def pausar_para_ofertas(self):
        """Pausa el flujo para permitir a los jugadores ofertar manualmente"""
        log_evento("⏸️ Pausa para ofertas - esperando ofertas de jugadores")

    def obtener_tienda(self, jugador_id: int):
        """Retorna la tienda individual de un jugador específico"""
        if jugador_id in self.tiendas_individuales:
            return self.tiendas_individuales[jugador_id]
        else:
            log_evento(f"⚠️ No se encontró tienda para jugador ID {jugador_id}")
            return None

    def obtener_subasta(self):
        """Retorna el sistema de subastas activo"""
        if self.subastas:
            return self.subastas
        else:
            log_evento("⚠️ No hay sistema de subastas activo")
            return None

    def obtener_estado_tiendas(self):
        """Retorna información de todas las tiendas activas"""
        estado = {}
        for jugador_id, tienda in self.tiendas_individuales.items():
            # Buscar el nombre del jugador
            nombre_jugador = "Desconocido"
            for jugador in self.jugadores:
                if jugador.id == jugador_id:
                    nombre_jugador = jugador.nombre
                    break

            estado[jugador_id] = {
                'nombre_jugador': nombre_jugador,
                'cartas_disponibles': len(tienda.cartas_disponibles),
                'cartas_info': tienda.mostrar_cartas()
            }
        return estado

    def obtener_estado_subasta(self):
        """Retorna información del estado actual de la subasta"""
        if not self.subastas:
            return None

        return {
            'cartas_en_subasta': len(self.subastas.cartas_subastadas),
            'estado_actual': self.subastas.ver_estado_actual(),
            'tiempo_restante': getattr(self.subastas, 'tiempo_restante', 0)
        }

    def obtener_tiempo_restante(self) -> float:
        """Devuelve los segundos restantes para que termine la fase"""
        if self.fin_fase is None:
            return 0.0
        return max(0.0, self.fin_fase - time.time())

    def acelerar_temporizador(self, segundos: int = 2):
        """Reduce el temporizador activo a los segundos indicados"""
        if self.finalizada or self.fin_fase is None:
            return

        # Cancelar temporizador existente si es un threading.Timer
        if isinstance(self._temporizador, object) and hasattr(self._temporizador, "cancel"):
            try:
                self._temporizador.cancel()
            except Exception:
                pass

        self.fin_fase = time.time() + segundos

        if hasattr(self.motor, "eventos_programados") and isinstance(self._temporizador, str):
            evento = self.motor.eventos_programados.get(self._temporizador)
            if evento:
                evento.tiempo_ejecucion = self.fin_fase
        else:
            import threading

            self._temporizador = threading.Timer(segundos, self.finalizar_fase)
            self._temporizador.start()

    def realizar_compra_tienda(self, jugador_id: int, indice_carta: int):
        """Facilita la compra de una carta en tienda individual"""
        tienda = self.obtener_tienda(jugador_id)
        if not tienda:
            return "❌ Tienda no encontrada"

        return tienda.comprar_carta(indice_carta)

    def realizar_reroll_tienda(self, jugador_id: int):
        """Facilita el reroll de una tienda individual"""
        tienda = self.obtener_tienda(jugador_id)
        if not tienda:
            return "❌ Tienda no encontrada"

        return tienda.hacer_reroll()

    def realizar_oferta_subasta(self, jugador_id: int, carta_id: int, monto: int):
        """Facilita realizar una oferta en subasta"""
        if not self.subastas:
            return "❌ No hay subasta activa"

        # Buscar el jugador
        jugador = None
        for j in self.jugadores:
            if j.id == jugador_id:
                jugador = j
                break

        if not jugador:
            return "❌ Jugador no encontrado"

        return self.subastas.ofertar(jugador, carta_id, monto)

    def hay_tiendas_activas(self):
        """Verifica si hay tiendas activas"""
        return len(self.tiendas_individuales) > 0

    def hay_subasta_activa(self):
        """Verifica si hay una subasta activa"""
        return self.subastas is not None

    def cerrar_tiendas(self):
        """Cierra todas las tiendas y devuelve cartas no compradas al pool"""
        if not self.tiendas_individuales:
            return

        log_evento("🏪 Cerrando tiendas individuales...")

        for jugador_id, tienda in self.tiendas_individuales.items():
            # Las cartas no compradas se devuelven automáticamente al pool
            # cuando la tienda se destruye (esto debería estar en el destructor de TiendaIndividual)
            cartas_no_compradas = len(tienda.cartas_disponibles)
            if cartas_no_compradas > 0:
                log_evento(f"   🔄 {cartas_no_compradas} cartas no compradas devueltas al pool")

        self.tiendas_individuales.clear()

    def cerrar_subasta(self):
        """Cierra la subasta y resuelve las ofertas pendientes"""
        if not self.subastas:
            return

        log_evento("🏛️ Cerrando subasta y resolviendo ofertas...")
        self.subastas.resolver_subastas()
        self.subastas = None

    def finalizar_fase(self):
        """Finaliza la fase de preparación limpiando recursos"""
        if self.finalizada:
            return

        log_evento("📦 Finalizando fase de preparación...")

        # Cerrar tiendas y subastas
        self.cerrar_tiendas()
        self.cerrar_subasta()

        self.finalizada = True
        log_evento("📦 Fase de preparación finalizada")

        # Iniciar la siguiente fase
        if hasattr(self.motor, 'iniciar_fase_enfrentamiento'):
            self.motor.iniciar_fase_enfrentamiento()
        else:
            log_evento("⚠️ Motor no tiene método iniciar_fase_enfrentamiento")

    def obtener_resumen_fase(self):
        """Retorna un resumen completo del estado de la fase"""
        return {
            'finalizada': self.finalizada,
            'jugadores_activos': len(self.jugadores),
            'tiendas_activas': len(self.tiendas_individuales),
            'subasta_activa': self.hay_subasta_activa(),
            'estado_tiendas': self.obtener_estado_tiendas(),
            'estado_subasta': self.obtener_estado_subasta()
        }

    def __str__(self):
        return f"ControladorFasePreparacion(jugadores={len(self.jugadores)}, tiendas={len(self.tiendas_individuales)}, finalizada={self.finalizada})"

    def __repr__(self):
        return f"ControladorFasePreparacion(jugadores={len(self.jugadores)}, finalizada={self.finalizada})"
