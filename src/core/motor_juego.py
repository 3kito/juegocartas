import time
import random

from src.core.jugador import Jugador
from src.data.config.game_config import GameConfig
from src.game.cartas.manager_cartas import manager_cartas
from src.game.combate.interacciones.gestor_interacciones import GestorInteracciones
from src.game.combate.mapa.mapa_global import MapaGlobal
from src.game.combate.motor.motor_tiempo_real import MotorTiempoReal
from src.utils.helpers import log_evento
from src.game.combate.fase.secuencia_turnos import generar_secuencia_turnos

from src.game.combate.fase.controlador_fase_enfrentamiento import ControladorFaseEnfrentamiento
from src.game.combate.fase.gestor_turnos import GestorTurnos
from src.game.fases.controlador_preparacion import ControladorFasePreparacion


class MotorJuego:
    def __init__(self, jugadores: list[Jugador] | None = None, on_step_callback=None):
        self.jugadores = jugadores
        self.jugadores_vivos = list(jugadores) if jugadores else []
        self.fase_actual = "preparacion"
        self.ronda = 1
        self.config = GameConfig()
        self.modo_testeo = self.config.modo_testeo

        self.controlador_enfrentamiento = None
        self.mapa_global = None
        self.on_step_callback = on_step_callback

        # Controlador especializado para la fase de preparación
        self.controlador_preparacion = ControladorFasePreparacion(
            self.jugadores_vivos,
            motor=self,
            config=self.config,
            modo_testeo=self.modo_testeo
        )


    def iniciar(self):
        log_evento("🎮 Iniciando juego...")

        # AGREGAR: Cargar base de datos de cartas
        if not manager_cartas.cartas_cargadas:
            manager_cartas.cargar_cartas()

        self._entregar_cartas_iniciales()

        self.controlador_preparacion.iniciar_fase(self.ronda)

    def _ejecutar_fase_combate(self):
        self.fase_actual = "combate"
        log_evento(f"⚔️ Fase de combate iniciada (Ronda {self.ronda})")
        if self.on_step_callback:
            try:
                self.on_step_callback(evento="transicion_fase")
            except TypeError:
                self.on_step_callback()

        # 1. Crear mapa global
        cant_jugadores = len(self.jugadores_vivos)
        cantidad_parejas = (cant_jugadores + 1) // 2
        mapa = MapaGlobal(cantidad_parejas=cantidad_parejas)
        self.mapa_global = mapa

        # Autocompletar tableros antes de ubicar jugadores
        self._autocompletar_tableros()

        # 2. Asignar jugadores a zonas
        jugadores_por_color = {"rojo": [], "azul": []}
        colores = ["rojo", "azul"]
        jugadores_ordenados = sorted(self.jugadores_vivos, key=lambda j: j.id)
        for idx, jugador in enumerate(jugadores_ordenados):
            color = colores[idx % len(colores)]
            jugador.color_fase_actual = color
            jugadores_por_color[color].append(jugador)
            mapa.ubicar_jugador_en_zona(jugador, color)

        # Aplicar comportamientos asignados a las cartas
        from src.game.cartas.carta_base import CartaBase
        for carta in mapa.tablero.celdas.values():
            if isinstance(carta, CartaBase) and getattr(carta, "comportamiento_asignado", None):
                carta.modo_control = carta.comportamiento_asignado
                log_evento(
                    f"🎯 {carta.nombre} inicia como '{carta.modo_control}'",
                    "DEBUG",
                )

        # 3. Crear gestor de interacciones y motor
        gestor = GestorInteracciones(tablero=mapa.tablero, on_step=self.on_step_callback)
        self.motor = MotorTiempoReal(fps_objetivo=20)
        gestor.motor = self.motor

        log_evento("🔧 Registrando GestorInteracciones...")
        self.motor.agregar_componente(gestor)
        log_evento(
            f"✅ Componentes activos: {self.motor.obtener_componentes_activos()}"
        )

        # Limpieza periódica de cartas muertas deshabilitada para mantener las cartas en el mapa
        # self.motor.iniciar_limpieza_cartas_muertas(self.mapa_global)

        # 4. Inicializar turnos y controlador
        secuencia = generar_secuencia_turnos()
        controlador = ControladorFaseEnfrentamiento(
            motor=self.motor,
            jugadores_por_color=jugadores_por_color,
            secuencia_turnos=secuencia,
            al_terminar_fase=self.transicionar_a_fase_preparacion,
            modo_testeo=self.modo_testeo
        )

        self.motor.agregar_componente(controlador)
        controlador.iniciar_fase()

        # Iniciar motor de tiempo real antes de continuar
        self.motor.iniciar()
        log_evento(
            f"🚀 Motor iniciado en modo {'testeo' if self.modo_testeo else 'normal'}"
        )

        self.controlador_enfrentamiento = controlador

        if not self.modo_testeo:
            while (
                not controlador.finalizada
                and self.motor.estado.value == "ejecutando"
            ):
                time.sleep(0.1)
    def transicionar_a_fase_preparacion(self):
        log_evento("🔄 Transición a fase de preparación...")
        if self.on_step_callback:
            try:
                self.on_step_callback(evento="transicion_fase")
            except TypeError:
                self.on_step_callback()

        # Limpiar mapa y controlador de combate
        self.mapa_global = None
        self.controlador_enfrentamiento = None

        # Eliminar jugadores muertos
        jugadores_antes = len(self.jugadores_vivos)
        self.jugadores_vivos = [j for j in self.jugadores_vivos if j.vida > 0]
        eliminados = jugadores_antes - len(self.jugadores_vivos)

        if eliminados:
            log_evento(f"💀 {eliminados} jugador(es) eliminado(s) por vida ≤ 0")

        # Verificar fin del juego
        if len(self.jugadores_vivos) <= 1:
            if self.jugadores_vivos:
                ganador = self.jugadores_vivos[0]
                log_evento(f"🏆 {ganador.nombre} gana la partida")
            else:
                log_evento("⚠️ Todos los jugadores fueron eliminados. Empate.")
            return  # No continuar si terminó el juego

        # Continuar con nueva ronda
        self.fase_actual = "preparacion"
        self.ronda += 1
        self.controlador_preparacion = ControladorFasePreparacion(
            self.jugadores_vivos,
            motor=self,
            config=self.config,
            modo_testeo=self.modo_testeo
        )
        self.controlador_preparacion.iniciar_fase(self.ronda)

    def get_tienda_para(self, jugador_id: int):
        """Devuelve la tienda individual de un jugador"""
        if hasattr(self, 'controlador_preparacion') and self.controlador_preparacion:
            return self.controlador_preparacion.obtener_tienda(jugador_id)
        else:
            log_evento(f"⚠️ No hay controlador de preparación activo para obtener tienda de jugador {jugador_id}")
            return None

    def get_subasta(self):
        """Devuelve el sistema de subastas activo"""
        if hasattr(self, 'controlador_preparacion') and self.controlador_preparacion:
            return self.controlador_preparacion.obtener_subasta()
        else:
            log_evento("⚠️ No hay controlador de preparación activo para obtener subasta")
            return None

    def iniciar_fase_enfrentamiento(self):
        self._ejecutar_fase_combate()

    # === MODO TESTEO ===
    def describir_proximo_paso(self) -> str:
        if self.fase_actual == "preparacion" and self.controlador_preparacion:
            return "Finalizar preparación"
        if self.fase_actual == "combate" and self.controlador_enfrentamiento:
            return f"Cambiar turno ({self.controlador_enfrentamiento.obtener_turno_activo()})"
        return "Sin acciones pendientes"

    def ejecutar_siguiente_paso(self):
        if self.fase_actual == "preparacion" and self.controlador_preparacion:
            self.controlador_preparacion.acelerar_temporizador()
        elif self.fase_actual == "combate" and self.controlador_enfrentamiento:
            self.controlador_enfrentamiento.acelerar_temporizador()

    # === MÉTODOS AUXILIARES ===
    def _entregar_cartas_iniciales(self):
        """Da a todos los jugadores una carta inicial de un mismo tier (1 o 2)"""
        if not self.jugadores_vivos:
            return

        tier = random.choice([1, 2])
        log_evento(f"🎁 Entregando carta inicial de tier {tier} a todos los jugadores")
        for jugador in self.jugadores_vivos:
            carta = manager_cartas.obtener_carta_aleatoria_tier(tier)
            if carta:
                jugador.agregar_carta_al_banco(carta)
            else:
                log_evento("⚠️ No se pudo obtener carta inicial", "WARNING")

    def _autocompletar_tableros(self):
        """Autocompleta los tableros de los jugadores con cartas de su banco"""
        for jugador in self.jugadores_vivos:
            jugador.autocompletar_tablero()

