# gestor_turnos.py

class GestorTurnos:
    def __init__(self, jugadores_por_color: dict, secuencia_turnos: list[dict]):
        """
        jugadores_por_color: dict con claves "rojo" y "azul", cada una una lista de IDs o jugadores
        secuencia_turnos: lista de dicts, ej: [{"color": "rojo", "duracion": 15}, ...]
        """
        self.jugadores_por_color = jugadores_por_color
        self.secuencia_turnos = secuencia_turnos
        self.turno_actual = 0

    def turno_actual_info(self) -> dict:
        return self.secuencia_turnos[self.turno_actual]

    def jugadores_activos(self) -> list:
        color = self.turno_actual_info()["color"]
        return self.jugadores_por_color.get(color, [])

    def avanzar_turno(self):
        self.turno_actual += 1

    def total_turnos(self) -> int:
        return len(self.secuencia_turnos)

    def termino_fase(self) -> bool:
        return self.turno_actual >= len(self.secuencia_turnos)

    def jugador_esta_activo(self, jugador_id) -> bool:
        return jugador_id in self.jugadores_activos()
