# ia_motor.py
from src.game.combate.ia.ia_acciones import construir_acciones
from src.game.combate.ia.ia_comportamiento import decidir_comportamiento
from src.game.combate.ia.ia_utilidades import obtener_info_entorno


def generar_interacciones_para(carta, tablero):
    """
    Punto de entrada principal para la IA.
    Decide y construye las interacciones que la carta debe ejecutar en este tick.
    """
    esta_viva = getattr(carta, "esta_viva", lambda: True)()
    if not esta_viva:
        return []

    info_entorno = obtener_info_entorno(carta, tablero)
    decision = decidir_comportamiento(carta, info_entorno)
    interacciones = construir_acciones(carta, decision, info_entorno)
    return interacciones
