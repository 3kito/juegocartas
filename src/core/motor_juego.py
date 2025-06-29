import random
import time

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
    def __init__(self, jugadores: list[Jugador]):
        self.jugadores = jugadores
        self.jugadores_vivos = list(jugadores)
        self.fase_actual = "preparacion"
        self.ronda = 1
        # Controlador especializado para la fase de preparación
        self.config = GameConfig()
        self.controlador_preparacion = ControladorFasePreparacion(self.jugadores_vivos, motor=self, config=self.config)

    def iniciar(self):
        log_evento("🎮 Iniciando juego...")

        # AGREGAR: Cargar base de datos de cartas
        if not manager_cartas.cartas_cargadas:
            manager_cartas.cargar_cartas()


        self.controlador_preparacion.iniciar_fase(self.ronda)

    def _ejecutar_fase_combate(self):
        self.fase_actual = "combate"
        log_evento(f"⚔️ Fase de combate iniciada (Ronda {self.ronda})")

        # 1. Crear mapa global
        mapa = MapaGlobal()

        # 2. Asignar jugadores a zonas
        jugadores_por_color = {"rojo": [], "azul": []}
        for jugador in self.jugadores_vivos:
            color = random.choice(["rojo", "azul"])
            jugador.color_fase_actual = color
            jugadores_por_color[color].append(jugador)
            mapa.ubicar_jugador_en_zona(jugador, color)

        # 3. Crear gestor de interacciones y motor
        gestor = GestorInteracciones(tablero=mapa.tablero)
        self.motor = MotorTiempoReal(fps_objetivo=20)
        self.motor.agregar_componente(gestor)

        # 4. Inicializar turnos y controlador
        secuencia = generar_secuencia_turnos()
        controlador = ControladorFaseEnfrentamiento(
            motor=self.motor,
            jugadores_por_color=jugadores_por_color,
            secuencia_turnos=secuencia,
            al_terminar_fase=self.transicionar_a_fase_preparacion
        )

        self.motor.agregar_componente(controlador)
        controlador.iniciar_fase()

        # 5. Ejecutar motor de tiempo real
        self.motor.iniciar()
        while not controlador.finalizada and self.motor.estado.value == "ejecutando":
            time.sleep(0.1)
    def transicionar_a_fase_preparacion(self):
        log_evento("🔄 Transición a fase de preparación...")

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
        self.controlador_preparacion = ControladorFasePreparacion(self.jugadores_vivos, motor=self, config=self.config)
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

