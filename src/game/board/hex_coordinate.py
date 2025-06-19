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

    def __mul__(self, escalar: int) -> "HexCoordinate":
        """Multiplica la coordenada por un escalar"""
        return HexCoordinate(self.q * escalar, self.r * escalar)

    __rmul__ = __mul__

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


# === Utilidades de patrones de visión ===

# Direcciones axiales básicas, útiles para construir patrones.
DIRECCIONES = [
    HexCoordinate(1, 0),
    HexCoordinate(1, -1),
    HexCoordinate(0, -1),
    HexCoordinate(-1, 0),
    HexCoordinate(-1, 1),
    HexCoordinate(0, 1),
]


def aplicar_offset(base: "HexCoordinate", offset: "HexCoordinate") -> "HexCoordinate":
    """Devuelve ``base`` desplazada por ``offset``"""
    return HexCoordinate(base.q + offset.q, base.r + offset.r)


def patron_circular(radio: int) -> List[HexCoordinate]:
    """Genera un patrón circular centrado en (0,0)"""
    return HexCoordinate(0, 0).obtener_area(radio)


def patron_linea(direccion: HexCoordinate, longitud: int) -> List[HexCoordinate]:
    """Genera un patrón en línea recta desde el origen"""
    coords = [HexCoordinate(0, 0)]
    for i in range(1, longitud + 1):
        coords.append(direccion * i)
    return coords


def patron_cono(direccion: HexCoordinate, longitud: int) -> List[HexCoordinate]:
    """Genera un patrón de cono sencillo en la dirección indicada"""
    coords = [HexCoordinate(0, 0)]
    idx = DIRECCIONES.index(direccion)
    izquierda = DIRECCIONES[(idx - 1) % len(DIRECCIONES)]
    derecha = DIRECCIONES[(idx + 1) % len(DIRECCIONES)]
    for dist in range(1, longitud + 1):
        base = direccion * dist
        coords.append(base)
        for offset in range(1, dist + 1):
            coords.append(base + izquierda * offset)
            coords.append(base + derecha * offset)
    # Eliminar duplicados preservando orden
    vistos = set()
    unicos = []
    for c in coords:
        if (c.q, c.r) not in vistos:
            unicos.append(c)
            vistos.add((c.q, c.r))
    return unicos

