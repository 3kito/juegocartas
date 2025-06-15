import tkinter as tk
from tkinter import ttk
from src.game.combate.mapa.mapa_global import MapaGlobal
from src.utils.helpers import log_evento


class InterfazMapaGlobal(ttk.Frame):
    """Widget para visualizar el mapa global"""

    def __init__(self, master, mapa: MapaGlobal, hex_size: int = 20):
        super().__init__(master)
        self.mapa = mapa
        self.hex_size = hex_size

        self.canvas = tk.Canvas(self, width=600, height=400, bg="white")
        h_scroll = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        v_scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._dibujar_mapa()

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
            points = self._hex_points(x + 200, y + 200, self.hex_size)
            self.canvas.create_polygon(points, fill=color, outline="black")
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        log_evento("Mapa global dibujado")

