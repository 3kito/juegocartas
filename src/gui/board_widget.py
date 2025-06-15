from PySide6.QtWidgets import QLabel, QWidget, QGridLayout

from src.game.tablero.tablero_hexagonal import TableroHexagonal


class BoardWidget(QWidget):
    """Muestra el tablero hexagonal de un jugador de forma simple."""

    def __init__(self, tablero: TableroHexagonal):
        super().__init__()
        self.tablero = tablero
        self.labels = {}
        size = tablero.radio * 2 + 1
        layout = QGridLayout(self)
        layout.setSpacing(1)
        for coord in tablero.celdas:
            row = coord.r + tablero.radio
            col = coord.q + tablero.radio
            label = QLabel()
            label.setFixedSize(30, 30)
            label.setStyleSheet("border:1px solid gray; font-size:10px; text-align:center;")
            layout.addWidget(label, row, col)
            self.labels[coord] = label
        self.actualizar()

    def actualizar(self):
        for coord, label in self.labels.items():
            carta = self.tablero.celdas.get(coord)
            label.setText(carta.nombre[0] if carta else "")

