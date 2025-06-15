# modificadores_basicos.py

def aplicar_defensas(dano_base: int, objetivo, tipo_dano: str = "fisico") -> float:
    """
    Resta defensa al daño base según el tipo (físico o mágico).
    """
    if tipo_dano == "fisico":
        defensa = objetivo.defensa_fisica_actual
    elif tipo_dano == "magico":
        defensa = objetivo.defensa_magica_actual
    else:
        defensa = 0

    return max(1, dano_base - defensa)
