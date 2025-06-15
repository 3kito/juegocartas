from src.game.combate import MapaGlobal
from src.game.tablero.coordenada import CoordenadaHexagonal

class CartaMock:
    def __init__(self, nombre):
        self.nombre = nombre

def test_mapa_tiene_suficientes_celdas():
    mapa = MapaGlobal(radio=11)
    total_celdas = len(mapa.celdas)
    assert total_celdas >= 180, f"Se esperaban al menos 180 celdas, se encontraron {total_celdas}"

def test_mapa_tiene_zonas_pareadas():
    mapa = MapaGlobal(radio=11)
    rojas = mapa.zonas_rojas
    azules = mapa.zonas_azules

    assert len(rojas) == 3, f"Se esperaban 3 zonas rojas, pero se encontraron {len(rojas)}"
    assert len(azules) == 3, f"Se esperaban 3 zonas azules, pero se encontraron {len(azules)}"

def test_zonas_son_cercanas_a_su_pareja():
    mapa = MapaGlobal(radio=11)
    for i, (roja, azul) in enumerate(zip(mapa.zonas_rojas, mapa.zonas_azules)):
        distancia_minima = min(
            r.distancia_a(a) for r in roja.coordenadas for a in azul.coordenadas
        )
        assert distancia_minima <= 5, f"Pareja {i} está demasiado alejada: distancia mínima {distancia_minima}"

def test_coordenadas_zonas_existen_en_tablero():
    mapa = MapaGlobal(radio=11)
    for zona in mapa.zonas_rojas + mapa.zonas_azules:
        for coord in zona.coordenadas:
            assert coord in mapa.celdas, f"Coordenada {coord} de zona no está en el tablero"
            assert isinstance(coord, CoordenadaHexagonal), f"{coord} no es CoordenadaHexagonal"

def test_colocacion_funciona_correctamente():
    mapa = MapaGlobal(radio=11)
    for zona in mapa.zonas_rojas:
        coords_validas = [c for c in zona.coordenadas if c in mapa.tablero.celdas and mapa.tablero.celdas[c] is None]
        if coords_validas:
            coord_libre = coords_validas[0]
            carta = CartaMock("Test")
            mapa.tablero.colocar_carta(coord_libre, carta)
            assert mapa.tablero.obtener_celda(coord_libre) == carta, "La carta no fue colocada correctamente"
            break
    else:
        raise AssertionError("No se encontraron coordenadas libres en zonas rojas para probar la colocación")
