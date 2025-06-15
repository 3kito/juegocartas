# interfaces/main_gui.py
import tkinter as tk
from tkinter import ttk, messagebox

from src.core.jugador import Jugador
from src.core.motor_juego import MotorJuego


class AutoBattlerGUI:
    def __init__(self):
        self.motor = None
        self.jugador_actual = None
        self.jugadores = []

        # Ventana principal
        self.root = tk.Tk()
        self.root.title("Auto-Battler Test Interface")
        self.root.geometry("1200x800")

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
        self.crear_tab_combate()

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

        # Botones para mover cartas
        btn_frame = ttk.Frame(banco_frame)
        btn_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(btn_frame, text="Mover al Tablero",
                   command=self.mover_carta_a_tablero).pack(side="left")

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

        # Panel lateral con controles
        control_frame = ttk.Frame(frame)
        control_frame.pack(side="right", fill="y", padx=10, pady=10)

        ttk.Label(control_frame, text="Cartas en Tablero:").pack()
        self.listbox_tablero = tk.Listbox(control_frame, width=25)
        self.listbox_tablero.pack(fill="both", expand=True, pady=(5, 10))

        ttk.Button(control_frame, text="Quitar del Tablero",
                   command=self.quitar_carta_tablero).pack(fill="x")

    def crear_tab_combate(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Combate")

        # Info de turno
        turno_frame = ttk.LabelFrame(frame, text="Estado del Combate")
        turno_frame.pack(fill="x", padx=10, pady=5)

        self.lbl_turno_actual = ttk.Label(turno_frame, text="Turno: -", font=("Arial", 14))
        self.lbl_turno_actual.pack(pady=10)

        # Lista de cartas en combate
        cartas_frame = ttk.LabelFrame(frame, text="Tus Cartas en Combate")
        cartas_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree_combate = ttk.Treeview(cartas_frame, columns=("nombre", "vida", "coordenada", "estado"))
        self.tree_combate.heading("#0", text="ID")
        self.tree_combate.heading("nombre", text="Nombre")
        self.tree_combate.heading("vida", text="Vida")
        self.tree_combate.heading("coordenada", text="Posición")
        self.tree_combate.heading("estado", text="Estado")
        self.tree_combate.pack(fill="both", expand=True, padx=5, pady=5)

        # Botones de órdenes
        ordenes_frame = ttk.Frame(cartas_frame)
        ordenes_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(ordenes_frame, text="Atacar", command=self.ordenar_ataque).pack(side="left")
        ttk.Button(ordenes_frame, text="Mover", command=self.ordenar_movimiento).pack(side="left", padx=(5, 0))
        ttk.Button(ordenes_frame, text="Usar Habilidad", command=self.usar_habilidad).pack(side="left", padx=(5, 0))

    # === MÉTODOS DE CONTROL ===

    def iniciar_juego(self):
        # Crear 2 jugadores
        j1 = Jugador(1, "Jugador 1")
        j2 = Jugador(2, "Jugador 2")
        self.jugadores = [j1, j2]

        # Inicializar motor
        self.motor = MotorJuego(self.jugadores)
        self.motor.iniciar()

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

        # Actualizar banco
        self.actualizar_banco()
        self.actualizar_tienda()
        self.actualizar_subasta()
        self.actualizar_tablero()

    def actualizar_banco(self):
        self.listbox_banco.delete(0, tk.END)
        for i, carta in enumerate(self.jugador_actual.cartas_banco):
            self.listbox_banco.insert(tk.END, f"[{i}] {carta.nombre} (Tier {carta.tier})")

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

        # Actualizar lista
        self.listbox_tablero.delete(0, tk.END)
        cartas_tablero = self.jugador_actual.obtener_cartas_tablero()
        for coord, carta in cartas_tablero:
            self.listbox_tablero.insert(tk.END, f"{carta.nombre} en {coord}")

    def dibujar_tablero_hexagonal(self):
        # Dibujar una representación simple del tablero hexagonal
        center_x, center_y = 300, 250
        hex_size = 30

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

        carta_id = int(seleccion[0])
        subasta = self.motor.get_subasta()
        resultado = subasta.ofertar(self.jugador_actual, carta_id, oferta)
        messagebox.showinfo("Oferta", resultado)
        self.actualizar_interfaz()

    def mover_carta_a_tablero(self):
        seleccion = self.listbox_banco.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona una carta del banco")
            return

        indice = seleccion[0]
        carta = self.jugador_actual.sacar_carta_del_banco(indice)
        if carta:
            if self.jugador_actual.colocar_carta_en_tablero(carta):
                messagebox.showinfo("Éxito", f"{carta.nombre} colocada en tablero")
            else:
                self.jugador_actual.agregar_carta_al_banco(carta)  # Devolver si no se pudo
                messagebox.showwarning("Error", "No se pudo colocar en tablero")
        self.actualizar_interfaz()

    def quitar_carta_tablero(self):
        seleccion = self.listbox_tablero.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona una carta del tablero")
            return

        # Implementar lógica para quitar carta
        messagebox.showinfo("Info", "Función en desarrollo")

    def ordenar_ataque(self):
        if self.motor.fase_actual != "combate":
            messagebox.showwarning("Advertencia", "No estás en fase de combate")
            return
        messagebox.showinfo("Info", "Órdenes de combate en desarrollo")

    def ordenar_movimiento(self):
        messagebox.showinfo("Info", "Órdenes de movimiento en desarrollo")

    def usar_habilidad(self):
        messagebox.showinfo("Info", "Uso de habilidades en desarrollo")

    def ejecutar(self):
        self.root.mainloop()


# Punto de entrada
if __name__ == "__main__":
    import math  # Para dibujar hexágonos

    app = AutoBattlerGUI()
    app.ejecutar()
