import random
from typing import Callable, Dict
# Las utilidades se importan de forma perezosa para evitar ciclos


# Conditions return bool

def condicion_enemigo_en_rango(carta, tablero, info_entorno):
    return bool(info_entorno.get("enemigos_en_rango"))


def condicion_enemigo_visible(carta, tablero, info_entorno):
    return bool(info_entorno.get("enemigos", info_entorno.get("enemigos_en_rango", [])))


def condicion_ha_recibido_dano(carta, tablero, info_entorno):
    return carta.stats_combate.get("dano_recibido", 0) > 0


# Actions return list of Interaccion or None

def accion_mover_aleatorio(carta, tablero, info_entorno):
    libres = tablero.coordenadas_libres()
    if not libres or carta.coordenada is None:
        return []
    destino = random.choice(libres)
    from src.game.combate.ia.ia_utilidades import mover_carta_con_pathfinding
    mover_carta_con_pathfinding(carta, destino, tablero)
    return []


def accion_mover_hacia_enemigo(carta, tablero, info_entorno):
    enemigos = info_entorno.get("enemigos_en_rango") or info_entorno.get("enemigos", [])
    if not enemigos:
        return []
    objetivo = enemigos[0]
    from src.game.combate.ia.ia_utilidades import mover_carta_con_pathfinding
    mover_carta_con_pathfinding(carta, objetivo.coordenada, tablero)
    return []


def accion_mover_lejos(carta, tablero, info_entorno):
    enemigos = info_entorno.get("enemigos_en_rango")
    if not enemigos or carta.coordenada is None:
        return []
    origen = carta.coordenada
    opciones = [c for c in origen.vecinos() if tablero.esta_dentro_del_tablero(c) and tablero.esta_vacia(c)]
    opciones.sort(key=lambda c: c.distancia(enemigos[0].coordenada), reverse=True)
    if opciones:
        from src.game.combate.ia.ia_utilidades import mover_carta_con_pathfinding
        mover_carta_con_pathfinding(carta, opciones[0], tablero)
    return []


def accion_atacar_objetivo(carta, tablero, info_entorno):
    from src.game.combate.interacciones.interaccion_modelo import Interaccion, TipoInteraccion
    from src.game.combate.ia.ia_utilidades import atacar_si_en_rango

    enemigos = info_entorno.get("enemigos_en_rango")
    if not enemigos:
        return []
    objetivo = enemigos[0]
    if atacar_si_en_rango(carta, objetivo):
        return [
            Interaccion(
                fuente_id=carta.id,
                objetivo_id=objetivo.id,
                tipo=TipoInteraccion.ATAQUE,
                metadata={"dano_base": carta.dano_fisico_actual},
            )
        ]
    return []


CONDITIONS: Dict[str, Callable] = {
    "enemigo_en_rango": condicion_enemigo_en_rango,
    "enemigo_visible": condicion_enemigo_visible,
    "ha_recibido_dano": condicion_ha_recibido_dano,
}

ACTIONS: Dict[str, Callable] = {
    "mover_aleatorio": accion_mover_aleatorio,
    "mover_hacia_enemigo": accion_mover_hacia_enemigo,
    "mover_lejos": accion_mover_lejos,
    "atacar_objetivo": accion_atacar_objetivo,
}
