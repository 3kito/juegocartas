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

    if coord:
        for otra_coord, otra_carta in tablero.obtener_cartas_en_rango(coord, carta.rango_ataque_actual):
            if otra_carta and not carta.es_aliado_de(otra_carta):
                enemigos.append(otra_carta)

    return {
        "coordenada_actual": coord,
        "enemigos_en_rango": enemigos
    }


def calcular_vision_jugador(jugador, mapa_global):
    """Calcula las celdas visibles para un jugador"""
    celdas_visibles = set()
    # zonas segun color
    if jugador.color_fase_actual == "rojo":
        zonas = mapa_global.zonas_rojas
    else:
        zonas = mapa_global.zonas_azules
    for zona in zonas:
        celdas_visibles.update(zona.coordenadas)

    # rango alrededor de cartas propias
    for coord, carta in jugador.tablero.celdas.items():
        if carta is not None:
            area = coord.obtener_area(carta.rango_vision)
            celdas_visibles.update(area)

    return celdas_visibles


def _buscar_ruta(tablero, origen, destino):
    """Búsqueda simple en anchura"""
    from collections import deque

    visitados = set([origen])
    cola = deque([(origen, [])])
    while cola:
        actual, ruta = cola.popleft()
        if actual == destino:
            return ruta
        for vecino in actual.vecinos():
            if vecino in visitados:
                continue
            if not tablero.esta_dentro_del_tablero(vecino):
                continue
            if not tablero.esta_vacia(vecino) and vecino != destino:
                continue
            visitados.add(vecino)
            cola.append((vecino, ruta + [vecino]))
    return []


def mover_carta_con_pathfinding(carta, destino, mapa):
    """Mueve la carta paso a paso usando pathfinding"""
    origen = mapa.obtener_coordenada_de(carta)
    if origen is None:
        return False
    ruta = _buscar_ruta(mapa, origen, destino)
    if not ruta:
        return False
    # tiempo por celda
    for paso in ruta:
        mapa.mover_carta(origen, paso)
        origen = paso
    return True


def atacar_si_en_rango(carta_atacante, carta_objetivo):
    """Realiza un ataque simple si el objetivo está en rango"""
    if carta_atacante.coordenada is None or carta_objetivo.coordenada is None:
        return False
    if carta_atacante.coordenada.distancia(carta_objetivo.coordenada) > carta_atacante.rango_ataque_actual:
        return False
    from src.game.combate.interacciones.interaccion_modelo import Interaccion, TipoInteraccion
    inter = Interaccion(
        fuente_id=carta_atacante.id,
        objetivo_id=carta_objetivo.id,
        tipo=TipoInteraccion.ATAQUE,
        metadata={"dano_base": carta_atacante.dano_fisico_actual},
    )
    carta_objetivo.recibir_dano(carta_atacante.dano_fisico_actual)
    return True
