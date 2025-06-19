import math
from src.game.board.hex_coordinate import HexCoordinate


def hex_round(q: float, r: float) -> HexCoordinate:
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
    return HexCoordinate(int(rx), int(rz))


def pixel_to_hex(x: float, y: float, hex_size: int, offset: tuple[int, int] = (0, 0)) -> HexCoordinate:
    px = x - offset[0]
    py = y - offset[1]
    q = (2 / 3 * px) / hex_size
    r = (-1 / 3 * px + math.sqrt(3) / 3 * py) / hex_size
    return hex_round(q, r)


def hex_to_pixel(coord: HexCoordinate, hex_size: int, offset: tuple[int, int] = (0, 0)) -> tuple[float, float]:
    x = hex_size * (3 / 2 * coord.q)
    y = hex_size * (math.sqrt(3) / 2 * coord.q + math.sqrt(3) * coord.r)
    return x + offset[0], y + offset[1]
