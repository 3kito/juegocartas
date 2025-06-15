"""
Configuración compartida para todos los tests
"""

import pytest
import sys
import os

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Configuración para tests
@pytest.fixture
def tablero_vacio():
    """Fixture que proporciona un tablero hexagonal vacío"""
    from src.game.tablero.tablero_hexagonal import TableroHexagonal
    return TableroHexagonal()

@pytest.fixture
def coordenadas_test():
    """Fixture que proporciona coordenadas de prueba"""
    from src.game.tablero.tablero_hexagonal import Coordenada
    return {
        'centro': Coordenada(0, 0),
        'vecino': Coordenada(1, 0),
        'lejana': Coordenada(2, 1)
    }