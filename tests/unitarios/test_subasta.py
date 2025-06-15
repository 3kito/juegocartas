"""
Tests unitarios para SistemaSubastas sin depender del JSON
"""

import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.game.tienda.sistema_subastas import SistemaSubastas
from src.core.jugador import Jugador
from src.game.cartas.carta_base import CartaBase


@pytest.fixture
def mock_cartas(monkeypatch):
    """Reemplaza el manager_cartas global por un mock"""
    class MockManager:
        def __init__(self):
            self.contador = 0
            self.devueltas = []

        def obtener_cartas_aleatorias_por_nivel(self, nivel_jugador, cantidad=1):
            cartas = []
            for _ in range(cantidad):
                self.contador += 1
                carta = CartaBase({
                    "id": self.contador,
                    "nombre": f"FakeCarta{self.contador}",
                    "tier": 1,
                    "costo": 3,
                    "stats": {"vida": 100, "dano_fisico": 10}
                })
                cartas.append(carta)
            return cartas

        def devolver_carta_al_pool(self, carta):
            self.devueltas.append(carta)

    mock = MockManager()
    monkeypatch.setattr("src.game.tienda.sistema_subastas.manager_cartas", mock)
    return mock


@pytest.fixture
def jugadores():
    j1 = Jugador(1, "Ada")
    j2 = Jugador(2, "Turing")
    j1.oro = 10
    j2.oro = 10
    return j1, j2


def test_generar_subasta(mock_cartas, jugadores):
    j1, j2 = jugadores
    subasta = SistemaSubastas([j1, j2])
    subasta.generar_subasta(2)

    assert len(subasta.cartas_subastadas) == 2
    assert all(c["carta"].nombre.startswith("FakeCarta") for c in subasta.cartas_subastadas.values())


def test_oferta_valida(mock_cartas, jugadores):
    j1, j2 = jugadores
    subasta = SistemaSubastas([j1, j2])
    subasta.generar_subasta(1)
    carta_id = next(iter(subasta.cartas_subastadas))

    resultado = subasta.ofertar(j1, carta_id, 5)
    assert resultado.startswith("✅")
    assert subasta.cartas_subastadas[carta_id]["mejor_oferta"] == 5
    assert subasta.cartas_subastadas[carta_id]["jugador"] == j1


def test_oferta_menor_o_igual(mock_cartas, jugadores):
    j1, j2 = jugadores
    subasta = SistemaSubastas([j1, j2])
    subasta.generar_subasta(1)
    carta_id = next(iter(subasta.cartas_subastadas))

    subasta.ofertar(j1, carta_id, 5)
    resultado = subasta.ofertar(j2, carta_id, 5)

    assert resultado.startswith("❌")
    assert subasta.cartas_subastadas[carta_id]["jugador"] == j1


def test_sin_oro(mock_cartas, jugadores):
    j1, j2 = jugadores
    j2.oro = 2
    subasta = SistemaSubastas([j1, j2])
    subasta.generar_subasta(1)
    carta_id = next(iter(subasta.cartas_subastadas))

    resultado = subasta.ofertar(j2, carta_id, 3)
    assert resultado.startswith("❌")


def test_resolucion(mock_cartas, jugadores):
    j1, j2 = jugadores
    subasta = SistemaSubastas([j1, j2])
    subasta.generar_subasta(1)
    carta_id = next(iter(subasta.cartas_subastadas))
    carta = subasta.cartas_subastadas[carta_id]["carta"]

    subasta.ofertar(j1, carta_id, 6)
    oro_inicial = j1.oro
    subasta.resolver_subastas()

    assert carta in j1.cartas_banco
    assert j1.oro == oro_inicial - 6


def test_sin_ofertas_vuelve_al_pool(mock_cartas, jugadores):
    j1, j2 = jugadores
    subasta = SistemaSubastas([j1, j2])
    subasta.generar_subasta(1)
    carta = next(iter(subasta.cartas_subastadas.values()))["carta"]

    subasta.resolver_subastas()
    assert carta in mock_cartas.devueltas


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
