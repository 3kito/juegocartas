import tkinter as tk
from tkinter import ttk
from src.game.combate.mapa.mapa_global import MapaGlobal
from src.utils.helpers import log_evento
from src.utils.hex_utils import pixel_to_hex as util_pixel_to_hex, hex_to_pixel


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

    def __init__(self, master, mapa: MapaGlobal | None = None, hex_size: int = 20, debug: bool = False):
        super().__init__(master)
        self.mapa = mapa
        self._ultimo_estado = None
        self._after_id = None
        self._intervalo_ms = 500
        self.hex_size = hex_size
        self.offset = (200, 200)
        self.debug = debug
        self.celdas_visibles = set()  # coordenadas visibles para el jugador
        log_evento(
            f"InterfazMapaGlobal init hex_size={self.hex_size} offset={self.offset} debug={self.debug}"
        )

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

        visibles = set()

        # Mostrar siempre ambas zonas sin importar el turno
        zonas = self.mapa.zonas_rojas + self.mapa.zonas_azules
        for zona in zonas:
            visibles.update(zona.coordenadas)

        for coord, carta in self.mapa.tablero.celdas.items():
            if carta is not None and getattr(carta, "duenio", None) == jugador_actual:
                visibles.update(coord.obtener_area(carta.rango_vision))

        return visibles

    def actualizar_vision_para_jugador(self, jugador_actual):
        """Recalcula y actualiza la visibilidad según el jugador"""
        celdas = self.calcular_celdas_visibles(jugador_actual)
        self.actualizar_vision(celdas)

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
        """Convierte una coordenada hexagonal a posición en pixeles sin offset."""
        import math
        x = self.hex_size * (3 / 2 * coord.q)
        y = self.hex_size * (
            math.sqrt(3) / 2 * coord.q + math.sqrt(3) * coord.r
        )
        return x, y

    def _hex_round(self, q, r):
        """Redondea coordenadas axiales flotantes a enteras"""
        from src.game.tablero.coordenada import CoordenadaHexagonal

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

        return CoordenadaHexagonal(int(rx), int(rz))

    def pixel_to_hex(self, x, y):
        """Convierte coordenadas de pixel (con offset) a hexágono del mapa."""
        coord = util_pixel_to_hex(x, y, self.hex_size, self.offset)

        # Verificar conversión inversa para depuración
        vx, vy = hex_to_pixel(coord, self.hex_size, self.offset)
        log_evento(
            f"pixel_to_hex: click ({x}, {y}) -> {coord} -> ({vx:.2f}, {vy:.2f})"
        )

        if self.mapa and coord not in self.mapa.tablero.celdas:
            log_evento(
                f"pixel_to_hex: coordenada {coord} fuera del mapa", "DEBUG"
            )
            return None

        return coord

    def centrar_en_coordenada(self, coord):
        """Centra la vista en una coordenada"""
        if not coord:
            return
        cx, cy = hex_to_pixel(coord, self.hex_size, self.offset)
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
        cx, cy = hex_to_pixel(coord, self.hex_size, self.offset)
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
        text = self.canvas.create_text(
            cx,
            cy,
            text=f"({coord.q},{coord.r})",
            fill="yellow",
            font=("Arial", 10, "bold"),
            tags="highlight",
        )
        self._centrar_en_pixel(cx, cy)
        self.canvas.after(duracion, lambda: self.canvas.delete("highlight"))

    def _dibujar_mapa(self):
        self.canvas.delete("all")
        board = self.mapa.tablero
        for coord in board.celdas:
            x, y = hex_to_pixel(coord, self.hex_size, self.offset)
            color = "white"
            zona_color = self.mapa.obtener_color_en(coord)
            if zona_color == "rojo":
                color = "#ffbbbb"
            elif zona_color == "azul":
                color = "#bbbbff"
            if self.celdas_visibles and coord not in self.celdas_visibles:
                color = "#404040"
            points = self._hex_points(x, y, self.hex_size)
            self.canvas.create_polygon(points, fill=color, outline="black")
            if self.debug:
                self.canvas.create_text(
                    x,
                    y,
                    text=f"{coord.q},{coord.r}",
                    fill="black",
                    font=("Arial", 8),
                )
        # Dibujar cartas en el tablero
        for coord, carta in board.celdas.items():
            if carta is None:
                continue

            # Posición base en el canvas
            cx, cy = hex_to_pixel(coord, self.hex_size, self.offset)

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

    # === Actualización automática ===
    def iniciar_actualizacion_automatica(self, intervalo_ms: int = 500):
        """Inicia un loop que refresca el mapa periódicamente"""
        self._intervalo_ms = intervalo_ms
        if self._after_id:
            self.after_cancel(self._after_id)
        self._after_id = self.after(self._intervalo_ms, self._loop_actualizacion)

    def detener_actualizacion_automatica(self):
        """Detiene el refresco periódico"""
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

    def _loop_actualizacion(self):
        self.forzar_actualizacion()
        self._after_id = self.after(self._intervalo_ms, self._loop_actualizacion)

    def forzar_actualizacion(self):
        """Fuerza un redibujo del mapa"""
        self._ultimo_estado = None
        self.actualizar()

