from src.game.combate.ia.ia_comportamiento import decidir_comportamiento


class CartaDummy:
    def __init__(self, vida_actual, vida_maxima):
        self.vida_actual = vida_actual
        self.vida_maxima = vida_maxima

def test_decision_atacar():
    carta = CartaDummy(vida_actual=100, vida_maxima=100)
    entorno = {"enemigos_en_rango": [object()]}
    decision = decidir_comportamiento(carta, entorno)
    assert decision["accion"] == "atacar", f"Esperado 'atacar', recibido: {decision['accion']}"

def test_decision_huir():
    carta = CartaDummy(vida_actual=10, vida_maxima=100)
    entorno = {"enemigos_en_rango": [object()]}
    decision = decidir_comportamiento(carta, entorno)
    assert decision["accion"] == "huir", f"Esperado 'huir', recibido: {decision['accion']}"

def test_decision_esperar():
    carta = CartaDummy(vida_actual=100, vida_maxima=100)
    entorno = {"enemigos_en_rango": []}
    decision = decidir_comportamiento(carta, entorno)
    assert decision["accion"] == "esperar", f"Esperado 'esperar', recibido: {decision['accion']}"

if __name__ == "__main__":
    test_decision_atacar()
    test_decision_huir()
    test_decision_esperar()
    print("✅ Todos los tests unitarios de IA pasaron correctamente.")
