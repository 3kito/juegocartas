"""
TiendaIndividual - Sistema de tienda privada por jugador durante la fases de preparación
"""

from typing import List, Optional
from src.game.cards.card_manager import card_manager
from src.game.cards.card_fusion import apply_fusions
from src.utils.helpers import log_evento


class TiendaIndividual:
    def __init__(self, jugador, cantidad_cartas: int = 5):
        self.jugador = jugador
        self.cantidad_cartas = cantidad_cartas
        self.cartas_disponibles: List = []
        self.generar_tienda()

    def generar_tienda(self):
        """Genera nuevas cartas según el nivel del jugador"""
        # Devolver cartas actuales al pool
        for carta in self.cartas_disponibles:
            card_manager.devolver_carta_al_pool(carta)

        self.cartas_disponibles = card_manager.obtener_cartas_aleatorias_por_nivel(
            nivel_jugador=self.jugador.nivel,
            cantidad=self.cantidad_cartas
        )

        # NUEVO: Log detallado de las cartas en tienda
        log_evento(f"🛒 {self.jugador.nombre} recibe {len(self.cartas_disponibles)} cartas nuevas en tienda")
        for i, carta in enumerate(self.cartas_disponibles):
            log_evento(f"   [{i}] {carta.nombre} (Tier {carta.tier}, {carta.costo} oro)")

    def mostrar_cartas(self) -> List[str]:
        """Devuelve las cartas disponibles en formato resumido"""
        return [f"[{i}] {carta.nombre} - Tier {carta.tier} - Costo: {carta.costo}"
                for i, carta in enumerate(self.cartas_disponibles)]

    def comprar_carta(self, indice: int) -> Optional[str]:
        """Intenta comprar una carta específica"""
        if indice < 0 or indice >= len(self.cartas_disponibles):
            return "❌ Índice inválido"

        carta = self.cartas_disponibles[indice]

        if not self.jugador.puede_gastar_oro(carta.costo):
            return "❌ No tienes suficiente oro"

        if not self.jugador.puede_guardar_carta_en_banco():
            return "❌ Banco lleno"

        self.jugador.gastar_oro(carta.costo, f"compra {carta.nombre}")
        self.jugador.agregar_carta_al_banco(carta)
        self.cartas_disponibles.pop(indice)

        eventos = apply_fusions(self.jugador.tablero, self.jugador.cartas_banco)
        for ev in eventos:
            log_evento(f"🔧 {ev}")

        mensaje = f"✅ {carta.nombre} comprada"
        if eventos:
            mensaje += " | " + " | ".join(eventos)
        return mensaje

    def hacer_reroll(self) -> Optional[str]:
        """Usa un token para refrescar los espacios vacíos de la tienda"""
        if not self.jugador.usar_token_reroll():
            return "❌ No tienes tokens de reroll"

        # Devolver al pool las cartas que no fueron compradas
        for carta in self.cartas_disponibles:
            card_manager.devolver_carta_al_pool(carta)

        # Vaciar la tienda
        self.cartas_disponibles.clear()

        # Rellenar hasta cantidad máxima
        self.rellenar_tienda()
        return f"🔄 Tienda actualizada con nuevas cartas"

    def rellenar_tienda(self):
        """Genera nuevas cartas para llenar los espacios faltantes"""
        faltantes = self.cantidad_cartas - len(self.cartas_disponibles)
        nuevas = card_manager.obtener_cartas_aleatorias_por_nivel(
            nivel_jugador=self.jugador.nivel,
            cantidad=faltantes
        )
        self.cartas_disponibles.extend(nuevas)
        log_evento(f"🛒 {self.jugador.nombre} recibe {faltantes} cartas nuevas en tienda")
