import os
import sys
import src.game.combate.interacciones.gestor_interacciones as gestor_mod

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.game.cartas.estado_carta import EstadoCarta
from src.game.cartas.carta_base import CartaBase
from src.game.tablero.tablero_hexagonal import TableroHexagonal

def crear_carta(id, duenio, modo_control="activo"):
    datos = {
        "id": id,
        "nombre": f"Test{id}",
        "tier": 1,
        "stats": {"vida": 100, "dano_fisico": 20, "rango_ataque": 1}
    }
    carta = CartaBase(datos)
    carta.duenio = duenio
    carta.modo_control = modo_control
    return carta

def test_activa_sin_orden_usa_ia(monkeypatch):
    tablero = TableroHexagonal(radio=2)
    gestor = gestor_mod.GestorInteracciones(tablero=tablero)

    carta = crear_carta(1, 1, "activo")
    estado = EstadoCarta(carta)

    gestor.registrar_estado_carta(estado)

    # Parchamos la IA para verificar si se llama
    llamada = {"ejecutada": False}

    def mock_generar_interacciones_para(c, t):
        llamada["ejecutada"] = True
        return []

    monkeypatch.setattr(gestor_mod, "generar_interacciones_para", mock_generar_interacciones_para)

    gestor.procesar_tick(0.1)

    assert llamada["ejecutada"], "La IA no fue llamada para carta activa sin orden"

def test_activa_con_orden_no_usa_ia(monkeypatch):
    tablero = TableroHexagonal(radio=2)
    gestor = GestorInteracciones(tablero=tablero)

    carta = crear_carta(2, 1, "activo")
    carta.marcar_orden_manual()
    estado = EstadoCarta(carta)

    gestor.registrar_estado_carta(estado)

    llamada = {"ejecutada": False}

    def mock_generar_interacciones_para(c, t):
        llamada["ejecutada"] = True
        return []

    monkeypatch.setattr("src.game.combate.ia.ia_motor.generar_interacciones_para", mock_generar_interacciones_para)

    gestor.procesar_tick(0.1)

    assert not llamada["ejecutada"], "La IA se ejecutó pese a tener orden manual pendiente"

if __name__ == "__main__":
    test_activa_sin_orden_usa_ia()
    test_activa_con_orden_no_usa_ia()
    print("✅ Tests IA fallback pasaron correctamente.")
