"""Interfaz gráfica sencilla para controlar el juego."""

from __future__ import annotations

from typing import List

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .board_widget import BoardWidget

from src.core.jugador import Jugador
from src.core.motor_juego import MotorJuego
from src.utils.helpers import log_evento, set_log_callback


class PlayerTab(QWidget):
    """Widget que muestra la información y acciones de un jugador."""

    def __init__(self, jugador: Jugador, motor: MotorJuego):
        super().__init__()
        self.jugador = jugador
        self.motor = motor

        self.info_label = QLabel()

        self.board = BoardWidget(jugador.tablero)


        self.tienda_layout = QVBoxLayout()
        self.reroll_btn = QPushButton("Reroll")
        self.reroll_btn.clicked.connect(self.hacer_reroll)

        v = QVBoxLayout(self)
        v.addWidget(self.info_label)

        v.addWidget(self.board)

        v.addLayout(self.tienda_layout)
        v.addWidget(self.reroll_btn)

        self.actualizar()

    # ------------------------------------------------------------------
    def actualizar(self):
        self.info_label.setText(
            f"Vida: {self.jugador.vida}  Oro: {self.jugador.oro}  Nivel: {self.jugador.nivel}"
        )

        self.board.actualizar()


        # Actualizar tienda si estamos en fase de preparación
        if self.motor.fase_actual == "preparacion":
            self._cargar_tienda()
        else:
            self._limpiar_tienda("En combate...")

    # ------------------------------------------------------------------
    def _limpiar_tienda(self, mensaje: str = ""):
        for i in reversed(range(self.tienda_layout.count())):
            item = self.tienda_layout.takeAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        if mensaje:
            self.tienda_layout.addWidget(QLabel(mensaje))

    # ------------------------------------------------------------------
    def _cargar_tienda(self):
        self._limpiar_tienda()
        tienda = self.motor.get_tienda_para(self.jugador.id)
        if not tienda:
            self.tienda_layout.addWidget(QLabel("Sin tienda"))
            return
        for idx, carta in enumerate(tienda.cartas_disponibles):
            fila = QHBoxLayout()
            info = QLabel(f"[{idx}] {carta.nombre} - {carta.costo} oro")
            btn = QPushButton("Comprar")
            btn.clicked.connect(lambda _, i=idx: self.comprar(i))
            fila.addWidget(info)
            fila.addWidget(btn)
            self.tienda_layout.addLayout(fila)

    # ------------------------------------------------------------------
    def comprar(self, indice: int):
        controlador = self.motor.controlador_preparacion
        resultado = controlador.realizar_compra_tienda(self.jugador.id, indice)
        log_evento(f"{self.jugador.nombre}: {resultado}")
        self.actualizar()

    # ------------------------------------------------------------------
    def hacer_reroll(self):
        controlador = self.motor.controlador_preparacion
        resultado = controlador.realizar_reroll_tienda(self.jugador.id)
        log_evento(f"{self.jugador.nombre}: {resultado}")
        self.actualizar()


class GameGUI(QMainWindow):
    def __init__(self, jugadores: List[Jugador]):
        super().__init__()
        self.setWindowTitle("Juego de Cartas")

        self.motor = MotorJuego(jugadores)
        self.motor.iniciar()

        self.tabs = QTabWidget()
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.fin_btn = QPushButton("Finalizar preparación")
        self.fin_btn.clicked.connect(self.finalizar_preparacion)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.addWidget(self.tabs)
        layout.addWidget(self.fin_btn)
        layout.addWidget(self.log_view)

        for j in jugadores:
            tab = PlayerTab(j, self.motor)
            self.tabs.addTab(tab, j.nombre)

        set_log_callback(self.agregar_log)

        # Actualizar interfaz periódicamente
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.actualizar)
        self.timer.start()

        self.actualizar()

    # ------------------------------------------------------------------
    def agregar_log(self, mensaje: str, _nivel: str):
        self.log_view.append(mensaje)

    # ------------------------------------------------------------------
    def actualizar(self):
        fase = self.motor.fase_actual
        if fase == "preparacion":
            self.fin_btn.setEnabled(True)
            self.fin_btn.setText("Finalizar preparación")
        else:
            self.fin_btn.setEnabled(False)
            self.fin_btn.setText("En combate...")

        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, PlayerTab):
                widget.actualizar()

    # ------------------------------------------------------------------
    def finalizar_preparacion(self):
        if self.motor.fase_actual == "preparacion":
            self.motor.controlador_preparacion.finalizar_fase()


def ejecutar_gui(num_jugadores: int = 2):
    jugadores = [Jugador(i + 1, f"Jugador {i+1}") for i in range(num_jugadores)]
    app = QApplication([])
    gui = GameGUI(jugadores)
    gui.resize(640, 480)
    gui.show()
    app.exec()


if __name__ == "__main__":
    ejecutar_gui()

