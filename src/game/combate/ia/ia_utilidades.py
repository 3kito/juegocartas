# ia_utilidades.py
from src.utils.helpers import log_evento

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
    aliados = []

    if coord:
        for otra_coord, otra_carta in tablero.obtener_cartas_en_rango(coord, carta.rango_ataque_actual):
            if otra_carta:
                if carta.es_aliado_de(otra_carta):
                    aliados.append(otra_carta)
                else:
                    enemigos.append(otra_carta)

    return {
        "coordenada_actual": coord,
        "enemigos_en_rango": enemigos,
        "aliados": aliados
    }


def calcular_vision_jugador(jugador, mapa_global):
    """Calcula las celdas visibles para un jugador"""
    celdas_visibles = set()

    # Zonas siempre visibles por color
    # Todas las zonas deben ser visibles sin importar el color
    zonas = mapa_global.zonas_rojas + mapa_global.zonas_azules
    for zona in zonas:
        celdas_visibles.update(zona.coordenadas)

    # Visibilidad desde cartas propias en el mapa global
    for coord, carta in mapa_global.tablero.celdas.items():
        if carta is not None and getattr(carta, "duenio", None) == jugador:
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


def mover_carta_con_pathfinding(
    carta, destino, mapa, motor=None, on_step=None, on_finish=None
):
    """Mueve la carta paso a paso usando pathfinding.

    Si se proporciona ``motor`` los pasos se ejecutan con delay usando
    :meth:`MotorTiempoReal.programar_evento` respetando la velocidad de
    movimiento de la carta. Devuelve ``True`` si se encontró una ruta.
    """

    origen = mapa.obtener_coordenada_de(carta)
    if origen is None:
        log_evento(f"❌ No se encontró coordenada de {carta.nombre}", "DEBUG")
        if on_finish:
            on_finish()
        return False, "sin_origen"

    # Al iniciar un movimiento cancelamos eventos de ataque previos
    if motor is not None:
        try:
            carta.cancelar_evento_activo("ataque", motor)
            carta.cancelar_evento_activo("movimiento", motor)
        except AttributeError:
            pass

    log_evento(
        f"🚶 INICIANDO pathfinding {carta.nombre}: {origen} → {destino}", "DEBUG"
    )
    log_evento(
        f"🧭 Buscando ruta para {carta.nombre}: {origen} → {destino}", "DEBUG"
    )
    ruta = _buscar_ruta(mapa, origen, destino)
    if not ruta:
        log_evento("⚠️ Ruta no encontrada", "DEBUG")
        if on_finish:
            on_finish()
        return False, "sin_ruta"

    log_evento(
        f"🗺️ Ruta encontrada: {len(ruta)} pasos",
        "DEBUG",
    )
    log_evento(
        f"🚶 {carta.nombre} se mueve {origen} → {destino} ({len(ruta)} pasos)",
        "DEBUG",
    )

    if motor is None:
        for paso in ruta:
            mapa.mover_carta(origen, paso)
            origen = paso
            if on_step:
                on_step()
        if on_finish:
            on_finish()
        return True, "ok"

    delay = max(0.1, 1.0 / max(0.01, getattr(carta, "velocidad_movimiento", 1.0)))
    def _programar_paso(indice: int):
        if indice >= len(ruta):
            carta.eventos_activos.pop("movimiento", None)
            if on_finish:
                on_finish()
            return

        paso = ruta[indice]

        def _ejecutar():
            actual = mapa.obtener_coordenada_de(carta)
            log_evento(f"➡️ {carta.nombre} paso a {paso}", "DEBUG")
            mapa.mover_carta(actual, paso)
            if on_step:
                on_step()
            _programar_paso(indice + 1)

        log_evento(
            f"⏰ Programando evento movimiento con delay {delay:.2f}s",
            "DEBUG",
        )
        # Programar cada paso respetando siempre la velocidad de movimiento
        # Anteriormente el primer paso se ejecutaba sin demora, lo que hacía
        # que en comportamientos automáticos la velocidad configurada no se
        # respetara visualmente.
        evt_id = motor.programar_evento(_ejecutar, delay)
        try:
            carta.registrar_evento_activo("movimiento", evt_id)
        except AttributeError:
            pass

    _programar_paso(0)
    return True, "ok"


def atacar_si_en_rango(carta_atacante, carta_objetivo):
    """Realiza un ataque simple si el objetivo está en rango"""
    if carta_atacante.coordenada is None or carta_objetivo.coordenada is None:
        return False
    if carta_atacante.coordenada.distancia(carta_objetivo.coordenada) > carta_atacante.rango_ataque_actual:
        return False
    from src.game.combate.interacciones.interaccion_modelo import Interaccion, TipoInteraccion
    from src.game.combate.calcular_dano.calculadora_dano import calcular_dano

    inter = Interaccion(
        fuente_id=carta_atacante.id,
        objetivo_id=carta_objetivo.id,
        tipo=TipoInteraccion.ATAQUE,
        metadata={"dano_base": carta_atacante.dano_fisico_actual},
    )

    dano = calcular_dano(carta_atacante, carta_objetivo, inter)
    aplicado = carta_objetivo.recibir_dano(dano)
    carta_atacante.registrar_ataque()

    log_evento(
        f"⚔️ {carta_atacante.nombre} golpea a {carta_objetivo.nombre} por {aplicado} daño (vida restante: {carta_objetivo.vida_actual})"
    )

    if not carta_objetivo.esta_viva():
        carta_atacante.stats_combate["enemigos_eliminados"] += 1
    carta_atacante.stats_combate["dano_infligido"] += aplicado
    return True


def iniciar_ataque_continuo(atacante, objetivo, mapa, motor, on_step=None, on_finish=None):
    """Ejecuta ataques automáticos mientras el objetivo esté vivo y visible.

    ``on_step`` es una función opcional que se llamará tras cada acción para
    permitir que la interfaz se actualice en tiempo real.
    """

    try:
        atacante.cancelar_evento_activo("movimiento", motor)
        atacante.cancelar_evento_activo("ataque", motor)
    except AttributeError:
        pass

    def _ciclo():
        if not atacante.esta_viva() or not objetivo.esta_viva():
            try:
                atacante.cancelar_evento_activo("ataque", motor)
            except AttributeError:
                pass
            if on_finish:
                on_finish()
            return

        if atacante.coordenada is None or objetivo.coordenada is None:
            try:
                atacante.cancelar_evento_activo("ataque", motor)
            except AttributeError:
                pass
            if on_finish:
                on_finish()
            return

        distancia = atacante.coordenada.distancia(objetivo.coordenada)
        if distancia > atacante.rango_ataque_actual:
            log_evento(
                f"📍 Acercando {atacante.nombre} hacia {objetivo.nombre}",
                "DEBUG",
            )
            mover_carta_con_pathfinding(
                atacante, objetivo.coordenada, mapa, motor, on_step=on_step
            )
            evt = motor.programar_evento(_ciclo, atacante.velocidad_ataque)
            try:
                atacante.registrar_evento_activo("ataque", evt)
            except AttributeError:
                pass
            return

        if distancia <= atacante.rango_ataque_actual:
            atacar_si_en_rango(atacante, objetivo)
            if on_step:
                try:
                    on_step()
                except TypeError:
                    on_step()

        if objetivo.esta_viva():
            evt = motor.programar_evento(_ciclo, atacante.velocidad_ataque)
            try:
                atacante.registrar_evento_activo("ataque", evt)
            except AttributeError:
                pass

    log_evento(
        f"⏳ Iniciando ataque continuo de {atacante.nombre} a {objetivo.nombre}",
        "DEBUG",
    )
    evt_inicio = motor.programar_evento(_ciclo, 0.0)
    try:
        atacante.registrar_evento_activo("ataque", evt_inicio)
    except AttributeError:
        pass


