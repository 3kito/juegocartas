# Formato de configuracion de comportamientos

Los comportamientos de movimiento y combate se definen en
`src/game/comportamientos/behaviors_config.json`.
Cada grupo (`movements` o `combats`) contiene un diccionario donde la clave es el
nombre del comportamiento y el valor una lista de **steps**.

Un step puede tener los campos:
- `condition`: nombre de una condicion basica definida en
  `behavior_primitives.CONDITIONS`.
- `action`: nombre de una accion basica definida en
  `behavior_primitives.ACTIONS`.

Las condiciones se evaluan antes de ejecutar la accion. Todas las acciones
reciben `(carta, tablero, info_entorno)` y pueden devolver interacciones.

Ejemplo simplificado:
```json
{
  "movements": {
    "explorador": {"steps": [{"action": "mover_aleatorio"}]}
  },
  "combats": {
    "agresivo": {
      "steps": [
        {"condition": "enemigo_en_rango", "action": "atacar_objetivo"},
        {"condition": "enemigo_visible", "action": "mover_hacia_enemigo"}
      ]
    }
  }
}
```
