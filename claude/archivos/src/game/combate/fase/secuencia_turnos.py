def generar_secuencia_turnos(turnos_por_color=3, duracion=1, duracion_inicial_final=1):
    secuencia = []
    colores = ["rojo", "azul"]

    for i in range(turnos_por_color * 2):
        color = colores[i % 2]
        if i == 0 or i == (turnos_por_color * 2 - 1):
            dur = duracion_inicial_final
        else:
            dur = duracion
        secuencia.append({"color": color, "duracion": dur})
    return secuencia
