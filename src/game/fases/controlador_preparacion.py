from src.game.cartas.fusion_cartas import aplicar_fusiones
from src.game.tienda.tienda_individual import TiendaIndividual
from src.game.tienda.sistema_subastas import SistemaSubastas
from src.utils.helpers import log_evento
from src.data.config.game_config import GameConfig


class ControladorFasePreparacion:
    def __init__(self, jugadores: list, motor=None, config=None, modo_testeo: bool = False):
        self.jugadores = jugadores
        self.motor = motor
        self.config = config or GameConfig()
        self.modo_testeo = modo_testeo
        self.tiendas_individuales = {}
        self.subastas = None
        self.finalizada = False

    def iniciar_fase(self, ronda: int):
        log_evento(f"📦 Fase de preparación iniciada (Ronda {ronda})")

        if not self.modo_testeo:
            self.entregar_oro()
            self.generar_tiendas()
            self.generar_subasta_publica()
            self.aplicar_fusiones_automaticas()

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
        self.subastas = SistemaSubastas(self.jugadores, modo_testeo=self.modo_testeo)
        self.subastas.generar_subasta(cartas_subasta)

    def pausar_para_ofertas(self):
        """Pausa el flujo para permitir a los jugadores ofertar manualmente"""
        log_evento("⏸️ Pausa para ofertas - esperando ofertas de jugadores")

    def aplicar_fusiones_automaticas(self):
        for jugador in self.jugadores:
            eventos = aplicar_fusiones(jugador.tablero, jugador.cartas_banco)
            for evento in eventos:
                log_evento(f"🔧 {jugador.nombre}: {evento}")

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
