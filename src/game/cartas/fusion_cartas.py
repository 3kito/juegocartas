"""
Fusionador de Cartas - Detecta y aplica fusiones automáticas combinando tablero y banco
"""

from collections import defaultdict
from src.utils.helpers import log_evento


def aplicar_fusiones(tablero, banco: list, limite: int = 10) -> list[str]:
    """
    Detecta tríos de cartas iguales (por nombre) entre el tablero y el banco,
    y realiza la fusión dejando la carta mejorada en la posición original de alguna del tablero o en el banco si no hay.
    """
    eventos = []
    cartas_por_nombre = defaultdict(list)  # nombre -> lista de (fuente, ubicacion, carta)

    # Agrupar cartas del tablero
    for coord, carta in tablero.celdas.items():
        if carta:
            cartas_por_nombre[carta.nombre].append(("tablero", coord, carta))

    # Agrupar cartas del banco
    for idx, carta in enumerate(banco):
        if carta:
            cartas_por_nombre[carta.nombre].append(("banco", idx, carta))

    # Procesar fusiones
    for nombre, grupo in list(cartas_por_nombre.items()):
        fusiones_realizadas = 0
        while len(grupo) >= 3 and fusiones_realizadas < limite:
            seleccionadas = grupo[:3]
            grupo = grupo[3:]
            cartas_por_nombre[nombre] = grupo
            fusiones_realizadas += 1

            fuentes, ubicaciones, cartas = zip(*seleccionadas)
            carta_fusionada = cartas[0]
            carta_fusionada.tier += 1
            carta_fusionada.vida_maxima += 50
            carta_fusionada.vida_actual += 50
            carta_fusionada.dano_fisico_actual += 5
            carta_fusionada.dano_magico_actual += 5

            # Remover otras dos
            restantes = list(zip(fuentes, ubicaciones))[1:]
            for fuente, ubicacion in restantes:
                if fuente == "tablero":
                    tablero.quitar_carta(ubicacion)
                else:
                    banco[ubicacion] = None

            # Colocar la fusionada
            ubicacion_final = (fuentes[0], ubicaciones[0])
            if ubicacion_final[0] == "tablero":
                tablero.celdas[ubicacion_final[1]] = carta_fusionada
            else:
                banco[ubicacion_final[1]] = carta_fusionada

            log_evento(f"✨ Fusión realizada: {nombre} → Estrella {carta_fusionada.tier}")
            eventos.append(f"{nombre} fusionado en {ubicacion_final} → tier {carta_fusionada.tier}")

    return eventos
