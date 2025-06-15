# ia_comportamiento.py

def decidir_comportamiento(carta, info_entorno):
    """
    Determina la intención de la carta basada en su rol, vida y entorno.
    Ejemplo de decisiones: 'atacar', 'huir', 'esperar', 'mover'.
    """
    enemigos_cercanos = info_entorno.get("enemigos_en_rango", [])
    vida_actual = carta.vida_actual
    vida_maxima = carta.vida_maxima

    if vida_actual < vida_maxima * 0.3:
        return {"accion": "huir", "objetivos": enemigos_cercanos}

    if enemigos_cercanos:
        return {"accion": "atacar", "objetivos": enemigos_cercanos}

    return {"accion": "esperar", "objetivos": []}
