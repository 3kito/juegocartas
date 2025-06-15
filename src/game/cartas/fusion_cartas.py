"""
Fusionador de Cartas - Detecta y aplica fusiones automáticas combinando tablero y banco
"""

from collections import defaultdict
from src.utils.helpers import log_evento


def aplicar_fusiones(tablero, banco: list, limite: int = 10) -> list[str]:
    """Realiza fusiones de cartas entre tablero y banco.

    Ejecuta una sola fusión por iteración y vuelve a escanear el estado, lo que
    evita bucles infinitos cuando las colecciones cambian durante el proceso.
    """
    eventos = []
    iteraciones = 0

    while iteraciones < limite:
        iteraciones += 1

        # Recalcular agrupaciones en cada iteración
        cartas_por_nombre = defaultdict(list)
        for coord, carta in tablero.celdas.items():
            if carta:
                cartas_por_nombre[carta.nombre].append(("tablero", coord, carta))
        for idx, carta in enumerate(banco):
            if carta:
                cartas_por_nombre[carta.nombre].append(("banco", idx, carta))

        fusion_realizada = False
        for nombre, grupo in cartas_por_nombre.items():
            if len(grupo) >= 3:
                seleccionadas = grupo[:3]
                fuentes, ubicaciones, cartas = zip(*seleccionadas)

                carta_fusionada = cartas[0]
                carta_fusionada.tier += 1
                carta_fusionada.vida_maxima += 50
                carta_fusionada.vida_actual += 50
                carta_fusionada.dano_fisico_actual += 5
                carta_fusionada.dano_magico_actual += 5

                for fuente, ubicacion in list(zip(fuentes, ubicaciones))[1:]:
                    if fuente == "tablero":
                        tablero.quitar_carta(ubicacion)
                    else:
                        banco[ubicacion] = None

                ubicacion_final = (fuentes[0], ubicaciones[0])
                if ubicacion_final[0] == "tablero":
                    tablero.celdas[ubicacion_final[1]] = carta_fusionada
                else:
                    banco[ubicacion_final[1]] = carta_fusionada

                log_evento(
                    f"✨ Fusión realizada: {nombre} → Estrella {carta_fusionada.tier}"
                )
                eventos.append(
                    f"{nombre} fusionado en {ubicacion_final} → tier {carta_fusionada.tier}"
                )

                fusion_realizada = True
                break

        if not fusion_realizada:
            break

    if iteraciones >= limite and fusion_realizada:
        log_evento("⚠️ Límite de iteraciones de fusión alcanzado")

    # Reconstruir banco sin huecos
    if indices_eliminar or fusiones_en_banco:
        nuevo_banco = []
        for idx, carta in enumerate(banco):
            if idx in indices_eliminar:
                continue
            if idx in fusiones_en_banco:
                nuevo_banco.append(fusiones_en_banco[idx])
            else:
                nuevo_banco.append(carta)
        banco[:] = nuevo_banco

    return eventos
