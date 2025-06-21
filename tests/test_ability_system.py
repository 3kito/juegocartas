import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.game.cards.base_card import Ability


def test_ability_por_usos():
    datos = {
        'nombre': 'Disparo',
        'tipo': 'activa',
        'cooldown': 3,
        'cooldown_tipo': 'por_usos',
        'max_usos': 2
    }
    abil = Ability(datos)
    assert abil.can_use(1)
    abil.use(1)
    assert abil.can_use(1)
    abil.use(1)
    assert not abil.can_use(1)
    for _ in range(3):
        abil.reducir_cooldown()
    assert abil.can_use(2)


def test_ability_por_turno():
    abil = Ability({'nombre': 'Golpe', 'tipo': 'activa', 'cooldown_tipo': 'por_turno'})
    assert abil.can_use(1)
    abil.use(1)
    assert not abil.can_use(1)
    assert abil.can_use(2)


def test_pasiva_cada_turno():
    from src.game.cards.base_card import BaseCard
    datos = {
        'id': 1,
        'stats': {'vida': 10},
        'habilidades': [
            {
                'nombre': 'Regeneracion',
                'tipo': 'pasiva',
                'trigger': 'cada_turno',
                'efectos': [{'tipo': 'curacion', 'cantidad': 2}]
            }
        ]
    }
    carta = BaseCard(datos)
    carta.vida_actual = 5
    carta.iniciar_turno()
    assert carta.vida_actual == 7


def test_pasiva_al_recibir_dano():
    from src.game.cards.base_card import BaseCard
    datos = {
        'id': 2,
        'stats': {'vida': 10, 'mana_maxima': 20, 'mana_inicial': 0},
        'habilidades': [
            {
                'nombre': 'Concentracion',
                'tipo': 'pasiva',
                'trigger': 'al_recibir_dano',
                'efectos': [{'tipo': 'mana', 'cantidad': 5}]
            }
        ]
    }
    carta = BaseCard(datos)
    carta.recibir_dano(3)
    assert carta.mana_actual == 5
