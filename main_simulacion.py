import random
import time
from src.core.jugador import Jugador
from src.core.motor_juego import MotorJuego
from src.utils.helpers import log_evento


def crear_jugador_mock(id_: int, nombre: str) -> Jugador:
    """Crea un jugador mock para la simulación"""
    j = Jugador(id_, nombre)
    j.vida = 100
    j.oro = 20  # Más oro inicial para poder comprar
    j.nivel = 3  # Nivel intermedio para mejores probabilidades
    return j


def simular_compras_tienda_privada(motor, jugadores):
    """Simula compras en tiendas privadas de cada jugador"""
    log_evento("🛒 === FASE: COMPRAS EN TIENDAS PRIVADAS ===")

    for jugador in jugadores:
        tienda = motor.get_tienda_para(jugador.id)
        if not tienda:
            log_evento(f"❌ {jugador.nombre} no tiene tienda disponible")
            continue

        log_evento(f"🛒 {jugador.nombre} revisa su tienda privada (Oro disponible: {jugador.oro}):")
        cartas_disponibles = tienda.mostrar_cartas()

        if not cartas_disponibles:
            log_evento(f"   📭 Tienda vacía para {jugador.nombre}")
            continue

        for carta_info in cartas_disponibles:
            log_evento(f"   {carta_info}")

        # Simular compra de 1-3 cartas si tiene oro y espacio
        compras_intentadas = 0
        max_compras = min(3, len(tienda.cartas_disponibles))

        while compras_intentadas < max_compras and jugador.oro > 0 and jugador.puede_guardar_carta_en_banco():
            # Estrategia: Comprar carta más barata disponible
            carta_mas_barata_idx = None
            precio_menor = float('inf')

            for i, carta in enumerate(tienda.cartas_disponibles):
                if carta.costo <= jugador.oro and carta.costo < precio_menor:
                    carta_mas_barata_idx = i
                    precio_menor = carta.costo

            if carta_mas_barata_idx is not None:
                carta_nombre = tienda.cartas_disponibles[carta_mas_barata_idx].nombre
                resultado = tienda.comprar_carta(carta_mas_barata_idx)
                log_evento(f"🛍️ {jugador.nombre} intenta comprar '{carta_nombre}': {resultado}")
                compras_intentadas += 1
            else:
                log_evento(f"💸 {jugador.nombre} no puede permitirse más cartas")
                break

        # Mostrar estado final del jugador
        log_evento(
            f"   💰 {jugador.nombre} termina con {jugador.oro} oro, {jugador.contar_cartas_banco()} cartas en banco")

        # Ocasionalmente hacer reroll si tiene tokens
        if jugador.tokens_reroll > 0 and random.random() < 0.3:  # 30% chance
            resultado_reroll = tienda.hacer_reroll()
            log_evento(f"🔄 {jugador.nombre}: {resultado_reroll}")


def simular_ofertas_subasta(sistema_subastas, jugadores):
    """Simula ofertas en la subasta pública"""
    log_evento("🏛️ === FASE: SUBASTAS PÚBLICAS ===")

    if not sistema_subastas.cartas_subastadas:
        log_evento("📭 No hay cartas en subasta esta ronda")
        return

    # Mostrar estado inicial de la subasta
    estado_subasta = sistema_subastas.ver_estado_actual()
    log_evento("🏛️ Cartas disponibles en subasta:")
    for carta_info in estado_subasta:
        log_evento(f"   {carta_info}")

    # Simular ofertas por cada carta
    for carta_id, data in sistema_subastas.cartas_subastadas.items():
        carta_nombre = data['carta'].nombre
        carta_tier = data['carta'].tier

        log_evento(f"💰 Iniciando ofertas por '{carta_nombre}' (Tier {carta_tier}):")

        # Jugadores interesados (no todos ofertan por todas las cartas)
        jugadores_interesados = [j for j in jugadores if j.oro > data['carta'].costo and random.random() < 0.7]

        if not jugadores_interesados:
            log_evento(f"   😴 Nadie está interesado en '{carta_nombre}'")
            continue

        # Simular rondas de ofertas
        for ronda_oferta in range(1, 4):  # Máximo 3 rondas de ofertas
            ofertas_esta_ronda = []

            for jugador in jugadores_interesados:
                # Calcular oferta basada en tier de la carta y oro disponible
                oferta_base = data['carta'].costo + (carta_tier * 2)
                oferta_maxima = min(jugador.oro, oferta_base + random.randint(0, 10))

                # Solo ofertar si supera la oferta actual
                if oferta_maxima > data['mejor_oferta'] and random.random() < 0.6:  # 60% chance de ofertar
                    ofertas_esta_ronda.append((jugador, oferta_maxima))

            # Procesar ofertas de esta ronda
            if ofertas_esta_ronda:
                # Ordenar por monto (mayor primero)
                ofertas_esta_ronda.sort(key=lambda x: x[1], reverse=True)

                for jugador, monto in ofertas_esta_ronda:
                    resultado = sistema_subastas.ofertar(jugador, carta_id, monto)
                    log_evento(f"   🤝 {jugador.nombre} oferta {monto} oro: {resultado}")

                    # Si la oferta fue exitosa, otros jugadores pueden decidir no continuar
                    if "✅" in resultado:
                        # Remover jugadores que no pueden/quieren superar esta oferta
                        jugadores_interesados = [
                            j for j in jugadores_interesados
                            if j != jugador and j.oro > monto + 2 and random.random() < 0.4
                        ]
                        break
            else:
                log_evento(f"   💤 Nadie oferta en ronda {ronda_oferta} por '{carta_nombre}'")
                break

            # Si no quedan jugadores interesados, terminar ofertas para esta carta
            if not jugadores_interesados:
                break

    # Resolver todas las subastas
    log_evento("🔨 Resolviendo subastas...")
    sistema_subastas.resolver_subastas()


def simular_posicionamiento_tablero(jugadores):
    """Simula el posicionamiento de cartas en tableros individuales"""
    log_evento("📋 === FASE: POSICIONAMIENTO EN TABLEROS ===")

    for jugador in jugadores:
        if jugador.contar_cartas_banco() == 0:
            log_evento(f"📭 {jugador.nombre} no tiene cartas para posicionar")
            continue

        log_evento(f"📋 {jugador.nombre} posiciona sus cartas:")
        log_evento(f"   Cartas en banco: {jugador.contar_cartas_banco()}")
        log_evento(
            f"   Espacios disponibles en tablero: {jugador.obtener_max_cartas_tablero() - jugador.contar_cartas_tablero()}")

        # Mover cartas del banco al tablero hasta llenar el límite
        cartas_posicionadas = 0
        while (jugador.puede_colocar_carta_en_tablero() and
               jugador.contar_cartas_banco() > 0):

            # Tomar la primera carta del banco
            carta = jugador.sacar_carta_del_banco(0)
            if carta:
                exito = jugador.colocar_carta_en_tablero(carta)
                if exito:
                    cartas_posicionadas += 1
                    log_evento(f"   ✅ '{carta.nombre}' posicionada en tablero")
                else:
                    # Si falló, devolver al banco
                    jugador.agregar_carta_al_banco(carta)
                    break

        log_evento(
            f"   📊 {jugador.nombre}: {cartas_posicionadas} cartas posicionadas, {jugador.contar_cartas_banco()} quedan en banco")


def mostrar_resumen_ronda(jugadores, ronda):
    """Muestra un resumen del estado de todos los jugadores al final de la ronda"""
    log_evento(f"📊 === RESUMEN FINAL RONDA {ronda} ===")

    for jugador in jugadores:
        estado = jugador.obtener_resumen_estado()
        log_evento(f"👤 {jugador.nombre}:")
        log_evento(f"   💚 Vida: {estado['vida']}")
        log_evento(f"   💰 Oro: {estado['oro']}")
        log_evento(f"   📈 Nivel: {estado['nivel']} (Exp: {jugador.experiencia})")
        log_evento(f"   🃏 Cartas: {estado['cartas_tablero']} en tablero, {estado['cartas_banco']} en banco")
        log_evento(f"   🎫 Tokens reroll: {estado['tokens_reroll']}")


def simular_juego():
    """Función principal de simulación del juego"""
    log_evento("🎮 === INICIANDO SIMULACIÓN DE AUTO-BATTLER ===")

    # Crear jugadores con nombres históricos
    nombres_jugadores = ["Napoleón Bonaparte", "Marie Curie", "Leonardo da Vinci", "Cleopatra"]
    jugadores = [crear_jugador_mock(i + 1, nombre) for i, nombre in
                 enumerate(nombres_jugadores[:2])]  # Empezar con 2 jugadores

    log_evento(f"👥 Jugadores creados: {[j.nombre for j in jugadores]}")

    # Inicializar motor con jugadores
    motor = MotorJuego(jugadores)
    motor.iniciar()

    # Loop principal del juego
    ronda_maxima = 10  # Límite de seguridad

    while len(motor.jugadores_vivos) > 1 and motor.ronda <= ronda_maxima:
        ronda = motor.ronda
        log_evento(f"\n{'=' * 60}")
        log_evento(f"🎯 RONDA {ronda} - {len(motor.jugadores_vivos)} jugadores vivos")
        log_evento(f"{'=' * 60}")

        # Mostrar estado inicial de jugadores
        for jugador in motor.jugadores_vivos:
            log_evento(f"🎮 {jugador.nombre}: {jugador.vida} vida, {jugador.oro} oro, nivel {jugador.nivel}")

        # === FASE DE PREPARACIÓN ===
        log_evento(f"\n📦 === FASE DE PREPARACIÓN (RONDA {ronda}) ===")

        # 1. Compras en tienda privada
        if hasattr(motor, "controlador_preparacion"):
            simular_compras_tienda_privada(motor, motor.jugadores_vivos)

            # 2. Ofertas en subasta pública
            if motor.controlador_preparacion.subastas:
                simular_ofertas_subasta(motor.controlador_preparacion.subastas, motor.jugadores_vivos)

            # 3. Posicionamiento en tableros
            simular_posicionamiento_tablero(motor.jugadores_vivos)

            # 4. Dar algunos tokens de reroll aleatoriamente
            for jugador in motor.jugadores_vivos:
                if random.random() < 0.4:  # 40% chance
                    tokens = random.randint(1, 2)
                    jugador.ganar_tokens_reroll(tokens)

            # 5. Finalizar fase de preparación
            log_evento("⏭️ Finalizando fase de preparación...")
            motor.controlador_preparacion.finalizar_fase()

        # === FASE DE ENFRENTAMIENTO ===
        log_evento(f"\n⚔️ === FASE DE ENFRENTAMIENTO (RONDA {ronda}) ===")
        log_evento("🤖 Los jugadores entran en combate automático...")

        # Esperar un poco para simular el combate
        time.sleep(0.5)

        # El combate se resuelve automáticamente en el motor
        # Cuando termine, continuará con la siguiente ronda o terminará el juego

        # Mostrar resumen de la ronda
        mostrar_resumen_ronda(motor.jugadores_vivos, ronda)

        # Pequeña pausa entre rondas
        time.sleep(1)

    # === FINAL DEL JUEGO ===
    log_evento(f"\n🏁 === JUEGO TERMINADO ===")

    if len(motor.jugadores_vivos) == 1:
        ganador = motor.jugadores_vivos[0]
        log_evento(f"🏆 ¡{ganador.nombre} es el GANADOR!")
        log_evento(f"   📊 Stats finales del ganador:")
        log_evento(f"      💚 Vida: {ganador.vida}/{ganador.vida_maxima}")
        log_evento(f"      📈 Nivel alcanzado: {ganador.nivel}")
        log_evento(f"      🃏 Cartas totales: {ganador.contar_cartas_total()}")
        log_evento(f"      ⚔️ Combates ganados: {ganador.stats_partida['combates_ganados']}")
    elif len(motor.jugadores_vivos) == 0:
        log_evento("💀 Todos los jugadores fueron eliminados. ¡EMPATE!")
    else:
        log_evento(f"⏰ Juego terminado por límite de rondas ({ronda_maxima})")
        supervivientes = [j.nombre for j in motor.jugadores_vivos]
        log_evento(f"🎖️ Supervivientes: {supervivientes}")

    log_evento("✅ Simulación completada exitosamente")


if __name__ == "__main__":
    try:
        simular_juego()
    except KeyboardInterrupt:
        log_evento("⏹️ Simulación interrumpida por el usuario")
    except Exception as e:
        log_evento(f"❌ Error durante la simulación: {e}")
        import traceback

        traceback.print_exc()