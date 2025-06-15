# interfaces/main_gui.py
import tkinter as tk
from tkinter import ttk, messagebox

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

        self.mapa_global = MapaGlobal()
        self.interfaz_mapa = InterfazMapaGlobal(frame, self.mapa_global)
        self.interfaz_mapa.pack(fill="both", expand=True)

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

        # Actualizar banco
        self.actualizar_banco()
        self.actualizar_tienda()
        self.actualizar_subasta()
        self.actualizar_tablero()
        if hasattr(self, "interfaz_mapa"):
            self.interfaz_mapa.actualizar()

        if hasattr(self.motor, "controlador_enfrentamiento") and self.motor.controlador_enfrentamiento:
            turno = self.motor.controlador_enfrentamiento.obtener_turno_activo()
            self.lbl_turno_actual.config(text=f"TURNO ACTIVO: {turno.upper()}" if turno else "TURNO ACTIVO: -")
            rojos = ", ".join(j.nombre for j in self.motor.controlador_enfrentamiento.turnos.jugadores_por_color.get("rojo", []))
            azules = ", ".join(j.nombre for j in self.motor.controlador_enfrentamiento.turnos.jugadores_por_color.get("azul", []))
            self.lbl_equipo_rojo.config(text=f"🔴 EQUIPO ROJO: {rojos or '-'}")
            self.lbl_equipo_azul.config(text=f"🔵 EQUIPO AZUL: {azules or '-'}")

        if self.motor.modo_testeo:
            self.actualizar_controles_testeo()

        # Habilitar/deshabilitar controles según fase
        if self.motor.fase_actual == "preparacion":
            for i in range(1, 4):
                self.notebook.tab(i, state="normal")
            self.canvas_tablero.bind("<Button-1>", self.on_canvas_click)
        else:
            for i in range(1, 4):
                self.notebook.tab(i, state="disabled")
            self.canvas_tablero.unbind("<Button-1>")

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
            self.listbox_tablero.insert(tk.END, f"{carta.nombre} en {coord}")

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

    def ordenar_ataque(self):
        if self.motor.fase_actual != "combate":
            messagebox.showwarning("Advertencia", "No estás en fase de combate")
            return
        messagebox.showinfo("Info", "Órdenes de combate en desarrollo")

    def ordenar_movimiento(self):
        messagebox.showinfo("Info", "Órdenes de movimiento en desarrollo")

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
