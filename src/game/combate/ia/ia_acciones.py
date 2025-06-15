# ia_acciones.py
from src.game.combate.interacciones.interaccion_modelo import Interaccion, TipoInteraccion


def construir_acciones(carta, decision, info_entorno):
    """
    Genera una lista de Interacciones basadas en la decisión tomada.
    """
    acciones = []

    if decision["accion"] == "atacar":
        for objetivo in decision["objetivos"]:
            acciones.append(Interaccion(
                fuente_id=carta.id,
                objetivo_id=objetivo.id,
                tipo=TipoInteraccion.ATAQUE,
                metadata={"dano_base": carta.dano_fisico_actual}
            ))

    # Otros tipos como huir, mover, usar habilidad, etc., se agregarán aquí

    return acciones
