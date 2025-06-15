"""
Test unitarios para la TiendaIndividual sin JSON externo
"""

import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.game.tienda.tienda_individual import TiendaIndividual
from src.core.jugador import Jugador
from src.game.cartas.carta_base import CartaBase
from src.game.cartas import manager_cartas as global_manager


class MockManagerCartas:
    """Mock que reemplaza a manager_cartas"""
    def __init__(self):
        self.devueltas = []

    def obtener_cartas_aleatorias_por_nivel(self, nivel_jugador, cantidad=5):
        return [CartaBase({
            "id": i + 1,
            "nombre": f"Carta {i + 1}",
            "tier": 1,
            "costo": 2,
            "stats": {"vida": 100, "dano_fisico": 10}
        }) for i in range(cantidad)]

    def devolver_carta_al_pool(self, carta):
        self.devueltas.append(carta.id)


@pytest.fixture
def mock_tienda(monkeypatch):
    mock = MockManagerCartas()
    monkeypatch.setattr("src.game.tienda.tienda_individual.manager_cartas", mock)
    jugador = Jugador(1, "Test")
    jugador.oro = 10
    return TiendaIndividual(jugador), mock, jugador


class TestTiendaIndividual:
    def test_generacion_basica(self, mock_tienda):
        tienda, _, _ = mock_tienda
        assert len(tienda.cartas_disponibles) == 5
        for carta in tienda.cartas_disponibles:
            assert isinstance(carta, CartaBase)

    def test_compra_exitosa(self, mock_tienda):
        tienda, _, jugador = mock_tienda
        oro_inicial = jugador.oro
        resultado = tienda.comprar_carta(0)

        assert resultado.startswith("✅")
        assert len(jugador.cartas_banco) == 1
        assert jugador.oro == oro_inicial - jugador.cartas_banco[0].costo
        assert len(tienda.cartas_disponibles) == 4

    def test_reroll_funciona(self, mock_tienda):
        tienda, mock, jugador = mock_tienda

        # Compra una carta primero (quedan 4)
        compra = tienda.comprar_carta(0)
        assert compra.startswith("✅")
        assert len(tienda.cartas_disponibles) == 4

        # Gana token de reroll
        jugador.ganar_tokens_reroll(1)

        # Guarda las IDs antes del reroll
        anteriores = [c.id for c in tienda.cartas_disponibles]

        # Hace el reroll
        resultado = tienda.hacer_reroll()
        nuevos = [c.id for c in tienda.cartas_disponibles]

        # Verifica resultado
        assert resultado.startswith("🔄")
        assert len(mock.devueltas) == 4  # Solo las cartas visibles fueron devueltas
        assert len(tienda.cartas_disponibles) == 5  # Se vuelve a tener tienda completa
        assert anteriores != nuevos  # En la mayoría de los casos

    def test_compra_banco_lleno(self, mock_tienda):
        tienda, _, jugador = mock_tienda
        jugador.cartas_banco = [CartaBase({"id": i, "nombre": f"C{i}", "tier": 1, "costo": 1}) for i in range(jugador.MAX_CARTAS_BANCO)]

        resultado = tienda.comprar_carta(0)
        assert resultado == "❌ Banco lleno"

    def test_compra_sin_oro(self, mock_tienda):
        tienda, _, jugador = mock_tienda
        jugador.oro = 0
        resultado = tienda.comprar_carta(0)
        assert resultado == "❌ No tienes suficiente oro"

    def test_reroll_sin_token(self, mock_tienda):
        tienda, _, _ = mock_tienda
        resultado = tienda.hacer_reroll()
        assert resultado == "❌ No tienes tokens de reroll"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
