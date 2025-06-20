# interfaces/main_gui.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time

from src.utils.helpers import log_evento
from src.data.config.game_config import GameConfig

from src.core.jugador import Jugador
from src.core.motor_juego import MotorJuego
from src.game.combate.mapa.mapa_global import MapaGlobal
from src.utils.hex_utils import pixel_to_hex, hex_to_pixel
from src.interfaces.gui.game_panels.testing_panel import PanelTesteo


class AutoBattlerGUI:
    def __init__(self):
        self.config = GameConfig()
        self.modo_testeo = self.config.modo_testeo
        self.motor = None
        self.jugador_actual = None
        self.jugadores = []
        self.panel_testeo = None  # panel incrustado

        # Ventana principal
        self.root = tk.Tk()
        self.root.title("Auto-Battler Test Interface")
        self.root.geometry("1200x800")

        # Configuración de tablero
        self.hex_size = 30
        self.board_center = (300, 250)
        self.hover_hex = None
        self.modo_mover_carta = False
        self.coordenada_origen = None
        self._ultima_fase_mapa = None
        self._ultimo_estado_mapa = None
        self._jugador_prev = None
        self._panel_coords = []
        self.carta_seleccionada = None
        self.ui_mode = "normal"  # normal, seleccionar_destino
        self.var_mostrar_coordenadas = tk.BooleanVar(value=True)

        self.crear_interfaz_principal()
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        self.root.after(500, self.refrescar_temporizadores)

    def crear_interfaz_principal(self):
        # Frame superior - Info del juego
        info_frame = ttk.Frame(self.root)
        info_frame.pack(fill="x", padx=10, pady=5)

        self.lbl_ronda = ttk.Label(info_frame, text="Ronda: -", font=("Arial", 12))
        self.lbl_ronda.pack(side="left")

        self.lbl_fase = ttk.Label(info_frame, text="Fase: -", font=("Arial", 12))
        self.lbl_fase.pack(side="left", padx=(20, 0))
        self.lbl_tiempo_fase = ttk.Label(info_frame, text="Tiempo restante: -", font=("Arial", 12))
        self.lbl_tiempo_fase.pack(side="left", padx=(20, 0))

        # Botones de control
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(control_frame, text="Iniciar Juego (2 jugadores)",
                   command=self.iniciar_juego).pack(side="left")
        ttk.Button(control_frame, text="Cambiar Jugador",
                   command=self.cambiar_jugador).pack(side="left", padx=(10, 0))

        # Selector de jugador
        self.combo_jugador = ttk.Combobox(control_frame, state="readonly")
        self.combo_jugador.pack(side="left", padx=(10, 0))
        self.combo_jugador.bind('<<ComboboxSelected>>', self.on_jugador_changed)

        # Contenedor principal para las vistas y el panel de testeo
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Notebook para las diferentes vistas
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(side="left", fill="both", expand=True)

        # Panel de testeo (inicialmente oculto)
        self.panel_testeo = PanelTesteo(self.main_frame, None, lambda: self.jugador_actual)
        self.panel_testeo.pack(side="right", fill="y", padx=(10, 0))
        self.panel_testeo.pack_forget()

        # Tabs
        self.crear_tab_estado()
        self.crear_tab_tienda()
        self.crear_tab_subasta()
        self.crear_tab_tablero()
        self.crear_tab_enfrentamiento()



    def crear_tab_estado(self):
        # Tab de estado general del jugador
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Estado")

        # Info del jugador
        info_frame = ttk.LabelFrame(frame, text="Información del Jugador")
        info_frame.pack(fill="x", padx=10, pady=5)

        self.lbl_jugador_info = ttk.Label(info_frame, text="Selecciona un jugador")
        self.lbl_jugador_info.pack(pady=10)

        # Banco de cartas
        banco_frame = ttk.LabelFrame(frame, text="Banco de Cartas")
        banco_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.listbox_banco = tk.Listbox(banco_frame)
        self.listbox_banco.pack(fill="both", expand=True, padx=5, pady=5)

        # Controles de experiencia
        exp_frame = ttk.LabelFrame(frame, text="Experiencia")
        exp_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(exp_frame, text="Oro a convertir:").pack(side="left")
        self.entry_oro_experiencia = ttk.Entry(exp_frame, width=10)
        self.entry_oro_experiencia.pack(side="left", padx=(5, 0))
        ttk.Button(
            exp_frame,
            text="Comprar Experiencia",
            command=self.comprar_experiencia,
        ).pack(side="left", padx=5)
        self.lbl_costo_experiencia = ttk.Label(exp_frame, text="Costo actual: -")
        self.lbl_costo_experiencia.pack(side="left", padx=5)
        self.lbl_exp_disponible = ttk.Label(exp_frame, text="Exp: 0")
        self.lbl_exp_disponible.pack(side="left", padx=5)

        # (Botón mover al tablero eliminado)

    def crear_tab_tienda(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Tienda Individual")

        # Lista de cartas disponibles
        cartas_frame = ttk.LabelFrame(frame, text="Cartas Disponibles")
        cartas_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.listbox_tienda = tk.Listbox(cartas_frame)
        self.listbox_tienda.pack(fill="both", expand=True, padx=5, pady=5)

        # Botones de tienda
        btn_frame = ttk.Frame(cartas_frame)
        btn_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(btn_frame, text="Comprar Carta",
                   command=self.comprar_carta).pack(side="left")
        ttk.Button(btn_frame, text="Reroll Tienda",
                   command=self.reroll_tienda).pack(side="left", padx=(10, 0))

    def crear_tab_subasta(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Subasta Pública")

        # Lista de cartas en subasta
        subasta_frame = ttk.LabelFrame(frame, text="Cartas en Subasta")
        subasta_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree_subasta = ttk.Treeview(subasta_frame, columns=("carta", "oferta_actual", "jugador"))
        self.tree_subasta.heading("#0", text="ID")
        self.tree_subasta.heading("carta", text="Carta")
        self.tree_subasta.heading("oferta_actual", text="Oferta Actual")
        self.tree_subasta.heading("jugador", text="Mejor Postor")
        self.tree_subasta.pack(fill="both", expand=True, padx=5, pady=5)

        # Frame para ofertar
        ofertar_frame = ttk.Frame(subasta_frame)
        ofertar_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(ofertar_frame, text="Oferta:").pack(side="left")
        self.entry_oferta = ttk.Entry(ofertar_frame, width=10)
        self.entry_oferta.pack(side="left", padx=(5, 0))
        ttk.Button(ofertar_frame, text="Ofertar",
                   command=self.hacer_oferta).pack(side="left", padx=(10, 0))

    def crear_tab_tablero(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Tablero")

        # Canvas para dibujar el tablero hexagonal
        self.canvas_tablero = tk.Canvas(frame, bg="lightgray", width=600, height=500)
        self.canvas_tablero.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.canvas_tablero.bind("<Button-1>", self.on_canvas_click)
        self.canvas_tablero.bind("<Motion>", self.on_canvas_motion)

        # Panel lateral con controles
        control_frame = ttk.Frame(frame)
        control_frame.pack(side="right", fill="y", padx=10, pady=10)

        ttk.Label(control_frame, text="Cartas en Tablero:").pack()
        self.listbox_tablero = tk.Listbox(control_frame, width=25)
        self.listbox_tablero.pack(fill="both", expand=True, pady=(5, 10))
        self.listbox_tablero.bind('<<ListboxSelect>>', self.preparar_mover_carta)

        ttk.Button(control_frame, text="Quitar del Tablero",
                   command=self.quitar_carta_tablero).pack(fill="x")

        ttk.Label(control_frame, text="Movimiento:").pack(pady=(5, 0))
        self.combo_movimiento = ttk.Combobox(
            control_frame,
            state="readonly",
            values=[
                "explorador",
                "merodeador",
                "seguidor",
                "huir",
                "regreso",
                "parado",
                "cazador",
            ],
        )
        self.combo_movimiento.current(0)
        self.combo_movimiento.pack(fill="x")

        ttk.Label(control_frame, text="Combate:").pack(pady=(5, 0))
        self.combo_combate = ttk.Combobox(
            control_frame,
            state="readonly",
            values=["agresivo", "defensivo", "guardian", "ignorar"],
        )
        self.combo_combate.current(0)
        self.combo_combate.pack(fill="x")

        ttk.Button(
            control_frame,
            text="Asignar Comportamiento",
            command=self.asignar_comportamiento_preparacion,
        ).pack(fill="x", pady=(2, 2))

        # Panel con información de la carta seleccionada
        self.frame_estado_carta = ttk.LabelFrame(control_frame, text="Estado Carta")
        self.frame_estado_carta.pack(fill="x", pady=5)
        self.lbl_estado_carta = ttk.Label(
            self.frame_estado_carta, text="Selecciona una carta"
        )
        self.lbl_estado_carta.pack()

        ttk.Separator(control_frame, orient="horizontal").pack(fill="x", pady=10)
        ttk.Label(control_frame, text="Cartas en Banco:").pack()

        banco_list_frame = ttk.Frame(control_frame)
        banco_list_frame.pack(fill="both", expand=True)
        self.listbox_banco_tablero = tk.Listbox(banco_list_frame, width=25)
        scrollbar = ttk.Scrollbar(banco_list_frame, orient="vertical", command=self.listbox_banco_tablero.yview)
        self.listbox_banco_tablero.config(yscrollcommand=scrollbar.set)
        self.listbox_banco_tablero.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Label(control_frame, text="Selecciona carta → Clic en tablero").pack(pady=(5, 0))
        self.lbl_coord_actual = ttk.Label(control_frame, text="Coordenada: -")
        self.lbl_coord_actual.pack()
        self.lbl_modo_mover = ttk.Label(control_frame, text="")
        self.lbl_modo_mover.pack()

    def crear_tab_enfrentamiento(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Enfrentamiento")

        from src.interfaces.gui.widgets.hex_canvas import InterfazMapaGlobal

        self.mapa_global = None
        self.interfaz_mapa = InterfazMapaGlobal(
            frame, None, debug=self.var_mostrar_coordenadas.get()
        )
        self.interfaz_mapa.pack(side="left", fill="both", expand=True)
        self.interfaz_mapa.canvas.bind("<Button-1>", self.on_mapa_click)
        self.interfaz_mapa.canvas.bind("<Motion>", self.on_mapa_motion)

        panel = ttk.Frame(frame)
        panel.pack(side="right", fill="y", padx=5)
        ttk.Label(panel, text="Cartas del Jugador Actual:").pack(anchor="w")
        self.listbox_enfrentamiento = tk.Listbox(panel, height=15)
        self.listbox_enfrentamiento.pack(fill="both", expand=True, pady=2)
        self.listbox_enfrentamiento.bind('<<ListboxSelect>>', self.on_seleccionar_carta_enfrentamiento)
        btns = ttk.Frame(panel)
        btns.pack(fill="x", pady=2)
        ttk.Button(btns, text="Centrar en Carta", command=self.centrar_en_carta).pack(fill="x")

        # Información de la carta seleccionada en el mapa global
        self.frame_estado_carta_global = ttk.LabelFrame(panel, text="Estado Carta")
        self.frame_estado_carta_global.pack(fill="x", pady=5)
        self.lbl_estado_carta_global = ttk.Label(
            self.frame_estado_carta_global, text="Selecciona una carta"
        )
        self.lbl_estado_carta_global.pack()
        self.frame_mover_test = ttk.LabelFrame(panel, text="Mover (Test)")
        self.frame_mover_test.pack(fill="x", pady=5)
        self.frame_mover_test.pack_forget()
        ttk.Label(self.frame_mover_test, text="Q:").grid(row=0, column=0)
        self.entry_q = ttk.Entry(self.frame_mover_test, width=4)
        self.entry_q.grid(row=0, column=1)
        ttk.Label(self.frame_mover_test, text="R:").grid(row=0, column=2)
        self.entry_r = ttk.Entry(self.frame_mover_test, width=4)
        self.entry_r.grid(row=0, column=3)
        ttk.Button(self.frame_mover_test, text="Mover Aquí", command=self.mover_carta_test).grid(row=1, column=0, columnspan=4, pady=2)

        # Panel de órdenes manuales
        self.frame_ordenes = ttk.LabelFrame(panel, text="Órdenes")
        self.frame_ordenes.pack(fill="x", pady=5)
        self.lbl_orden_carta = ttk.Label(self.frame_ordenes, text="🎮 ÓRDENES PARA: -")
        self.lbl_orden_carta.pack(anchor="w")
        orden_btns = ttk.Frame(self.frame_ordenes)
        orden_btns.pack(fill="x", pady=2)
        self.btn_orden_mover = ttk.Button(
            orden_btns, text="Mover a Posición", command=self.ordenar_movimiento
        )
        self.btn_orden_mover.pack(fill="x")
        self.btn_orden_atacar = ttk.Button(
            orden_btns, text="Atacar Enemigo", command=self.ordenar_ataque
        )
        self.btn_orden_atacar.pack(fill="x")
        self.btn_orden_comportamiento = ttk.Button(
            orden_btns,
            text="Cambiar Comportamiento",
            command=self.cambiar_comportamiento_carta,
        )
        self.btn_orden_comportamiento.pack(fill="x")
        self.lbl_estado_orden = ttk.Label(self.frame_ordenes, text="Estado: -")
        self.lbl_estado_orden.pack(anchor="w")
        self.lbl_turno_req = ttk.Label(self.frame_ordenes, text="Turno requerido: -")
        self.lbl_turno_req.pack(anchor="w")

        info_frame = ttk.LabelFrame(frame, text="Estado Combate")
        info_frame.pack(fill="x")
        self.lbl_turno_actual = ttk.Label(info_frame, text="TURNO ACTIVO: -", font=("Arial", 12, "bold"))
        self.lbl_turno_actual.pack(side="top", padx=5, pady=2, anchor="w")
        self.lbl_equipo_rojo = ttk.Label(info_frame, text="🔴 EQUIPO ROJO: -")
        self.lbl_equipo_rojo.pack(side="top", padx=5, anchor="w")
        self.lbl_equipo_azul = ttk.Label(info_frame, text="🔵 EQUIPO AZUL: -")
        self.lbl_equipo_azul.pack(side="top", padx=5, anchor="w")
        self.lbl_tiempo_turno = ttk.Label(info_frame, text="Tiempo turno: -")
        self.lbl_tiempo_turno.pack(side="top", padx=5, anchor="w")
        self.lbl_coord_mapa = ttk.Label(info_frame, text="Mapa: -")
        self.lbl_coord_mapa.pack(side="top", padx=5, anchor="w")
        self.chk_mostrar_coords = ttk.Checkbutton(
            info_frame,
            text="Mostrar coordenadas",
            variable=self.var_mostrar_coordenadas,
            command=self.toggle_mostrar_coordenadas,
        )
        self.chk_mostrar_coords.pack(side="top", padx=5, anchor="w")

    # === MÉTODOS DE CONTROL ===

    def iniciar_juego(self):
        # Crear 2 jugadores
        j1 = Jugador(1, "Jugador 1")
        j2 = Jugador(2, "Jugador 2")
        self.jugadores = [j1, j2]

        # Inicializar motor
        self.motor = MotorJuego(self.jugadores, on_step_callback=self.on_evento_motor)
        self.motor.iniciar()

        # Actualizar modo de testeo según la configuración del motor
        self.modo_testeo = self.motor.modo_testeo
        if self.motor.modo_testeo:
            self.mostrar_panel_testeo()

        # Configurar combo
        self.combo_jugador['values'] = [f"{j.nombre} (ID: {j.id})" for j in self.jugadores]
        self.combo_jugador.current(0)
        self.jugador_actual = self.jugadores[0]

        self.actualizar_interfaz()
        messagebox.showinfo("Juego Iniciado", "¡Juego iniciado con 2 jugadores!")

    def cambiar_jugador(self):
        if not self.jugadores:
            return

        indice_actual = self.jugadores.index(self.jugador_actual)
        siguiente_indice = (indice_actual + 1) % len(self.jugadores)
        self.jugador_actual = self.jugadores[siguiente_indice]
        self.combo_jugador.current(siguiente_indice)
        self.actualizar_interfaz()

    def on_jugador_changed(self, event):
        if self.jugadores:
            indice = self.combo_jugador.current()
            self.jugador_actual = self.jugadores[indice]
            self.actualizar_interfaz()

    def actualizar_interfaz(self):
        if not self.jugador_actual or not self.motor:
            return

        cambio_jugador = self.jugador_actual is not self._jugador_prev
        self._jugador_prev = self.jugador_actual

        # Actualizar info general
        self.lbl_ronda.config(text=f"Ronda: {self.motor.ronda}")
        self.lbl_fase.config(text=f"Fase: {self.motor.fase_actual}")

        # Actualizar info del jugador
        info = f"""Jugador: {self.jugador_actual.nombre}
Vida: {self.jugador_actual.vida}/{self.jugador_actual.vida_maxima}
Oro: {self.jugador_actual.oro}
Nivel: {self.jugador_actual.nivel}
Experiencia: {self.jugador_actual.experiencia}
Tokens Reroll: {self.jugador_actual.tokens_reroll}"""
        self.lbl_jugador_info.config(text=info)

        costo = self.jugador_actual.calcular_costo_siguiente_nivel()
        self.lbl_costo_experiencia.config(text=f"Costo actual: {costo} exp")
        self.lbl_exp_disponible.config(
            text=f"Exp: {self.jugador_actual.experiencia}"
        )

        # Actualizar banco y tablero siempre
        self.actualizar_banco()
        if self.motor.fase_actual == "preparacion":
            self.actualizar_tienda()
            self.actualizar_subasta()
        self.actualizar_tablero()

        if hasattr(self, "interfaz_mapa"):
            if hasattr(self.motor, "mapa_global") and self.motor.mapa_global:
                if self.interfaz_mapa.mapa is not self.motor.mapa_global:
                    self.interfaz_mapa.set_mapa(self.motor.mapa_global)
                    self.mapa_global = self.motor.mapa_global

                if cambio_jugador:
                    self.interfaz_mapa.actualizar_vision_para_jugador(
                        self.jugador_actual
                    )

                if self.motor.fase_actual != "preparacion":
                    estado_actual = tuple(
                        (c.q, c.r, id(card) if card else None)
                        for c, card in sorted(
                            self.mapa_global.tablero.celdas.items(),
                            key=lambda i: (i[0].q, i[0].r),
                        )
                    )

                    if (
                        estado_actual != self._ultimo_estado_mapa
                        or self.motor.fase_actual != self._ultima_fase_mapa
                        or cambio_jugador
                    ):
                        visibles = self.interfaz_mapa.calcular_celdas_visibles(
                            self.jugador_actual
                        )
                        self.interfaz_mapa.actualizar_vision(visibles)
                        self.interfaz_mapa.actualizar()
                        self._ultimo_estado_mapa = estado_actual
                        self._ultima_fase_mapa = self.motor.fase_actual
                else:
                    self._ultima_fase_mapa = self.motor.fase_actual
            else:
                if self.interfaz_mapa.mapa is not None:
                    self.interfaz_mapa.set_mapa(None)
                self.mapa_global = None

        if hasattr(self.motor, "controlador_enfrentamiento") and self.motor.controlador_enfrentamiento:
            turno = self.motor.controlador_enfrentamiento.obtener_turno_activo()
            self.lbl_turno_actual.config(text=f"TURNO ACTIVO: {turno.upper()}" if turno else "TURNO ACTIVO: -")
            rojos = ", ".join(j.nombre for j in self.motor.controlador_enfrentamiento.turnos.jugadores_por_color.get("rojo", []))
            azules = ", ".join(j.nombre for j in self.motor.controlador_enfrentamiento.turnos.jugadores_por_color.get("azul", []))
            self.lbl_equipo_rojo.config(text=f"🔴 EQUIPO ROJO: {rojos or '-'}")
            self.lbl_equipo_azul.config(text=f"🔵 EQUIPO AZUL: {azules or '-'}")

        if self.motor.modo_testeo and self.frame_mover_test.winfo_ismapped() == 0:
            self.frame_mover_test.pack(fill="x", pady=5)
        
        # Habilitar/deshabilitar controles según fase
        if self.motor.fase_actual == "preparacion":
            for i in range(1, 4):
                self.notebook.tab(i, state="normal")
            self.canvas_tablero.bind("<Button-1>", self.on_canvas_click)
            self.notebook.tab(4, state="disabled")
            # Asegurar que la pestaña de estado siempre esté accesible
            self.notebook.tab(0, state="normal")
        else:
            for i in range(1, 4):
                self.notebook.tab(i, state="disabled")
            self.canvas_tablero.unbind("<Button-1>")
            self.notebook.tab(4, state="normal")
            # Asegurar que la pestaña de estado siempre esté accesible
            self.notebook.tab(0, state="normal")
        if not self.motor.modo_testeo and self.frame_mover_test.winfo_ismapped() == 1:
            self.frame_mover_test.pack_forget()

        self.actualizar_panel_enfrentamiento()

    def actualizar_banco(self):
        self.listbox_banco.delete(0, tk.END)
        if hasattr(self, 'listbox_banco_tablero'):
            self.listbox_banco_tablero.delete(0, tk.END)
        cartas_validas = [c for c in self.jugador_actual.cartas_banco if c is not None]
        for i, carta in enumerate(cartas_validas):
            texto = f"[{i}] {carta.nombre} (Tier {carta.tier})"
            self.listbox_banco.insert(tk.END, texto)
            if hasattr(self, 'listbox_banco_tablero'):
                self.listbox_banco_tablero.insert(tk.END, texto)

    def actualizar_tienda(self):
        self.listbox_tienda.delete(0, tk.END)

        # Obtener tienda del controlador
        if hasattr(self.motor, 'controlador_preparacion'):
            tienda = self.motor.get_tienda_para(self.jugador_actual.id)
            if tienda:
                for i, carta in enumerate(tienda.cartas_disponibles):
                    self.listbox_tienda.insert(tk.END,
                                               f"[{i}] {carta.nombre} - Tier {carta.tier} - {carta.costo} oro")

    def actualizar_subasta(self):
        # Limpiar tree
        for item in self.tree_subasta.get_children():
            self.tree_subasta.delete(item)

        # Obtener subasta del controlador
        if hasattr(self.motor, 'controlador_preparacion'):
            subasta = self.motor.get_subasta()
            if subasta:
                for carta_id, datos in subasta.cartas_subastadas.items():
                    carta = datos["carta"]
                    oferta = datos["mejor_oferta"]
                    jugador = datos["jugador"]
                    jugador_nombre = jugador.nombre if jugador else "-"

                    self.tree_subasta.insert("", tk.END, iid=carta_id,
                                             values=(carta.nombre, f"{oferta} oro", jugador_nombre))

    def actualizar_tablero(self):
        # Limpiar canvas
        self.canvas_tablero.delete("all")

        # Dibujar hexágonos del tablero
        self.dibujar_tablero_hexagonal()

        self.lbl_modo_mover.config(text="" if not self.modo_mover_carta else self.lbl_modo_mover.cget("text"))
        self.actualizar_estado_carta_tablero(None)

        # Actualizar lista
        self.listbox_tablero.delete(0, tk.END)
        cartas_tablero = [
            par
            for par in self.jugador_actual.obtener_cartas_tablero()
            if par[1] is not None and par[1].esta_viva()
        ]
        for coord, carta in cartas_tablero:
            mov = getattr(carta, "movement_behavior", "-")
            com = getattr(carta, "combat_behavior", "-")
            self.listbox_tablero.insert(
                tk.END, f"{carta.nombre} en {coord} (M:{mov} C:{com})"
            )

    def actualizar_panel_enfrentamiento(self):
        if not hasattr(self, "listbox_enfrentamiento"):
            return
        # Conservar la carta seleccionada actual si sigue siendo válida
        selected_coord = None
        if (
            self.carta_seleccionada
            and self.carta_seleccionada.esta_viva()
            and self.motor
            and self.motor.mapa_global
        ):
            selected_coord = self.motor.mapa_global.tablero.obtener_coordenada_de(
                self.carta_seleccionada
            )

        self.listbox_enfrentamiento.delete(0, tk.END)
        self._panel_coords = []

        if not (self.motor and self.motor.mapa_global and self.jugador_actual):
            self.carta_seleccionada = None
            self.actualizar_estado_carta_global(None)
            return

        index_to_select = None
        for coord, carta in self.motor.mapa_global.tablero.celdas.items():
            if (
                carta is not None
                and carta.duenio == self.jugador_actual
                and carta.esta_viva()
            ):
                self.listbox_enfrentamiento.insert(
                    tk.END, f"{carta.nombre} - Pos: ({coord.q}, {coord.r})"
                )
                self._panel_coords.append(coord)
                if selected_coord and coord == selected_coord:
                    index_to_select = len(self._panel_coords) - 1
                    self.carta_seleccionada = carta

        if index_to_select is not None:
            self.listbox_enfrentamiento.selection_set(index_to_select)
        elif not (
            self.carta_seleccionada
            and self.carta_seleccionada.esta_viva()
            and selected_coord
        ):
            self.carta_seleccionada = None

        self.actualizar_estado_carta_global(self.carta_seleccionada)
        self.actualizar_panel_ordenes()

    def dibujar_tablero_hexagonal(self):
        # Dibujar una representación simple del tablero hexagonal
        hex_size = self.hex_size

        # Dibujar hexágonos para cada coordenada
        for coord in self.jugador_actual.tablero.celdas.keys():
            # Convertir coordenadas hexagonales a pixel
            x, y = hex_to_pixel(coord, hex_size, self.board_center)

            # Dibujar hexágono
            carta = self.jugador_actual.tablero.celdas[coord]
            color = "lightblue" if carta else "white"
            self.dibujar_hexagono(x, y, hex_size, color)

            # Escribir nombre de carta si existe
            if carta:
                self.canvas_tablero.create_text(x, y, text=carta.nombre[:8], font=("Arial", 8))

    def dibujar_hexagono(self, x, y, size, color):
        import math
        points = []
        for i in range(6):
            angle = math.pi / 3 * i
            px = x + size * math.cos(angle)
            py = y + size * math.sin(angle)
            points.extend([px, py])

        self.canvas_tablero.create_polygon(points, fill=color, outline="black")

    def pixel_a_hex(self, x, y):
        return pixel_to_hex(x, y, self.hex_size, self.board_center)


    def mapa_pixel_a_hex(self, x, y):
        """Compatibilidad: delega conversión a InterfazMapaGlobal"""
        return self.interfaz_mapa.pixel_to_hex(x, y)

    def preparar_mover_carta(self, event):
        if not self.jugador_actual:
            return
        seleccion = self.listbox_tablero.curselection()
        if not seleccion:
            return
        cartas = [p for p in self.jugador_actual.obtener_cartas_tablero() if p[1] is not None]
        if seleccion[0] >= len(cartas):
            return
        self.modo_mover_carta = True
        self.coordenada_origen = cartas[seleccion[0]][0]
        carta = cartas[seleccion[0]][1]
        self.lbl_modo_mover.config(text=f"Mover {carta.nombre}: elige destino")
        self.listbox_banco_tablero.selection_clear(0, tk.END)
        self.actualizar_estado_carta_tablero(carta)

    def on_canvas_click(self, event):
        if not self.jugador_actual:
            return
        coord = self.pixel_a_hex(event.x, event.y)
        if coord not in self.jugador_actual.tablero.celdas:
            messagebox.showwarning("Advertencia", "Coordenada fuera del tablero")
            return

        if self.modo_mover_carta and self.coordenada_origen:
            if self.jugador_actual.mover_carta_en_tablero(self.coordenada_origen, coord):
                messagebox.showinfo("Éxito", f"Carta movida a {coord}")
            else:
                messagebox.showwarning("Error", "No se pudo mover la carta")
            self.modo_mover_carta = False
            self.coordenada_origen = None
            self.lbl_modo_mover.config(text="")
            self.listbox_tablero.selection_clear(0, tk.END)
            self.actualizar_estado_carta_tablero(None)
            self.actualizar_interfaz()
            return

        if not self.listbox_banco_tablero.curselection():
            messagebox.showwarning("Advertencia", "Selecciona una carta del banco")
            return

        indice = self.listbox_banco_tablero.curselection()[0]
        if self.jugador_actual.colocar_carta_en_coordenada(indice, coord):
            messagebox.showinfo("Éxito", f"Carta colocada en {coord}")
        else:
            messagebox.showwarning("Error", "No se pudo colocar en tablero")
        self.actualizar_interfaz()

    def on_canvas_motion(self, event):
        if not self.jugador_actual:
            return
        coord = self.pixel_a_hex(event.x, event.y)
        if coord in self.jugador_actual.tablero.celdas:
            self.lbl_coord_actual.config(text=f"Coordenada: {coord}")
        else:
            self.lbl_coord_actual.config(text="Coordenada: -")

    def on_mapa_motion(self, event):
        x = self.interfaz_mapa.canvas.canvasx(event.x)
        y = self.interfaz_mapa.canvas.canvasy(event.y)
        coord = self.interfaz_mapa.pixel_to_hex(x, y)
        if hasattr(self, "lbl_coord_mapa"):
            self.lbl_coord_mapa.config(text=f"Mapa: {coord}" if coord else "Mapa: -")

    def on_mapa_click(self, event):
        x = self.interfaz_mapa.canvas.canvasx(event.x)
        y = self.interfaz_mapa.canvas.canvasy(event.y)
        coord = self.interfaz_mapa.pixel_to_hex(x, y)
        if hasattr(self, "lbl_coord_mapa"):
            self.lbl_coord_mapa.config(text=f"Mapa: {coord}" if coord else "Mapa: -")
        if coord:
            self.interfaz_mapa.resaltar_coordenada(coord, duracion=1000)
        if coord is None:
            return
        if self.ui_mode == "normal" and self.motor and self.motor.mapa_global:
            carta = self.motor.mapa_global.tablero.obtener_carta_en(coord)
            if carta and carta.esta_viva():
                self.carta_seleccionada = carta
            else:
                self.carta_seleccionada = None
            self.actualizar_estado_carta_global(self.carta_seleccionada)
            self.actualizar_panel_ordenes()
            return
        if self.ui_mode != "seleccionar_destino":
            return
        if not (self.motor and self.motor.mapa_global and self.carta_seleccionada):
            return
        tablero = self.motor.mapa_global.tablero
        if not tablero.esta_dentro_del_tablero(coord):
            messagebox.showwarning("Error", "Destino inválido")
            return
        origen = tablero.obtener_coordenada_de(self.carta_seleccionada)
        self.carta_seleccionada.marcar_orden_manual("mover", coord)
        log_evento(
            f"🎮 {self.jugador_actual.nombre} ordena mover {self.carta_seleccionada.nombre} "
            f"desde {origen} hacia {coord}"
        )
        self.ui_mode = "normal"
        self.interfaz_mapa.canvas.configure(cursor="")
        self.lbl_estado_orden.config(text="Estado: orden registrada")
        self.actualizar_panel_ordenes()

    def toggle_mostrar_coordenadas(self):
        if self.interfaz_mapa:
            self.interfaz_mapa.debug = self.var_mostrar_coordenadas.get()
            self.interfaz_mapa.forzar_actualizacion()

    # === MÉTODOS DE ACCIÓN ===

    def comprar_carta(self):
        seleccion = self.listbox_tienda.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona una carta")
            return

        indice = seleccion[0]
        tienda = self.motor.get_tienda_para(self.jugador_actual.id)
        resultado = tienda.comprar_carta(indice)
        messagebox.showinfo("Compra", resultado)
        self.actualizar_interfaz()

    def reroll_tienda(self):
        tienda = self.motor.get_tienda_para(self.jugador_actual.id)
        resultado = tienda.hacer_reroll()
        messagebox.showinfo("Reroll", resultado or "Tienda actualizada")
        self.actualizar_interfaz()

    def hacer_oferta(self):
        seleccion = self.tree_subasta.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona una carta")
            return

        try:
            oferta = int(self.entry_oferta.get())
        except ValueError:
            messagebox.showerror("Error", "Ingresa un monto válido")
            return

        carta_id = seleccion[0]
        log_evento(
            f"🎯 Intentando ofertar: jugador={self.jugador_actual.nombre}, carta_id={carta_id}, monto={oferta}")
        subasta = self.motor.get_subasta()
        resultado = subasta.ofertar(self.jugador_actual, carta_id, oferta)
        messagebox.showinfo("Oferta", resultado)
        self.actualizar_interfaz()

    def comprar_experiencia(self):
        if not self.jugador_actual:
            return
        try:
            cantidad = int(self.entry_oro_experiencia.get())
        except ValueError:
            messagebox.showerror("Error", "Ingresa un número válido")
            return
        if cantidad <= 0:
            messagebox.showwarning(
                "Advertencia", "La cantidad debe ser mayor a 0"
            )
            return
        if self.jugador_actual.comprar_experiencia_con_oro(cantidad):
            messagebox.showinfo("Éxito", "Experiencia comprada")
        else:
            messagebox.showwarning("Error", "No se pudo comprar experiencia")
        self.actualizar_interfaz()

    def mover_carta_a_tablero(self):
        seleccion = self.listbox_banco.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona una carta del banco")
            return

        indice = seleccion[0]
        carta = self.jugador_actual.sacar_carta_del_banco(indice)
        if carta is None:
            messagebox.showwarning("Error", "Esa posición del banco está vacía")
        else:
            if self.jugador_actual.colocar_carta_en_tablero(carta, coordenada=None):
                messagebox.showinfo("Éxito", f"{carta.nombre} colocada en tablero")
            else:
                self.jugador_actual.agregar_carta_al_banco(carta)
                messagebox.showwarning("Error", "No se pudo colocar en tablero")
        self.actualizar_interfaz()

    def quitar_carta_tablero(self):
        seleccion = self.listbox_tablero.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona una carta del tablero")
            return

        log_evento(f"GUI: selección para quitar índice {seleccion[0]}", "DEBUG")

        cartas = [p for p in self.jugador_actual.obtener_cartas_tablero() if p[1] is not None]
        indice = seleccion[0]
        if indice >= len(cartas):
            messagebox.showwarning("Error", "Selección inválida")
            return
        coord, _ = cartas[indice]
        log_evento(f"GUI: quitando carta en {coord}", "DEBUG")
        carta = self.jugador_actual.quitar_carta_del_tablero(coord)
        log_evento(f"GUI: resultado quitar {carta}", "DEBUG")
        if carta:
            self.jugador_actual.agregar_carta_al_banco(carta)
            log_evento("GUI: carta agregada al banco", "DEBUG")
            messagebox.showinfo("Éxito", f"{carta.nombre} removida de {coord}")
        else:
            messagebox.showwarning("Error", "No se pudo quitar la carta")
        self.actualizar_interfaz()

    def asignar_comportamiento_preparacion(self):
        if not self.jugador_actual:
            return
        seleccion = self.listbox_tablero.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona una carta del tablero")
            return
        cartas = [p for p in self.jugador_actual.obtener_cartas_tablero() if p[1] is not None]
        if seleccion[0] >= len(cartas):
            messagebox.showwarning("Error", "Selección inválida")
            return
        carta = cartas[seleccion[0]][1]
        mov = self.combo_movimiento.get()
        com = self.combo_combate.get()
        carta.movement_behavior = mov
        carta.combat_behavior = com
        messagebox.showinfo(
            "Comportamiento",
            f"Movimiento: {mov}\nCombate: {com}",
        )

    def centrar_en_carta(self):
        if not self.motor or not self.motor.mapa_global:
            return
        sel = self.listbox_enfrentamiento.curselection()
        if not sel or sel[0] >= len(self._panel_coords):
            return
        coord = self._panel_coords[sel[0]]
        self.interfaz_mapa.resaltar_coordenada(coord)

    def mover_carta_test(self):
        if not (self.motor and self.motor.mapa_global):
            return
        try:
            q = int(self.entry_q.get())
            r = int(self.entry_r.get())
        except ValueError:
            messagebox.showerror("Error", "Coordenadas inválidas")
            return
        sel = self.listbox_enfrentamiento.curselection()
        if not sel or sel[0] >= len(self._panel_coords):
            return
        origen = self._panel_coords[sel[0]]
        from src.game.board.hex_coordinate import HexCoordinate
        destino = HexCoordinate(q, r)
        tablero = self.motor.mapa_global.tablero
        if tablero.mover_carta(origen, destino):
            self.actualizar_interfaz()
        else:
            messagebox.showwarning("Error", "No se pudo mover la carta")

    def on_seleccionar_carta_enfrentamiento(self, event):
        if not (self.motor and self.motor.mapa_global):
            return
        sel = self.listbox_enfrentamiento.curselection()
        if not sel or sel[0] >= len(self._panel_coords):
            self.carta_seleccionada = None
        else:
            coord = self._panel_coords[sel[0]]
            carta = self.motor.mapa_global.tablero.obtener_carta_en(coord)
            if carta and carta.esta_viva():
                self.carta_seleccionada = carta
            else:
                self.carta_seleccionada = None
        self.actualizar_estado_carta_global(self.carta_seleccionada)
        self.actualizar_panel_ordenes()

    def ordenar_ataque(self):
        if not self.carta_seleccionada or not self.carta_seleccionada.esta_viva():
            return
        if self.motor.fase_actual != "combate":
            messagebox.showwarning("Advertencia", "No estás en fase de combate")
            return
        turno = None
        if hasattr(self.motor, "controlador_enfrentamiento") and self.motor.controlador_enfrentamiento:
            turno = self.motor.controlador_enfrentamiento.obtener_turno_activo()
        color = getattr(self.carta_seleccionada.duenio, "color_fase_actual", None)
        if turno != color:
            messagebox.showwarning("Advertencia", "NO ES SU TURNO")
            return
        visibles = self.interfaz_mapa.calcular_celdas_visibles(self.jugador_actual)
        rango = self.carta_seleccionada.rango_ataque_actual
        enemigos = []
        for coord, carta in self.motor.mapa_global.tablero.celdas.items():
            if (
                carta is not None
                and not self.carta_seleccionada.es_aliado_de(carta)
                and coord in visibles
                and self.carta_seleccionada.coordenada
                and self.carta_seleccionada.coordenada.distancia(coord) <= rango
            ):
                enemigos.append((coord, carta))
        if not enemigos:
            messagebox.showinfo("Atacar", "No hay objetivos visibles")
            return
        carta_ref = self.carta_seleccionada

        top = tk.Toplevel(self.root)
        top.title("Seleccionar Objetivo")
        top.transient(self.root)
        top.grab_set()
        ttk.Label(top, text="Objetivo:").pack(padx=5, pady=5)
        opciones = [f"{carta.nombre} ({coord.q},{coord.r})" for coord, carta in enemigos]
        combo = ttk.Combobox(top, values=opciones, state="readonly")
        combo.pack(padx=5, pady=5)
        combo.current(0)

        def confirmar():
            idx = combo.current()
            coord, objetivo = enemigos[idx]
            if carta_ref and carta_ref.esta_viva():
                carta_ref.marcar_orden_manual("atacar", objetivo)
            log_evento(
                f"🎮 {self.jugador_actual.nombre} ordena atacar a {objetivo.nombre}"
            )
            self.actualizar_panel_ordenes()
            top.destroy()

        ttk.Button(top, text="OK", command=confirmar).pack(pady=5)
        self.root.wait_window(top)

    def ordenar_movimiento(self):
        if not self.carta_seleccionada or not self.carta_seleccionada.esta_viva():
            return
        turno = None
        if hasattr(self.motor, "controlador_enfrentamiento") and self.motor.controlador_enfrentamiento:
            turno = self.motor.controlador_enfrentamiento.obtener_turno_activo()
        color = getattr(self.carta_seleccionada.duenio, "color_fase_actual", None)
        if turno != color:
            messagebox.showwarning("Advertencia", "NO ES SU TURNO")
            return
        self.ui_mode = "seleccionar_destino"
        self.interfaz_mapa.canvas.configure(cursor="crosshair")
        self.lbl_estado_orden.config(text="Selecciona destino en el mapa")
        log_evento(f"🎮 {self.jugador_actual.nombre} ordena mover a {self.carta_seleccionada.nombre}")

    def cambiar_comportamiento_carta(self):
        if not self.carta_seleccionada or not self.carta_seleccionada.esta_viva():
            return
        turno = None
        if hasattr(self.motor, "controlador_enfrentamiento") and self.motor.controlador_enfrentamiento:
            turno = self.motor.controlador_enfrentamiento.obtener_turno_activo()
        color = getattr(self.carta_seleccionada.duenio, "color_fase_actual", None)
        if turno != color:
            messagebox.showwarning("Advertencia", "NO ES SU TURNO")
            return
        from src.game.comportamientos.legacy.movement_behaviors import MovementBehavior
        from src.game.comportamientos.legacy.combat_behaviors import CombatBehavior

        restricciones = getattr(self.carta_seleccionada, "behavior_restrictions", None)
        mov_opciones = (
            [b.value for b in restricciones.movement]
            if restricciones and restricciones.movement
            else [b.value for b in MovementBehavior]
        )
        com_opciones = (
            [b.value for b in restricciones.combat]
            if restricciones and restricciones.combat
            else [b.value for b in CombatBehavior]
        )

        carta_ref = self.carta_seleccionada

        top = tk.Toplevel(self.root)
        top.title("Cambiar Comportamiento")
        top.transient(self.root)
        top.grab_set()

        ttk.Label(top, text="Movimiento:").pack(padx=5, pady=(5, 0))
        combo_mov = ttk.Combobox(top, values=mov_opciones, state="readonly")
        combo_mov.pack(padx=5, pady=5)
        if self.carta_seleccionada.movement_behavior in mov_opciones:
            combo_mov.current(mov_opciones.index(self.carta_seleccionada.movement_behavior))
        else:
            combo_mov.current(0)

        ttk.Label(top, text="Combate:").pack(padx=5, pady=(5, 0))
        combo_com = ttk.Combobox(top, values=com_opciones, state="readonly")
        combo_com.pack(padx=5, pady=5)
        if self.carta_seleccionada.combat_behavior in com_opciones:
            combo_com.current(com_opciones.index(self.carta_seleccionada.combat_behavior))
        else:
            combo_com.current(0)

        def confirmar():
            nuevo_mov = combo_mov.get()
            nuevo_com = combo_com.get()
            if carta_ref and carta_ref.esta_viva():
                carta_ref.marcar_orden_manual(
                    "cambiar_comportamiento",
                    datos_adicionales={"nuevo_movimiento": nuevo_mov, "nuevo_combate": nuevo_com},
                )
            self.actualizar_panel_ordenes()
            top.destroy()

        ttk.Button(top, text="OK", command=confirmar).pack(pady=5)
        self.root.wait_window(top)

    def actualizar_estado_carta_tablero(self, carta=None):
        if not hasattr(self, "lbl_estado_carta"):
            return
        if carta:
            info = (
                f"{carta.nombre}\n"
                f"Vida: {carta.vida_actual}/{carta.vida_maxima}\n"
                f"Daño: {carta.dano_fisico_actual}\n"
                f"Defensa: {carta.defensa_fisica_actual}\n"
                f"Mov: {getattr(carta, 'movement_behavior', '-') }\n"
                f"Comb: {getattr(carta, 'combat_behavior', '-') }"
            )
            self.lbl_estado_carta.config(text=info)
        else:
            self.lbl_estado_carta.config(text="Selecciona una carta")

    def actualizar_estado_carta_global(self, carta=None):
        if not hasattr(self, "lbl_estado_carta_global"):
            return
        if carta:
            info = (
                f"{carta.nombre}\n"
                f"Vida: {carta.vida_actual}/{carta.vida_maxima}"
            )
            if carta.duenio == self.jugador_actual:
                info += (
                    f"\nMov: {getattr(carta, 'movement_behavior', '-')}"
                    f"\nComb: {getattr(carta, 'combat_behavior', '-')}"
                )
            else:
                info += "\nComportamiento: desconocido"
            self.lbl_estado_carta_global.config(text=info)
        else:
            self.lbl_estado_carta_global.config(text="Selecciona una carta")

    def actualizar_panel_ordenes(self):
        if not hasattr(self, "lbl_orden_carta"):
            return
        if (
            not self.carta_seleccionada
            or not self.carta_seleccionada.esta_viva()
            or self.carta_seleccionada.duenio != self.jugador_actual
        ):
            self.lbl_orden_carta.config(text="🎮 ÓRDENES PARA: -")
            self.lbl_estado_orden.config(text="Estado: -")
            self.lbl_turno_req.config(text="Turno requerido: -")
            for btn in (
                getattr(self, "btn_orden_mover", None),
                getattr(self, "btn_orden_atacar", None),
                getattr(self, "btn_orden_comportamiento", None),
            ):
                if btn:
                    btn.state(["disabled"])
            return

        self.lbl_orden_carta.config(text=f"🎮 ÓRDENES PARA: {self.carta_seleccionada.nombre}")
        orden = self.carta_seleccionada.orden_actual
        estado = orden.get("progreso") if orden else "-"
        self.lbl_estado_orden.config(text=f"Estado: {estado}")
        turno = None
        if hasattr(self.motor, "controlador_enfrentamiento") and self.motor.controlador_enfrentamiento:
            turno = self.motor.controlador_enfrentamiento.obtener_turno_activo()
        rojo = "✅" if turno == "rojo" else "❌"
        azul = "✅" if turno == "azul" else "❌"
        self.lbl_turno_req.config(text=f"Turno requerido: ROJO {rojo} / AZUL {azul}")
        for btn in (
            getattr(self, "btn_orden_mover", None),
            getattr(self, "btn_orden_atacar", None),
            getattr(self, "btn_orden_comportamiento", None),
        ):
            if btn:
                btn.state(["!disabled"])

    def usar_habilidad(self):
        messagebox.showinfo("Info", "Uso de habilidades en desarrollo")

    def mostrar_panel_testeo(self):
        if not self.panel_testeo:
            return
        self.panel_testeo.motor = self.motor
        if not self.panel_testeo.winfo_ismapped():
            self.panel_testeo.pack(side="right", fill="y", padx=(10, 0))
        self.panel_testeo.detener()
        self.panel_testeo.actualizar_informacion()

    def ocultar_panel_testeo(self):
        if self.panel_testeo and self.panel_testeo.winfo_ismapped():
            self.panel_testeo.detener()
            self.panel_testeo.pack_forget()

    def verificar_ventana_testeo(self):
        if self.motor and self.motor.modo_testeo:
            self.mostrar_panel_testeo()
        else:
            self.ocultar_panel_testeo()

    def cerrar_aplicacion(self):
        self.ocultar_panel_testeo()
        self.root.destroy()


    def refrescar_temporizadores(self):
        self.actualizar_temporizador_fase()
        self.actualizar_temporizador_turno()
        self.verificar_ventana_testeo()
        self.root.after(500, self.refrescar_temporizadores)

    def actualizar_temporizador_fase(self):
        if not self.motor:
            self.lbl_tiempo_fase.config(text="Tiempo restante: -")
            return
        if self.motor.fase_actual == "preparacion" and hasattr(self.motor, 'controlador_preparacion'):
            segundos = self.motor.controlador_preparacion.obtener_tiempo_restante()
            self.lbl_tiempo_fase.config(text=f"Tiempo restante: {int(segundos)}s")
        else:
            self.lbl_tiempo_fase.config(text="Tiempo restante: -")

    def actualizar_temporizador_turno(self):
        if not self.motor or self.motor.fase_actual != "combate" or not hasattr(self.motor, 'controlador_enfrentamiento'):
            self.lbl_tiempo_turno.config(text="Tiempo turno: -")
            return
        segundos = self.motor.controlador_enfrentamiento.obtener_tiempo_restante_turno()
        self.lbl_tiempo_turno.config(text=f"Tiempo turno: {int(segundos)}s")

    def on_evento_motor(self, evento="actualizacion_mapa"):
        def _actualizar():
            if evento in ("transicion_fase", "actualizacion_mapa"):
                self.actualizar_interfaz()
            if evento == "actualizacion_mapa" and self.interfaz_mapa and self.jugador_actual:
                self.interfaz_mapa.actualizar_vision_para_jugador(self.jugador_actual)
                self.interfaz_mapa.forzar_actualizacion()

        self.root.after(0, _actualizar)

    def ejecutar(self):
        self.root.mainloop()


# Punto de entrada
if __name__ == "__main__":
    import math  # Para dibujar hexágonos

    app = AutoBattlerGUI()
    app.ejecutar()
