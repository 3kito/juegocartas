# src/game/combate/calculadora_dano.py
"""
Calculadora de daño y defensas para el sistema de combate
"""

from typing import Tuple, Dict, Any
from src.game.cartas.carta_base import CartaBase
from src.utils.helpers import log_evento


class CalculadoraDano:
    """Maneja todos los cálculos de daño, defensas y efectos"""

    def __init__(self):
        # Configuración de fórmulas (después mover a config)
        self.DANO_MINIMO = 1
        self.FACTOR_CRITICO = 1.5
        self.PROBABILIDAD_CRITICO = 0.1  # 10%

    def calcular_dano(self, atacante: CartaBase, defensor: CartaBase,
                      tipo_ataque: str = "fisico") -> Dict[str, Any]:
        """
        Calcula el daño final considerando stats, defensas y efectos

        Returns:
            Dict con información completa del cálculo
        """
        if not atacante.esta_viva() or not defensor.esta_viva():
            return self._resultado_dano_nulo()

        # 1. Obtener daño base según tipo
        if tipo_ataque == "magico":
            dano_base = atacante.dano_magico_actual
            defensa = defensor.defensa_magica_actual
        else:  # físico
            dano_base = atacante.dano_fisico_actual
            defensa = defensor.defensa_fisica_actual

        # 2. Aplicar reducción por defensa
        dano_reducido = max(self.DANO_MINIMO, dano_base - defensa)

        # 3. Calcular crítico (opcional)
        es_critico = self._calcular_critico()
        if es_critico:
            dano_final = int(dano_reducido * self.FACTOR_CRITICO)
        else:
            dano_final = dano_reducido

        # 4. Aplicar el daño real
        dano_aplicado = defensor.recibir_dano(dano_final, tipo_ataque)

        # 5. Registrar estadísticas
        atacante.stats_combate['dano_infligido'] += dano_aplicado
        if not defensor.esta_viva():
            atacante.stats_combate['enemigos_eliminados'] += 1

        return {
            'dano_base': dano_base,
            'defensa': defensa,
            'dano_reducido': dano_reducido,
            'dano_final': dano_final,
            'dano_aplicado': dano_aplicado,
            'es_critico': es_critico,
            'tipo_ataque': tipo_ataque,
            'objetivo_eliminado': not defensor.esta_viva()
        }

    def _calcular_critico(self) -> bool:
        """Calcula si el ataque es crítico"""
        import random
        return random.random() < self.PROBABILIDAD_CRITICO

    def _resultado_dano_nulo(self) -> Dict[str, Any]:
        """Resultado cuando no se puede hacer daño"""
        return {
            'dano_base': 0,
            'defensa': 0,
            'dano_reducido': 0,
            'dano_final': 0,
            'dano_aplicado': 0,
            'es_critico': False,
            'tipo_ataque': 'ninguno',
            'objetivo_eliminado': False
        }

    def calcular_dano_habilidad(self, atacante: CartaBase, defensor: CartaBase,
                                multiplicador: float = 1.0, tipo: str = "magico") -> Dict[str, Any]:
        """Calcula daño de habilidades con multiplicador especial"""
        resultado = self.calcular_dano(atacante, defensor, tipo)

        # Aplicar multiplicador de habilidad
        if multiplicador != 1.0:
            resultado['dano_final'] = int(resultado['dano_final'] * multiplicador)
            resultado['dano_aplicado'] = defensor.recibir_dano(resultado['dano_final'], tipo)

        return resultado

    def puede_atacar(self, atacante: CartaBase, defensor: CartaBase, distancia: int) -> bool:
        """Verifica si una carta puede atacar a otra"""
        if not atacante.esta_viva() or not defensor.esta_viva():
            return False

        if not atacante.puede_actuar:
            return False

        if distancia > atacante.rango_ataque_actual:
            return False

        return True