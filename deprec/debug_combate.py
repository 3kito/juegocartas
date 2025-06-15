import time
import sys
import os

# Detectar automáticamente la raíz del proyecto
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir

# Buscar hacia arriba hasta encontrar la carpeta 'src'
while project_root and not os.path.exists(os.path.join(project_root, 'src')):
    parent = os.path.dirname(project_root)
    if parent == project_root:  # Llegamos al tope del filesystem
        break
    project_root = parent

# Agregar la raíz del proyecto al path
if project_root and os.path.exists(os.path.join(project_root, 'src')):
    sys.path.insert(0, project_root)
    print(f"🔧 Project root encontrado: {project_root}")
else:
    print("❌ No se pudo encontrar la raíz del proyecto")
    sys.exit(1)

from src.game.combate.motor.motor_tiempo_real import MotorTiempoReal
from deprec.combate_multiple import CombateMultiple
from src.game.cartas.carta_base import CartaBase


def crear_carta_test(id_carta: int, nombre: str, vida: int = 100, dano: int = 20) -> CartaBase:
    datos_carta = {
        'id': id_carta, 'nombre': nombre, 'tier': 1,
        'stats': {'vida': vida, 'dano_fisico': dano, 'defensa_fisica': 5}
    }
    return CartaBase(datos_carta)


print("🧪 Test de debug del combate")

# Crear cartas
carta_a = crear_carta_test(1, "A", vida=80, dano=25)
carta_b = crear_carta_test(2, "B", vida=70, dano=30)

print(f"Carta A: {carta_a.vida_actual} vida")
print(f"Carta B: {carta_b.vida_actual} vida")

# Crear combate
combate = CombateMultiple("debug_combate")
combate.agregar_carta(carta_a)
combate.agregar_carta(carta_b)

print(f"Cartas en combate: {len(combate.cartas_combate)}")

# Crear motor
motor = MotorTiempoReal(fps_objetivo=10)
print("Motor creado")

# Agregar combate al motor
resultado_agregar = motor.agregar_componente(combate)
print(f"Combate agregado al motor: {resultado_agregar}")

print("Iniciando motor...")
motor.iniciar()

print("Esperando 0.5s para que motor inicie completamente...")
time.sleep(0.5)

print("Programando ataques...")
resultado1 = combate.ordenar_ataque(1, 2)
resultado2 = combate.ordenar_ataque(2, 1)

print(f"Ataques programados: {resultado1}, {resultado2}")
print(f"Ataques en cola: {len(combate.ataques_programados)}")

# Mostrar detalles de ataques programados
for i, ataque in enumerate(combate.ataques_programados):
    print(f"  Ataque {i + 1}: {ataque.atacante_id} → {ataque.objetivo_id} en {ataque.tiempo_ejecucion}")

print("Esperando 5 segundos...")
for i in range(5):
    time.sleep(1)

    # Mostrar estado detallado
    print(f"Segundo {i + 1}:")
    print(f"  A vida: {carta_a.vida_actual}")
    print(f"  B vida: {carta_b.vida_actual}")
    print(f"  Ataques pendientes: {len(combate.ataques_programados)}")
    print(f"  Ataques ejecutados: {combate.total_ataques_ejecutados}")

    # Verificar si el combate sigue activo
    componentes_activos = motor.obtener_componentes_activos()
    print(f"  Combate activo en motor: {'debug_combate' in componentes_activos}")

motor.detener()
print("Test terminado")