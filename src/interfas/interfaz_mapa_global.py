import tkinter as tk
from tkinter import ttk
from src.game.combate.mapa.mapa_global import MapaGlobal
from src.utils.helpers import log_evento


class InterfazMapaGlobal(ttk.Frame):
    """Widget para visualizar el mapa global con soporte de *fog of war*.

    Para celdas fuera de ``self.celdas_visibles`` se dibuja un overlay oscuro.
    Esta lista puede actualizarse mediante :meth:`actualizar_vision`.

    Ideas para mejorar la performance del "fog of war"::

        1. Dibujar el overlay en un canvas separado y mantenerlo cacheado,
           actualizando solo las celdas cuya visibilidad cambió.
        2. Generar imágenes pre-renderizadas por patrón de visibilidad y
           reutilizarlas cuando se mueva la cámara.
        3. Mantener un mapa de bits con la visibilidad y sólo redibujar las
           regiones modificadas utilizando ``Canvas.coords``.
    """

    def __init__(self, master, mapa: MapaGlobal | None = None, hex_size: int = 20):
        super().__init__(master)
        self.mapa = mapa
        self._ultimo_estado = None
        self.hex_size = hex_size
        self.celdas_visibles = set()  # coordenadas visibles para el jugador

        self.canvas = tk.Canvas(self, width=600, height=400, bg="white")
        h_scroll = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        v_scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        if self.mapa:
            self._dibujar_mapa()

    def set_mapa(self, mapa: MapaGlobal):
        """Asigna un nuevo mapa y lo dibuja"""
        self.mapa = mapa
        self._ultimo_estado = None
        self.actualizar()

    def actualizar_vision(self, celdas_visibles: set):
        """Actualiza las celdas visibles y redibuja si es necesario"""
        self.celdas_visibles = set(celdas_visibles)
        self._ultimo_estado = None
        self.actualizar()

    def actualizar(self):
        """Redibuja el mapa completo si hay cambios"""
        if not self.mapa:
            return
        estado_actual = (
            tuple(
                (c.q, c.r, id(card) if card else None)
                for c, card in sorted(
                    self.mapa.tablero.celdas.items(), key=lambda i: (i[0].q, i[0].r)
                )
            ),
            tuple(sorted((c.q, c.r) for c in self.celdas_visibles)),
        )
        if estado_actual == self._ultimo_estado:
            return
        self._ultimo_estado = estado_actual
        self._dibujar_mapa()
        log_evento("Mapa global dibujado")

    def calcular_celdas_visibles(self, jugador_actual):
        """Calcula celdas visibles para el jugador dado"""
        if not self.mapa or not jugador_actual:
            return set()
        from src.game.combate.ia.ia_utilidades import calcular_vision_jugador

        visibles = set()
        visibles.update(calcular_vision_jugador(jugador_actual, self.mapa))
        for zona in self.mapa.zonas_rojas + self.mapa.zonas_azules:
            visibles.update(zona.coordenadas)
        return visibles

    def _hex_points(self, x, y, size):
        import math
        points = []
        for i in range(6):
            angle = math.pi / 3 * i
            px = x + size * math.cos(angle)
            py = y + size * math.sin(angle)
            points.extend([px, py])
        return points

    def _coord_to_pixel(self, coord):
        import math
        x = self.hex_size * (3 / 2 * coord.q)
        y = self.hex_size * (math.sqrt(3) / 2 * coord.q + math.sqrt(3) * coord.r)
        return x, y

    def centrar_en_coordenada(self, coord):
        """Centra la vista en una coordenada"""
        if not coord:
            return
        x, y = self._coord_to_pixel(coord)
        cx, cy = x + 200, y + 200
        self._centrar_en_pixel(cx, cy)

    def _centrar_en_pixel(self, x, y):
        bbox = self.canvas.bbox("all")
        if not bbox:
            return
        ancho = self.canvas.winfo_width()
        alto = self.canvas.winfo_height()
        total_ancho = bbox[2]
        total_alto = bbox[3]
        self.canvas.xview_moveto(max(0, x - ancho / 2) / total_ancho)
        self.canvas.yview_moveto(max(0, y - alto / 2) / total_alto)

    def resaltar_coordenada(self, coord, duracion=1000):
        """Resalta una coordenada temporalmente"""
        x, y = self._coord_to_pixel(coord)
        cx, cy = x + 200, y + 200
        radio = self.hex_size * 0.6
        highlight = self.canvas.create_oval(
            cx - radio,
            cy - radio,
            cx + radio,
            cy + radio,
            outline="yellow",
            width=2,
            tags="highlight",
        )
        self._centrar_en_pixel(cx, cy)
        self.canvas.after(duracion, lambda: self.canvas.delete(highlight))

    def _dibujar_mapa(self):
        self.canvas.delete("all")
        board = self.mapa.tablero
        for coord in board.celdas:
            x, y = self._coord_to_pixel(coord)
            color = "white"
            zona_color = self.mapa.obtener_color_en(coord)
            if zona_color == "rojo":
                color = "#ffbbbb"
            elif zona_color == "azul":
                color = "#bbbbff"
            if self.celdas_visibles and coord not in self.celdas_visibles:
                color = "#1a1a1a"
            points = self._hex_points(x + 200, y + 200, self.hex_size)
            self.canvas.create_polygon(points, fill=color, outline="black")
        # Dibujar cartas en el tablero
        for coord, carta in board.celdas.items():
            if carta is None:
                continue

            # Posición base en el canvas
            x, y = self._coord_to_pixel(coord)
            cx, cy = x + 200, y + 200

            # Color según dueño de la carta
            jugador_color = getattr(carta.duenio, "color_fase_actual", "rojo")
            color = "red" if jugador_color == "rojo" else "blue"

            # Dibujar círculo representando la carta
            radio = self.hex_size * 0.4
            self.canvas.create_oval(
                cx - radio,
                cy - radio,
                cx + radio,
                cy + radio,
                fill=color,
                outline="black",
            )

            # Texto con el nombre (abreviado)
            self.canvas.create_text(
                cx,
                cy,
                text=carta.nombre[:8],
                fill="white",
                font=("Arial", 8, "bold"),
            )

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

