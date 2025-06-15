import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.game.combate.calcular_dano.calculadora_dano import calcular_dano
from src.game.combate.interacciones.interaccion_modelo import Interaccion, TipoInteraccion


# Mocks básicos
class DummyEstado:
    def __init__(self, id, vida, dano, defensa_fisica, defensa_magica):
        self.id = id
        self.vida_actual = vida
        self.dano_base = dano
        self.defensa_fisica_actual = defensa_fisica
        self.defensa_magica_actual = defensa_magica


def test_dano_fisico_sin_defensa():
    atacante = DummyEstado(1, 100, 20, 0, 0)
    defensor = DummyEstado(2, 100, 0, 0, 0)
    interaccion = Interaccion(fuente_id=1, objetivo_id=2, tipo=TipoInteraccion.ATAQUE,
                              metadata={"dano_base": 20, "tipo_dano": "fisico"})

    dano = calcular_dano(atacante, defensor, interaccion)
    assert dano == 20, f"Se esperaba 20 de daño, se obtuvo {dano}"


def test_dano_fisico_con_defensa():
    atacante = DummyEstado(1, 100, 30, 0, 0)
    defensor = DummyEstado(2, 100, 0, 10, 0)
    interaccion = Interaccion(fuente_id=1, objetivo_id=2, tipo=TipoInteraccion.ATAQUE,
                              metadata={"dano_base": 30, "tipo_dano": "fisico"})

    dano = calcular_dano(atacante, defensor, interaccion)
    assert dano == 20, f"Se esperaba 20 de daño, se obtuvo {dano}"


def test_dano_magico_con_defensa_magica():
    atacante = DummyEstado(1, 100, 40, 0, 0)
    defensor = DummyEstado(2, 100, 0, 0, 15)
    interaccion = Interaccion(fuente_id=1, objetivo_id=2, tipo=TipoInteraccion.ATAQUE,
                              metadata={"dano_base": 40, "tipo_dano": "magico"})

    dano = calcular_dano(atacante, defensor, interaccion)
    assert dano == 25, f"Se esperaba 25 de daño, se obtuvo {dano}"


def test_dano_minimo_1():
    atacante = DummyEstado(1, 100, 5, 0, 0)
    defensor = DummyEstado(2, 100, 0, 999, 999)
    interaccion = Interaccion(fuente_id=1, objetivo_id=2, tipo=TipoInteraccion.ATAQUE,
                              metadata={"dano_base": 5, "tipo_dano": "fisico"})

    dano = calcular_dano(atacante, defensor, interaccion)
    assert dano == 1, f"El daño mínimo debería ser 1, se obtuvo {dano}"


if __name__ == "__main__":
    test_dano_fisico_sin_defensa()
    test_dano_fisico_con_defensa()
    test_dano_magico_con_defensa_magica()
    test_dano_minimo_1()
    print("✅ Todos los tests de calculadora de daño pasaron correctamente.")
