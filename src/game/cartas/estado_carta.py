# cartas/estado_carta.py

from src.game.cartas.carta_base import CartaBase
from src.utils.helpers import log_evento


class EstadoCarta:
    """
    Representa el estado de combate de una carta en tiempo real.
    Mantiene información dinámica como vida actual, cooldowns, etc.
    """

    def __init__(self, carta: CartaBase):
        self.id_carta: int = carta.id
        self.nombre: str = carta.nombre
        self.carta: CartaBase = carta

        self.vida_actual: int = carta.vida_actual
        self.cooldown_ataque: float = 0.0
        self.estado: str = "activo"  # o "muerta"

        # Stats relevantes
        self.dano_base: int = carta.dano_fisico_actual
        self.defensa: int = carta.defensa_fisica_actual
        self.defensa_fisica_actual: int = carta.defensa_fisica_actual
        self.defensa_magica_actual: int = getattr(carta, 'defensa_magica_actual', 0)

    def recibir_dano(self, cantidad: int):
        """Aplica daño ya calculado al estado de la carta"""
        dano_real = max(0, cantidad)
        self.vida_actual -= dano_real
        log_evento(f"💥 {self.nombre} recibe {dano_real} de daño")

        if self.vida_actual <= 0:
            self.vida_actual = 0
            self.estado = "muerta"
            log_evento(f"☠️ {self.nombre} ha sido derrotada")

    def esta_viva(self) -> bool:
        return self.estado != "muerta"

    def puede_actuar(self) -> bool:
        return self.esta_viva() and self.cooldown_ataque <= 0.0

    def reducir_cooldowns(self, delta_time: float):
        if self.cooldown_ataque > 0:
            self.cooldown_ataque = max(0.0, self.cooldown_ataque - delta_time)

    def reiniciar_cooldown(self, velocidad_base: float = 1.5):
        self.cooldown_ataque = velocidad_base

    def __str__(self):
        return f"EstadoCarta(id={self.id_carta}, vida={self.vida_actual}, estado={self.estado})"
