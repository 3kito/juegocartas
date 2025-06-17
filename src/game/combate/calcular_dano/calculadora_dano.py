# calculadora_dano.py

from src.game.combate.calcular_dano.modificadores_basicos import aplicar_defensas
from src.game.combate.calcular_dano.sinergias_dano import aplicar_bonus_sinergia
from src.game.combate.calcular_dano.efectos_especiales import aplicar_efectos_especiales

def calcular_dano(fuente, objetivo, interaccion) -> int:
    """
    Calcula el daño final a aplicar a un objetivo, considerando todas las capas de modificadores.
    """
    base = interaccion.metadata.get(
        "dano_base",
        getattr(fuente, "dano_base", getattr(fuente, "dano_fisico_actual", 0)),
    )
    tipo_dano = interaccion.metadata.get("tipo_dano", "fisico")

    dano_post_defensa = aplicar_defensas(base, objetivo, tipo_dano)
    dano_con_bonus = aplicar_bonus_sinergia(fuente, objetivo, dano_post_defensa)
    dano_final = aplicar_efectos_especiales(fuente, objetivo, interaccion, dano_con_bonus)

    return max(1, int(dano_final))  # Nunca menos de 1 de daño
