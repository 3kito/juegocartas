# tests/integration/test_sistema_interacciones.py

import pytest
from src.game.cartas.estado_carta import EstadoCarta
from src.game.combate import GestorInteracciones
from src.game.combate import Interaccion, TipoInteraccion
from src.game.combate import MotorTiempoReal

# Mock de carta base con atributos mínimos
class CartaMock:
    def __init__(self, id_, nombre, vida, dano, defensa, duenio):
        self.id = id_
        self.nombre = nombre
        self.vida_actual = vida
        self.dano_fisico_actual = dano
        self.defensa_fisica_actual = defensa
        self.duenio = duenio
        self.estado_carta = EstadoCarta(self)
        self.modo_control = "pasivo"
        self.rango = 1

    def es_aliado_de(self, otra):
        return self.duenio == otra.duenio

    def generar_interacciones(self, tablero):
        return [Interaccion(self.id, 2, TipoInteraccion.ATAQUE, metadata={"dano_base": 20})]

def test_interaccion_en_motor_tiempo_real():
    atacante = CartaMock(1, "Atacante", 100, 20, 0, "jugadorA")
    defensor = CartaMock(2, "Defensor", 50, 10, 5, "jugadorB")

    gestor = GestorInteracciones()
    gestor.registrar_estado_carta(atacante.estado_carta)
    gestor.registrar_estado_carta(defensor.estado_carta)

    # Simula una IA que decide atacar en el primer tick
    gestor.registrar_interaccion(
        Interaccion(fuente_id=1, objetivo_id=2, tipo=TipoInteraccion.ATAQUE, metadata={"dano_base": 20})
    )

    motor = MotorTiempoReal(fps_objetivo=30)
    motor.agregar_componente(gestor)

    motor.iniciar()

    # Ejecutar ticks manuales durante ~0.5 segundos
    import time
    start = time.time()
    while time.time() - start < 0.5:
        motor.tick()

    assert defensor.estado_carta.vida_actual == 35  # 20 - 5 defensa
    assert defensor.estado_carta.esta_viva()
