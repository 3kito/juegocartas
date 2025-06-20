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

def _puede_generar_movimiento(carta) -> bool:
    """Evita encadenar movimientos ignorando la velocidad."""
    return not (
        carta.tiene_orden_manual()
        or carta.tiene_orden_simulada()
        or carta.tiene_evento_activo("movimiento")
        or (
            carta.orden_actual is not None
            and carta.orden_actual.get("progreso") == "ejecutando"
        )
    )


def accion_mover_aleatorio(carta, tablero, info_entorno):
    if not _puede_generar_movimiento(carta):
        return []
    libres = tablero.coordenadas_libres()
    if not libres or carta.coordenada is None:
        return []
    destino = random.choice(libres)
    carta.marcar_orden_simulada("mover", destino)
    return []


def accion_mover_hacia_enemigo(carta, tablero, info_entorno):
    if not _puede_generar_movimiento(carta):
        return []
    enemigos = info_entorno.get("enemigos_en_rango") or info_entorno.get("enemigos", [])
    if not enemigos:
        return []
    objetivo = enemigos[0]
    carta.marcar_orden_simulada("mover", objetivo.coordenada)
    return []


def accion_mover_lejos(carta, tablero, info_entorno):
    if not _puede_generar_movimiento(carta):
        return []
    enemigos = info_entorno.get("enemigos_en_rango")
    if not enemigos or carta.coordenada is None:
        return []
    origen = carta.coordenada
    opciones = [c for c in origen.vecinos() if tablero.esta_dentro_del_tablero(c) and tablero.esta_vacia(c)]
    opciones.sort(key=lambda c: c.distancia(enemigos[0].coordenada), reverse=True)
    if opciones:
        carta.marcar_orden_simulada("mover", opciones[0])
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
