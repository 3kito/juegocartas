import pytest
import time

from src.game.cartas.estado_carta import EstadoCarta
from src.game.combate import GestorInteracciones
from src.game.combate import MotorTiempoReal
from src.game.tablero.tablero_hexagonal import TableroHexagonal
from src.game.tablero.coordenada import CoordenadaHexagonal
from src.game.combate import Interaccion, TipoInteraccion

class CartaMock:
    def __init__(self, id_, nombre, vida, dano, defensa, duenio):
        self.id = id_
        self.nombre = nombre
        self.vida_actual = vida
        self.vida_maxima = vida
        self.dano_fisico_actual = dano
        self.defensa_fisica_actual = defensa
        self.duenio = duenio
        self.rango = 1
        self.modo_control = "pasivo"
        self.estado_carta = EstadoCarta(self)

    def es_aliado_de(self, otra):
        return self.duenio == otra.duenio

    def generar_interacciones(self, tablero):
        coord = tablero.obtener_coordenada_de(self)
        if not coord:
            return []
        interacciones = []
        for otra_coord, otra in tablero.obtener_cartas_en_rango(coord, self.rango):
            if otra != self and not self.es_aliado_de(otra):
                interacciones.append(
                    Interaccion(
                        fuente_id=self.id,
                        objetivo_id=otra.id,
                        tipo=TipoInteraccion.ATAQUE,
                        metadata={"dano_base": self.dano_fisico_actual}
                    )
                )
        return interacciones

    def __eq__(self, other):
        return isinstance(other, CartaMock) and self.id == other.id

    def __hash__(self):
        return hash(self.id)

def test_interacciones_tablero_completo():
    tablero = TableroHexagonal()

    # 🛠 Agregamos manualmente las coordenadas necesarias al tablero
    coordenadas_usadas = [
        CoordenadaHexagonal(0, 0),
        CoordenadaHexagonal(1, -1),
        CoordenadaHexagonal(3, -3),
        CoordenadaHexagonal(4, -4),
        CoordenadaHexagonal(10, 10),
        CoordenadaHexagonal(15, 15),
        CoordenadaHexagonal(20, 0),
        CoordenadaHexagonal(21, -1),
    ]
    for coord in coordenadas_usadas:
        tablero.celdas[coord] = None

    gestor = GestorInteracciones(tablero)
    motor = MotorTiempoReal(fps_objetivo=20)
    motor.agregar_componente(gestor)
    motor.iniciar()

    # 🧪 Escenario 1: Carta A ataca a B
    carta1 = CartaMock(1, "Aliada", 100, 30, 0, "jugadorA")
    carta2 = CartaMock(2, "Enemiga", 60, 10, 5, "jugadorB")

    tablero.colocar_carta(carta1, CoordenadaHexagonal(0, 0))
    tablero.colocar_carta(carta2, CoordenadaHexagonal(1, -1))

    gestor.registrar_estado_carta(carta1.estado_carta)
    gestor.registrar_estado_carta(carta2.estado_carta)

    for _ in range(15):
        motor.tick()

    assert carta2.estado_carta.vida_actual <= 35

    # 🧪 Escenario 2: Ambas se atacan, una muere
    carta3 = CartaMock(3, "Tanque", 80, 50, 0, "jugadorC")
    carta4 = CartaMock(4, "Vidrio", 40, 40, 0, "jugadorD")

    tablero.colocar_carta(carta3, CoordenadaHexagonal(3, -3))
    tablero.colocar_carta(carta4, CoordenadaHexagonal(4, -4))

    gestor.registrar_estado_carta(carta3.estado_carta)
    gestor.registrar_estado_carta(carta4.estado_carta)

    for _ in range(20):
        motor.tick()

    vivos = [c for c in [carta3, carta4] if c.estado_carta.esta_viva()]
    assert len(vivos) <= 1

    # 🧪 Escenario 3: se acercan y atacan luego
    carta5 = CartaMock(5, "Paciente", 90, 20, 5, "jugadorE")
    carta6 = CartaMock(6, "Impulsivo", 90, 20, 5, "jugadorF")

    tablero.colocar_carta(carta5, CoordenadaHexagonal(10, 10))
    tablero.colocar_carta(carta6, CoordenadaHexagonal(15, 15))

    gestor.registrar_estado_carta(carta5.estado_carta)
    gestor.registrar_estado_carta(carta6.estado_carta)

    for _ in range(10):
        motor.tick()

    assert carta5.estado_carta.vida_actual == 90
    assert carta6.estado_carta.vida_actual == 90

    # Simulan que se mueven a rango
    tablero.mover_carta(CoordenadaHexagonal(10, 10), CoordenadaHexagonal(20, 0))
    tablero.mover_carta(CoordenadaHexagonal(15, 15), CoordenadaHexagonal(21, -1))

    for _ in range(10):
        motor.tick()

    assert carta5.estado_carta.vida_actual < 90 or carta6.estado_carta.vida_actual < 90
