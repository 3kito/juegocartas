# ia_motor.py
from src.game.combate.ia.ia_acciones import construir_acciones
from src.game.combate.ia.ia_comportamiento import decidir_comportamiento
from src.game.combate.ia.ia_utilidades import (
    obtener_info_entorno,
    calcular_vision_jugador,
    mover_carta_con_pathfinding,
    atacar_si_en_rango,
)


def generar_interacciones_para(carta, tablero):
    """
    Punto de entrada principal para la IA.
    Decide y construye las interacciones que la carta debe ejecutar en este tick.
    """
    if not carta.esta_viva():
        return []

    info_entorno = obtener_info_entorno(carta, tablero)
    decision = decidir_comportamiento(carta, info_entorno)
    interacciones = construir_acciones(carta, decision, info_entorno)

    # Acciones básicas: mover hacia objetivo y atacar si es posible
    if decision["accion"] == "atacar" and decision["objetivos"]:
        objetivo = decision["objetivos"][0]
        if not atacar_si_en_rango(carta, objetivo):
            mover_carta_con_pathfinding(carta, objetivo.coordenada, tablero)

    return interacciones
