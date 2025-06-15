"""
Fusionador de Cartas - Detecta y aplica fusiones automáticas combinando tablero y banco
"""

from collections import defaultdict
from src.utils.helpers import log_evento


def aplicar_fusiones(tablero, banco: list) -> list[str]:
    """Aplica fusiones de cartas entre tablero y banco de forma controlada."""
    eventos = []
    iteraciones = 0
    fusion_realizada = True
    while fusion_realizada and iteraciones < 10:
        fusion_realizada = False
        iteraciones += 1
        log_evento(f"🔍 Búsqueda de fusiones (iteración {iteraciones})", "DEBUG")

        cartas_por_nombre = defaultdict(list)

        for coord, carta in tablero.celdas.items():
            if carta:
                cartas_por_nombre[carta.nombre].append(("tablero", coord, carta))

        for idx, carta in enumerate(banco):
            if carta:
                cartas_por_nombre[carta.nombre].append(("banco", idx, carta))

        for nombre, grupo in cartas_por_nombre.items():
            if len(group) >= 3:
                fuentes, ubicaciones, cartas = zip(*group[:3])
                carta_fusionada = cartas[0]
                carta_fusionada.tier += 1
                carta_fusionada.vida_maxima += 50
                carta_fusionada.vida_actual += 50
                carta_fusionada.dano_fisico_actual += 5
                carta_fusionada.dano_magico_actual += 5

                log_evento(
                    f"✨ Fusión realizada: {nombre} → Estrella {carta_fusionada.tier}",
                    "INFO",
                )
                eventos.append(
                    f"{nombre} fusionado → tier {carta_fusionada.tier}"
                )

                restantes = list(zip(fuentes, ubicaciones))[1:]
                for fuente, ubicacion in restantes:
                    if fuente == "tablero":
                        tablero.quitar_carta(ubicacion)
                    else:
                        banco[ubicacion] = None

                if fuentes[0] == "tablero":
                    tablero.celdas[ubicaciones[0]] = carta_fusionada
                else:
                    banco[ubicaciones[0]] = carta_fusionada

                banco[:] = [c for c in banco if c is not None]
                fusion_realizada = True
                break

    if iteraciones == 10 and fusion_realizada:
        log_evento("⚠️ Límite de iteraciones de fusión alcanzado", "WARNING")

    return eventos
