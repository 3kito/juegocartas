# ia_utilidades.py

def obtener_info_entorno(carta, tablero):
    """
    Recolecta información relevante del entorno para facilitar la toma de decisiones.
    Retorna:
        {
            "enemigos_en_rango": [...],
            "coordenada_actual": ...,
            ...
        }
    """
    coord = tablero.obtener_coordenada_de(carta)
    enemigos = []

    rango = getattr(carta, "rango_ataque_actual", 1)
    if coord:
        for otra_coord, otra_carta in tablero.obtener_cartas_en_rango(coord, rango):
            if otra_carta and not carta.es_aliado_de(otra_carta):
                enemigos.append(otra_carta)

    return {
        "coordenada_actual": coord,
        "enemigos_en_rango": enemigos
    }
