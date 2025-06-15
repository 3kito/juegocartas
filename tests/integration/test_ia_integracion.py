import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.game.combate import GestorInteracciones
from src.game.cartas.estado_carta import EstadoCarta
from src.game.cartas.carta_base import CartaBase
from src.game.tablero.tablero_hexagonal import TableroHexagonal

def crear_carta(id, vida, dano, duenio, modo):
    datos = {
        'id': id,
        'nombre': f"Carta{id}",
        'tier': 1,
        'stats': {'vida': vida, 'dano_fisico': dano, 'rango_ataque': 1}
    }
    carta = CartaBase(datos)
    carta.duenio = duenio
    carta.modo_control = modo
    return carta

def test_ia_generacion_interaccion():
    tablero = TableroHexagonal(radio=2)
    gestor = GestorInteracciones(tablero=tablero)

    # Colocar dos cartas enfrentadas (no aliadas)
    carta_1 = crear_carta(1, 100, 20, 1, "pasivo")
    carta_2 = crear_carta(2, 100, 15, 2, "pasivo")

    coord_1 = list(tablero.celdas.keys())[0]
    coord_2 = next(iter(coord_1.vecinos()))

    carta_1.coordenada = coord_1
    carta_2.coordenada = coord_2

    tablero.colocar_carta(coord_1, carta_1)
    tablero.colocar_carta(coord_2, carta_2)

    estado_1 = EstadoCarta(carta_1)
    estado_2 = EstadoCarta(carta_2)

    gestor.registrar_estado_carta(estado_1)
    gestor.registrar_estado_carta(estado_2)

    gestor.procesar_tick(0.1)

    assert estado_2.vida_actual < 100, "La IA no ejecutó un ataque como se esperaba"
    print("✅ Test de integración de IA ejecutado con éxito")

if __name__ == "__main__":
    test_ia_generacion_interaccion()
