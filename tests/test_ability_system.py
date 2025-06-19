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
