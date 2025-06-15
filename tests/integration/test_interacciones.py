import sys
import os

# Agrega el path a la carpeta raíz del proyecto dinámicamente
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, project_root)

from src.game.cartas.estado_carta import EstadoCarta
from src.game.combate import GestorInteracciones
from src.game.combate import Interaccion, TipoInteraccion

# Carta mock mínima (no importa que sea simplificada)
class CartaMock:
    def __init__(self, id_, nombre, vida=50, dano=20, defensa=5):
        self.id = id_
        self.nombre = nombre
        self.vida_actual = vida
        self.dano_fisico_actual = dano
        self.defensa_fisica_actual = defensa


class TestInteraccionesSimples:
    def test_ataque_directo_aplica_dano(self):
        carta_a = CartaMock(1, "Atacante", vida=100, dano=30)
        carta_b = CartaMock(2, "Defensor", vida=80, dano=10)

        estado_a = EstadoCarta(carta_a)
        estado_b = EstadoCarta(carta_b)

        gestor = GestorInteracciones()
        gestor.registrar_estado_carta(estado_a)
        gestor.registrar_estado_carta(estado_b)

        # Crear interacción de ataque
        interaccion = Interaccion(
            fuente_id=1,
            objetivo_id=2,
            tipo=TipoInteraccion.ATAQUE,
            metadata={"dano_base": 30}
        )

        gestor.registrar_interaccion(interaccion)

        # Ejecutar un tick (no importa el delta_time real en este caso)
        gestor.procesar_tick(0.1)

        # Verificar que el defensor recibió daño (30 - 5 defensa = 25)
        assert estado_b.vida_actual == 55
        assert estado_b.esta_viva()
