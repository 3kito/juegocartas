from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class HexCoordinate:
    q: int
    r: int

    def __add__(self, otro: "HexCoordinate") -> "HexCoordinate":
        return HexCoordinate(self.q + otro.q, self.r + otro.r)

    def __sub__(self, otro: "HexCoordinate") -> "HexCoordinate":
        return HexCoordinate(self.q - otro.q, self.r - otro.r)

    def s(self) -> int:
        return -self.q - self.r

    def distancia(self, otra: "HexCoordinate") -> int:
        """Devuelve la distancia hexagonal entre dos coordenadas."""
        return int((abs(self.q - otra.q) + abs(self.r - otra.r) + abs(self.s() - otra.s())) / 2)

    def distancia_a(self, otra: "HexCoordinate") -> int:
        """Otra forma de calcular la distancia, usando max de diferencias."""
        return max(
            abs(self.q - otra.q),
            abs(self.r - otra.r),
            abs(self.s() - otra.s())
        )

    def obtener_area(self, radio: int) -> List["HexCoordinate"]:
        """Devuelve todas las coordenadas dentro de un radio desde esta coordenada."""
        resultados = []
        for dq in range(-radio, radio + 1):
            for dr in range(max(-radio, -dq - radio), min(radio, -dq + radio) + 1):
                resultados.append(HexCoordinate(self.q + dq, self.r + dr))
        return resultados

    def vecinos(self) -> List["HexCoordinate"]:
        direcciones = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]
        return [
            HexCoordinate(self.q + dq, self.r + dr)
            for dq, dr in direcciones
        ]

    def __hash__(self):
        return hash((self.q, self.r))

    def __repr__(self):
        return f"({self.q}, {self.r})"
