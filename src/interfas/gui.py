# interfaces/main_gui.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from src.utils.helpers import log_evento

from src.core.jugador import Jugador
from src.core.motor_juego import MotorJuego
from src.game.combate.mapa.mapa_global import MapaGlobal


class AutoBattlerGUI:
    def __init__(self):
        self.motor = None
        self.jugador_actual = None
        self.jugadores = []

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
        self._panel_coords = []
        self.carta_seleccionada = None
        self.ui_mode = "normal"  # normal, seleccionar_destino

        self.crear_interfaz_principal()

    def crear_interfaz_principal(self):
        # Frame superior - Info del juego
        info_frame = ttk.Frame(self.root)
        info_frame.pack(fill="x", padx=10, pady=5)

        self.lbl_ronda = ttk.Label(info_frame, text="Ronda: -", font=("Arial", 12))
        self.lbl_ronda.pack(side="left")

        self.lbl_fase = ttk.Label(info_frame, text="Fase: -", font=("Arial", 12))
        self.lbl_fase.pack(side="left", padx=(20, 0))

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

        # Notebook para las diferentes vistas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tabs
        self.crear_tab_estado()
        self.crear_tab_tienda()
        self.crear_tab_subasta()
        self.crear_tab_tablero()
        self.crear_tab_enfrentamiento()

        # Controles de Testeo (ocultos por defecto)
        self.frame_testeo = ttk.LabelFrame(self.root, text="Controles de Testeo")
        self.lbl_proximo_paso = ttk.Label(self.frame_testeo, text="Próximo Paso: -")
        self.lbl_proximo_paso.pack(side="left", padx=5)
        ttk.Button(self.frame_testeo, text="Ejecutar Siguiente Paso", command=self.ejecutar_paso_testeo).pack(side="left", padx=5)
        self.lbl_estado_actual = ttk.Label(self.frame_testeo, text="Estado: -")
        self.lbl_estado_actual.pack(side="left", padx=5)
        self.lbl_turno_activo = ttk.Label(self.frame_testeo, text="Turno: -")
        self.lbl_turno_activo.pack(side="left", padx=5)
        self.btn_oro_infinito = ttk.Button(
            self.frame_testeo,
            text="Oro Infinito",
            command=self.asignar_oro_infinito,
        )
        self.btn_oro_infinito.pack(side="left", padx=5)
        self.btn_tokens_infinitos = ttk.Button(
            self.frame_testeo,
            text="Tokens Infinitos",
            command=self.asignar_tokens_infinitos,
        )
        self.btn_tokens_infinitos.pack(side="left", padx=5)

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

        ttk.Label(control_frame, text="Comportamiento:").pack(pady=(5, 0))
        self.combo_comportamiento = ttk.Combobox(
            control_frame,
            state="readonly",
            values=["agresivo", "defensivo", "explorador", "guardian", "seguidor"],
        )
        self.combo_comportamiento.current(0)
        self.combo_comportamiento.pack(fill="x")
        ttk.Button(
            control_frame,
            text="Asignar Comportamiento",
            command=self.asignar_comportamiento_preparacion,
        ).pack(fill="x", pady=(2, 2))

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

        from src.interfas.interfaz_mapa_global import InterfazMapaGlobal

        self.mapa_global = None
        self.interfaz_mapa = InterfazMapaGlobal(frame, None)
        self.interfaz_mapa.pack(side="left", fill="both", expand=True)
        self.interfaz_mapa.canvas.bind("<Button-1>", self.on_mapa_click)

        panel = ttk.Frame(frame)
        panel.pack(side="right", fill="y", padx=5)
        ttk.Label(panel, text="Cartas del Jugador Actual:").pack(anchor="w")
        self.listbox_enfrentamiento = tk.Listbox(panel, height=15)
        self.listbox_enfrentamiento.pack(fill="both", expand=True, pady=2)
        self.listbox_enfrentamiento.bind('<<ListboxSelect>>', self.on_seleccionar_carta_enfrentamiento)
        btns = ttk.Frame(panel)
        btns.pack(fill="x", pady=2)
        ttk.Button(btns, text="Centrar en Carta", command=self.centrar_en_carta).pack(fill="x")
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
        ttk.Button(orden_btns, text="Mover a Posición", command=self.ordenar_movimiento).pack(fill="x")
        ttk.Button(orden_btns, text="Atacar Enemigo", command=self.ordenar_ataque).pack(fill="x")
        ttk.Button(orden_btns, text="Cambiar Comportamiento", command=self.cambiar_comportamiento_carta).pack(fill="x")
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

    # === MÉTODOS DE CONTROL ===

    def iniciar_juego(self):
        # Crear 2 jugadores
        j1 = Jugador(1, "Jugador 1")
        j2 = Jugador(2, "Jugador 2")
        self.jugadores = [j1, j2]

        # Inicializar motor
        self.motor = MotorJuego(self.jugadores)
        self.motor.iniciar()

        if self.motor.modo_testeo:
            self.frame_testeo.pack(fill="x", padx=10, pady=5)
            self.actualizar_controles_testeo()

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
                    ):
                        visibles = self.interfaz_mapa.calcular_celdas_visibles(self.jugador_actual)
                        self.interfaz_mapa.actualizar_vision(visibles)
                        self.interfaz_mapa.actualizar()
                        self._ultimo_estado_mapa = estado_actual
                        self._ultima_fase_mapa = self.motor.fase_actual
                else:
                    self._ultima_fase_mapa = self.motor.fase_actual

        if hasattr(self.motor, "controlador_enfrentamiento") and self.motor.controlador_enfrentamiento:
            turno = self.motor.controlador_enfrentamiento.obtener_turno_activo()
            self.lbl_turno_actual.config(text=f"TURNO ACTIVO: {turno.upper()}" if turno else "TURNO ACTIVO: -")
            rojos = ", ".join(j.nombre for j in self.motor.controlador_enfrentamiento.turnos.jugadores_por_color.get("rojo", []))
            azules = ", ".join(j.nombre for j in self.motor.controlador_enfrentamiento.turnos.jugadores_por_color.get("azul", []))
            self.lbl_equipo_rojo.config(text=f"🔴 EQUIPO ROJO: {rojos or '-'}")
            self.lbl_equipo_azul.config(text=f"🔵 EQUIPO AZUL: {azules or '-'}")

        if self.motor.modo_testeo:
            self.actualizar_controles_testeo()
            if self.frame_mover_test.winfo_ismapped() == 0:
                self.frame_mover_test.pack(fill="x", pady=5)
        
        # Habilitar/deshabilitar controles según fase
        if self.motor.fase_actual == "preparacion":
            for i in range(1, 4):
                self.notebook.tab(i, state="normal")
            self.canvas_tablero.bind("<Button-1>", self.on_canvas_click)
        else:
            for i in range(1, 4):
                self.notebook.tab(i, state="disabled")
            self.canvas_tablero.unbind("<Button-1>")
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

        # Actualizar lista
        self.listbox_tablero.delete(0, tk.END)
        cartas_tablero = [par for par in self.jugador_actual.obtener_cartas_tablero() if par[1] is not None]
        for coord, carta in cartas_tablero:
            comp = carta.comportamiento_asignado or "-"
            self.listbox_tablero.insert(tk.END, f"{carta.nombre} en {coord} ({comp})")

    def actualizar_panel_enfrentamiento(self):
        if not hasattr(self, "listbox_enfrentamiento"):
            return
        self.listbox_enfrentamiento.delete(0, tk.END)
        self._panel_coords = []
        if not (self.motor and self.motor.mapa_global and self.jugador_actual):
            return
        for coord, carta in self.motor.mapa_global.tablero.celdas.items():
            if carta is not None and carta.duenio == self.jugador_actual:
                self.listbox_enfrentamiento.insert(
                    tk.END, f"{carta.nombre} - Pos: ({coord.q}, {coord.r})"
                )
                self._panel_coords.append(coord)

        self.actualizar_panel_ordenes()

    def dibujar_tablero_hexagonal(self):
        # Dibujar una representación simple del tablero hexagonal
        center_x, center_y = self.board_center
        hex_size = self.hex_size

        # Dibujar hexágonos para cada coordenada
        for coord in self.jugador_actual.tablero.celdas.keys():
            # Convertir coordenadas hexagonales a pixel
            x = center_x + hex_size * (3 / 2 * coord.q)
            y = center_y + hex_size * (math.sqrt(3) / 2 * coord.q + math.sqrt(3) * coord.r)

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
        import math
        cx, cy = self.board_center
        size = self.hex_size
        x = x - cx
        y = y - cy
        q = (2/3 * x) / size
        r = (-1/3 * x + math.sqrt(3)/3 * y) / size
        return self.hex_round(q, r)

    def hex_round(self, q, r):
        x = q
        z = r
        y = -x - z
        rx = round(x)
        ry = round(y)
        rz = round(z)
        x_diff = abs(rx - x)
        y_diff = abs(ry - y)
        z_diff = abs(rz - z)
        if x_diff > y_diff and x_diff > z_diff:
            rx = -ry - rz
        elif y_diff > z_diff:
            ry = -rx - rz
        else:
            rz = -rx - ry
        from src.game.tablero.coordenada import CoordenadaHexagonal
        return CoordenadaHexagonal(int(rx), int(rz))

    def mapa_pixel_a_hex(self, x, y):
        import math
        size = self.interfaz_mapa.hex_size
        x = x - 200
        y = y - 200
        q = (2/3 * x) / size
        r = (-1/3 * x + math.sqrt(3)/3 * y) / size
        return self.hex_round(q, r)

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

    def on_mapa_click(self, event):
        if self.ui_mode != "seleccionar_destino":
            return
        if not (self.motor and self.motor.mapa_global and self.carta_seleccionada):
            return
        coord = self.mapa_pixel_a_hex(event.x, event.y)
        tablero = self.motor.mapa_global.tablero
        if not tablero.esta_dentro_del_tablero(coord) or not tablero.esta_vacia(coord):
            messagebox.showwarning("Error", "Destino inválido")
            return
        self.carta_seleccionada.marcar_orden_manual("mover", coord)
        log_evento(f"🎮 {self.jugador_actual.nombre} ordena mover a {self.carta_seleccionada.nombre}")
        self.ui_mode = "normal"
        self.interfaz_mapa.canvas.configure(cursor="")
        self.lbl_estado_orden.config(text="Estado: orden registrada")
        self.actualizar_panel_ordenes()

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
        comportamiento = self.combo_comportamiento.get()
        resultado = carta.asignar_comportamiento(comportamiento)
        messagebox.showinfo("Comportamiento", resultado)

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
        from src.game.tablero.coordenada import CoordenadaHexagonal
        destino = CoordenadaHexagonal(q, r)
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
            self.carta_seleccionada = self.motor.mapa_global.tablero.obtener_carta_en(coord)
        self.actualizar_panel_ordenes()

    def ordenar_ataque(self):
        if not self.carta_seleccionada:
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
        enemigos = []
        for coord, carta in self.motor.mapa_global.tablero.celdas.items():
            if (
                carta is not None
                and not self.carta_seleccionada.es_aliado_de(carta)
                and coord in visibles
            ):
                enemigos.append((coord, carta))
        if not enemigos:
            messagebox.showinfo("Atacar", "No hay objetivos visibles")
            return
        top = tk.Toplevel(self.root)
        top.title("Seleccionar Objetivo")
        ttk.Label(top, text="Objetivo:").pack(padx=5, pady=5)
        opciones = [f"{carta.nombre} ({coord.q},{coord.r})" for coord, carta in enemigos]
        combo = ttk.Combobox(top, values=opciones, state="readonly")
        combo.pack(padx=5, pady=5)
        combo.current(0)

        def confirmar():
            idx = combo.current()
            coord, objetivo = enemigos[idx]
            self.carta_seleccionada.marcar_orden_manual("atacar", objetivo)
            log_evento(
                f"🎮 {self.jugador_actual.nombre} ordena atacar a {objetivo.nombre}"
            )
            self.actualizar_panel_ordenes()
            top.destroy()

        ttk.Button(top, text="OK", command=confirmar).pack(pady=5)

    def ordenar_movimiento(self):
        if not self.carta_seleccionada:
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
        if not self.carta_seleccionada:
            return
        turno = None
        if hasattr(self.motor, "controlador_enfrentamiento") and self.motor.controlador_enfrentamiento:
            turno = self.motor.controlador_enfrentamiento.obtener_turno_activo()
        color = getattr(self.carta_seleccionada.duenio, "color_fase_actual", None)
        if turno != color:
            messagebox.showwarning("Advertencia", "NO ES SU TURNO")
            return
        nuevo = simpledialog.askstring("Comportamiento", "Nuevo comportamiento:", initialvalue="agresivo")
        if not nuevo:
            return
        self.carta_seleccionada.marcar_orden_manual("cambiar_comportamiento", datos_adicionales={"nuevo_comportamiento": nuevo})
        self.actualizar_panel_ordenes()

    def actualizar_panel_ordenes(self):
        if not hasattr(self, "lbl_orden_carta"):
            return
        if not self.carta_seleccionada:
            self.lbl_orden_carta.config(text="🎮 ÓRDENES PARA: -")
            self.lbl_estado_orden.config(text="Estado: -")
            self.lbl_turno_req.config(text="Turno requerido: -")
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

    def usar_habilidad(self):
        messagebox.showinfo("Info", "Uso de habilidades en desarrollo")

    def asignar_oro_infinito(self):
        if self.jugador_actual:
            self.jugador_actual.oro = 999999
            self.actualizar_interfaz()

    def asignar_tokens_infinitos(self):
        if self.jugador_actual:
            self.jugador_actual.tokens_reroll = 999
            self.actualizar_interfaz()

    # === CONTROLES DE TESTEO ===
    def ejecutar_paso_testeo(self):
        if self.motor:
            self.motor.ejecutar_siguiente_paso()
            self.actualizar_interfaz()
            self.actualizar_controles_testeo()

    def actualizar_controles_testeo(self):
        if not self.motor:
            return
        self.lbl_proximo_paso.config(text=f"Próximo Paso: {self.motor.describir_proximo_paso()}")
        estado = f"{self.motor.fase_actual}"
        self.lbl_estado_actual.config(text=f"Estado: {estado}")
        turno = "-"
        if hasattr(self.motor, 'controlador_enfrentamiento') and self.motor.controlador_enfrentamiento:
            turno = self.motor.controlador_enfrentamiento.obtener_turno_activo()
        self.lbl_turno_activo.config(text=f"Turno: {turno if turno else '-'}")

    def ejecutar(self):
        self.root.mainloop()


# Punto de entrada
if __name__ == "__main__":
    import math  # Para dibujar hexágonos

    app = AutoBattlerGUI()
    app.ejecutar()
