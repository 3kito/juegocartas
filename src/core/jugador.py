"""
Clase Jugador - Representa a un jugador en el auto-battler
"""

from src.utils.helpers import log_evento, validar_rango
from src.game.tablero.tablero_hexagonal import TableroHexagonal


class Jugador:
    def __init__(self, id_jugador, nombre="Jugador"):
        # Identificación
        self.id = id_jugador
        self.nombre = nombre

        # Stats básicos
        self.vida_maxima = 100
        self.vida = self.vida_maxima
        self.oro = 10
        self.nivel = 1
        self.experiencia = 0

        # Estado del juego
        self.eliminado = False
        self.ronda_eliminacion = None

        # Tablero hexagonal individual (NUEVO)
        self.tablero = TableroHexagonal()

        # Inventario y cartas (ACTUALIZADO)
        self.cartas_banco = []  # Cartas guardadas (fuera del tablero)

        # Economía
        self.tokens_reroll = 0
        self.ofertas_activas = {}  # Para el sistema de subastas

        # Estadísticas de partida
        self.stats_partida = {
            'oro_total_ganado': 0,
            'dano_total_recibido': 0,
            'combates_ganados': 0,
            'combates_perdidos': 0,
            'cartas_compradas': 0,
            'rerolls_usados': 0
        }

        # Configuración (será cargada desde config más adelante)
        self.MAX_CARTAS_BANCO = 20
        self.COSTO_EXPERIENCIA_POR_ORO = 4
        self.color_fase_actual = None
    @property
    def cartas(self):
        return self.cartas_banco

    # === MÉTODOS DE VIDA Y ESTADO (sin cambios) ===

    def esta_vivo(self):
        """Retorna True si el jugador sigue en el juego"""
        return self.vida > 0 and not self.eliminado

    def recibir_dano(self, cantidad):
        """Aplica daño al jugador"""
        if cantidad < 0:
            cantidad = 0

        self.vida = max(0, self.vida - cantidad)
        self.stats_partida['dano_total_recibido'] += cantidad

        log_evento(f"{self.nombre} recibe {cantidad} daño (Vida: {self.vida}/{self.vida_maxima})")

    def curar(self, cantidad):
        """Cura al jugador (no puede exceder vida máxima)"""
        if cantidad < 0:
            cantidad = 0

        vida_anterior = self.vida
        self.vida = min(self.vida_maxima, self.vida + cantidad)
        cantidad_curada = self.vida - vida_anterior

        if cantidad_curada > 0:
            log_evento(f"{self.nombre} se cura {cantidad_curada} puntos (Vida: {self.vida}/{self.vida_maxima})")

    def eliminar(self, ronda_actual=None):
        """Elimina al jugador del juego"""
        if not self.eliminado:
            self.eliminado = True
            self.vida = 0
            self.ronda_eliminacion = ronda_actual
            log_evento(f"💀 {self.nombre} ha sido eliminado en la ronda {ronda_actual or 'desconocida'}")

    # === MÉTODOS DE ECONOMÍA (sin cambios) ===

    def ganar_oro(self, cantidad, razon=""):
        """Añade oro al jugador"""
        if cantidad < 0:
            cantidad = 0

        self.oro += cantidad
        self.stats_partida['oro_total_ganado'] += cantidad

        razon_texto = f" ({razon})" if razon else ""
        log_evento(f"{self.nombre} gana {cantidad} oro{razon_texto} (Total: {self.oro})")

    def gastar_oro(self, cantidad, razon=""):
        """Gasta oro del jugador si tiene suficiente"""
        if not self.puede_gastar_oro(cantidad):
            log_evento(f"❌ {self.nombre} no tiene suficiente oro para gastar {cantidad}")
            return False

        self.oro -= cantidad
        razon_texto = f" ({razon})" if razon else ""
        log_evento(f"{self.nombre} gasta {cantidad} oro{razon_texto} (Restante: {self.oro})")
        return True

    def puede_gastar_oro(self, cantidad):
        """Verifica si el jugador tiene suficiente oro"""
        return self.oro >= cantidad

    # === MÉTODOS DE EXPERIENCIA Y NIVELES (ACTUALIZADOS) ===

    def ganar_experiencia(self, cantidad):
        """Añade experiencia al jugador"""
        if cantidad < 0:
            cantidad = 0

        self.experiencia += cantidad
        log_evento(f"{self.nombre} gana {cantidad} experiencia (Total: {self.experiencia})")

    def comprar_experiencia_con_oro(self, cantidad_oro):
        """Convierte oro en experiencia"""
        if not self.puede_gastar_oro(cantidad_oro):
            return False

        experiencia_ganada = cantidad_oro // self.COSTO_EXPERIENCIA_POR_ORO
        oro_gastado = experiencia_ganada * self.COSTO_EXPERIENCIA_POR_ORO

        if experiencia_ganada > 0:
            self.gastar_oro(oro_gastado, "comprar experiencia")
            self.ganar_experiencia(experiencia_ganada)
            return True
        return False

    def puede_subir_nivel(self):
        """Verifica si el jugador puede subir de nivel"""
        costo = self.calcular_costo_siguiente_nivel()
        return self.experiencia >= costo and self.nivel < 10

    def calcular_costo_siguiente_nivel(self):
        """Calcula el costo en experiencia para subir al siguiente nivel"""
        costos = [0, 2, 6, 12, 20, 30, 42, 56, 72, 90]
        if self.nivel < len(costos):
            return costos[self.nivel]
        return 999

    def subir_nivel(self):
        """Sube el nivel del jugador si es posible"""
        if not self.puede_subir_nivel():
            return False

        costo = self.calcular_costo_siguiente_nivel()
        self.experiencia -= costo
        self.nivel += 1

        log_evento(f"🔥 {self.nombre} sube a nivel {self.nivel}! (Slots tablero: {self.obtener_max_cartas_tablero()})")
        return True

    def intentar_subir_nivel_automatico(self):
        """Intenta subir de nivel automáticamente si es posible"""
        niveles_subidos = 0
        while self.puede_subir_nivel():
            self.subir_nivel()
            niveles_subidos += 1
        return niveles_subidos

    # === MÉTODOS DE TABLERO HEXAGONAL (NUEVOS) ===

    def obtener_max_cartas_tablero(self):
        """Retorna el número máximo de cartas que puede tener en el tablero"""
        return min(10, self.nivel)  # Máximo 10, limitado por nivel

    def puede_colocar_carta_en_tablero(self):
        """Verifica si puede colocar más cartas en el tablero"""
        return self.tablero.contar_cartas() < self.obtener_max_cartas_tablero()

    def colocar_carta_en_tablero(self, carta, coordenada=None):
        """Coloca una carta en el tablero, en coordenada específica o automática"""
        if not self.puede_colocar_carta_en_tablero():
            log_evento(f"❌ {self.nombre} no puede colocar más cartas (límite: {self.obtener_max_cartas_tablero()})")
            return False

        # Si no se especifica coordenada, buscar una libre
        if coordenada is None:
            coordenadas_libres = self.tablero.obtener_coordenadas_disponibles()
            if not coordenadas_libres:
                log_evento(f"❌ {self.nombre} no tiene espacios libres en el tablero")
                return False
            coordenada = coordenadas_libres[0]  # Tomar la primera disponible

        # Intentar colocar la carta
        if self.tablero.colocar_carta(carta, coordenada):
            log_evento(f"✅ {self.nombre} coloca carta en {coordenada}")
            return True
        return False

    def mover_carta_en_tablero(self, desde, hacia):
        """Mueve una carta dentro del tablero"""
        if self.tablero.mover_carta(desde, hacia):
            log_evento(f"📦 {self.nombre} mueve carta: {desde} → {hacia}")
            return True
        return False

    def quitar_carta_del_tablero(self, coordenada):
        """Quita una carta del tablero"""
        carta = self.tablero.quitar_carta(coordenada)
        if carta:
            log_evento(f"🗑️ {self.nombre} retira carta de {coordenada}")
        return carta

    def obtener_cartas_tablero(self):
        """Retorna lista de todas las cartas en el tablero con sus coordenadas"""
        cartas = []
        for coord, carta in self.tablero.celdas.items():
            if carta is not None:
                cartas.append((coord, carta))
        return cartas

    def contar_cartas_tablero(self):
        """Cuenta las cartas actualmente en el tablero"""
        return self.tablero.contar_cartas()

    def limpiar_tablero(self):
        """Remueve todas las cartas del tablero (las devuelve al banco)"""
        cartas_removidas = []
        for coord, carta in self.tablero.celdas.items():
            if carta is not None:
                cartas_removidas.append(carta)
                self.cartas_banco.append(carta)

        self.tablero.limpiar_tablero()
        log_evento(f"🧹 {self.nombre} limpia tablero: {len(cartas_removidas)} cartas al banco")
        return cartas_removidas

    # === MÉTODOS DE BANCO (NUEVOS) ===

    def puede_guardar_carta_en_banco(self):
        """Verifica si puede guardar más cartas en el banco"""
        return len(self.cartas_banco) < self.MAX_CARTAS_BANCO

    # En src/core/jugador.py - método agregar_carta_al_banco()
    def agregar_carta_al_banco(self, carta):
        """Agrega una carta al banco"""
        if not self.puede_guardar_carta_en_banco():
            log_evento(f"❌ {self.nombre} banco lleno ({self.MAX_CARTAS_BANCO} cartas)")
            return False

        self.cartas_banco.append(carta)
        carta.duenio = self  # NUEVO: Asignar dueño
        log_evento(
            f"📦 {self.nombre} guarda '{carta.nombre}' en banco ({len(self.cartas_banco)}/{self.MAX_CARTAS_BANCO})")

        # NUEVO: Mostrar estado del banco
        if len(self.cartas_banco) <= 5:  # Solo mostrar si tiene pocas cartas
            cartas_nombres = [c.nombre for c in self.cartas_banco if c is not None]
            log_evento(f"   Banco actual: {cartas_nombres}")

        return True

    def sacar_carta_del_banco(self, indice=0):
        """Saca una carta del banco por índice"""
        if 0 <= indice < len(self.cartas_banco):
            carta = self.cartas_banco.pop(indice)
            log_evento(f"📤 {self.nombre} saca carta del banco")
            return carta
        return None

    def contar_cartas_banco(self):
        """Cuenta las cartas en el banco"""
        return len(self.cartas_banco)

    def contar_cartas_total(self):
        """Cuenta todas las cartas (tablero + banco)"""
        return self.contar_cartas_tablero() + self.contar_cartas_banco()

    # === MÉTODOS DE TOKENS Y COMBATE (sin cambios) ===

    def ganar_tokens_reroll(self, cantidad):
        """Añade tokens de reroll"""
        if cantidad < 0:
            cantidad = 0
        self.tokens_reroll += cantidad
        log_evento(f"{self.nombre} gana {cantidad} tokens de reroll (Total: {self.tokens_reroll})")

    def usar_token_reroll(self):
        """Usa un token de reroll si tiene disponible"""
        if self.tokens_reroll > 0:
            self.tokens_reroll -= 1
            self.stats_partida['rerolls_usados'] += 1
            log_evento(f"{self.nombre} usa token de reroll (Restantes: {self.tokens_reroll})")
            return True
        return False

    def registrar_victoria_combate(self):
        """Registra una victoria en combate"""
        self.stats_partida['combates_ganados'] += 1

    def registrar_derrota_combate(self):
        """Registra una derrota en combate"""
        self.stats_partida['combates_perdidos'] += 1

    def obtener_ratio_victorias(self):
        """Calcula el ratio de victorias"""
        total_combates = self.stats_partida['combates_ganados'] + self.stats_partida['combates_perdidos']
        if total_combates == 0:
            return 0.0
        return self.stats_partida['combates_ganados'] / total_combates

    # === MÉTODOS DE ESTADO Y ESTADÍSTICAS (ACTUALIZADOS) ===

    def obtener_resumen_estado(self):
        """Retorna un resumen del estado actual del jugador"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'vida': f"{self.vida}/{self.vida_maxima}",
            'oro': self.oro,
            'nivel': self.nivel,
            'experiencia': self.experiencia,
            'eliminado': self.eliminado,
            'cartas_tablero': self.contar_cartas_tablero(),
            'cartas_banco': self.contar_cartas_banco(),
            'cartas_total': self.contar_cartas_total(),
            'tokens_reroll': self.tokens_reroll,
            'max_cartas_tablero': self.obtener_max_cartas_tablero()
        }

    def obtener_stats_detalladas(self):
        """Retorna estadísticas detalladas de la partida"""
        resumen = self.obtener_resumen_estado()
        resumen['stats_partida'] = self.stats_partida.copy()
        resumen['ratio_victorias'] = self.obtener_ratio_victorias()
        resumen['ronda_eliminacion'] = self.ronda_eliminacion
        resumen['tablero_stats'] = self.tablero.obtener_estadisticas()
        return resumen

    def obtener_estado_tablero(self):
        """Retorna información detallada del tablero"""
        return {
            'cartas_colocadas': self.contar_cartas_tablero(),
            'max_cartas': self.obtener_max_cartas_tablero(),
            'espacios_libres': len(self.tablero.obtener_coordenadas_disponibles()),
            'puede_colocar_mas': self.puede_colocar_carta_en_tablero(),
            'posiciones_ocupadas': [str(coord) for coord, _ in self.obtener_cartas_tablero()]
        }

    def resetear_stats_partida(self):
        """Resetea las estadísticas de partida (útil para nuevas partidas)"""
        self.stats_partida = {
            'oro_total_ganado': 0,
            'dano_total_recibido': 0,
            'combates_ganados': 0,
            'combates_perdidos': 0,
            'cartas_compradas': 0,
            'rerolls_usados': 0
        }
        self.tablero.limpiar_tablero()
        self.cartas_banco.clear()

    def __str__(self):
        """Representación en string del jugador"""
        estado = "VIVO" if self.esta_vivo() else "ELIMINADO"
        return f"{self.nombre} (Nivel {self.nivel}, {self.vida} vida, {self.oro} oro, {self.contar_cartas_tablero()}/19 cartas) [{estado}]"

    def __repr__(self):
        """Representación para debugging"""
        return f"Jugador(id={self.id}, nombre='{self.nombre}', vida={self.vida}, oro={self.oro}, nivel={self.nivel}, cartas={self.contar_cartas_tablero()})"