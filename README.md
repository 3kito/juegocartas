# Juego de Cartas (Auto-battler)

Este repositorio contiene un prototipo de *auto-battler* escrito en Python. El juego se organiza en rondas que alternan una fase de preparación con una de combate. El motor principal procesa las acciones de las cartas en tiempo real.

## Estructura del proyecto

```text
.
├── README.md
├── config
│   └── tiempo_real.json
├── deprec
│   ├── ai_combate.py
│   ├── calculadora_dano.py
│   ├── combate_multiple.py
│   ├── componente_base.py
│   ├── comportamientos.py
│   ├── debug_combate.py
│   ├── estado_combate_carta.py
│   ├── gestor_ordenes.py
│   ├── manager_combates.py
│   ├── mapa_global.py
│   ├── motor_combate.py
│   └── sistema_turnos.py
├── docs
│   ├── api_reference.md
│   └── arquitectura.md
├── logs
├── main.py
├── main_simulacion.py
├── requirements.txt
├── src
│   ├── __init__.py
│   ├── __pycache__
│   ├── core
│   ├── data
│   ├── game
│   └── utils
└── tests
    ├── __init__.py
    ├── __pycache__
    ├── conftest.py
    ├── integration
    ├── simulation
    └── unitarios

16 directories, 22 files
```

Dentro de `src/` se encuentra el código fuente del juego:

```text
src
├── __init__.py
├── __pycache__
├── core
│   ├── __init__.py
│   ├── __pycache__
│   ├── jugador.py
│   └── motor_juego.py
├── data
│   ├── __init__.py
│   ├── __pycache__
│   ├── cartas
│   └── config
├── game
│   ├── __init__.py
│   ├── __pycache__
│   ├── cartas
│   ├── combate
│   ├── economia
│   ├── fases
│   ├── tablero
│   └── tienda
└── utils
    ├── __init__.py
    ├── __pycache__
    └── helpers.py

18 directories, 9 files
```

## Motor y flujo de ejecución

El archivo `src/game/combate/motor/motor_tiempo_real.py` implementa el motor que procesa continuamente los componentes activos. El método `_loop_principal` mantiene un bucle en un hilo separado y regula el FPS objetivo:

```python
    def _loop_principal(self):
        """Loop principal del motor (ejecutado en hilo separado)"""
        log_evento(f"🔄 Loop principal iniciado (Objetivo: {self.fps_objetivo} FPS)")
        try:
            while self.ejecutando:
                inicio_tick = time.time()
                if not self.pausado:
                    self._procesar_tick()
                else:
                    # Si está pausado, esperar un poco y continuar
                    time.sleep(0.1)
                    continue
                # Control de frame rate
                tiempo_procesamiento = time.time() - inicio_tick
                tiempo_espera = max(0, self.intervalo_tick - tiempo_procesamiento)
                if tiempo_espera > 0:
                    time.sleep(tiempo_espera)
                # Actualizar estadísticas de FPS
                self._actualizar_fps()
        except Exception as e:
            log_evento(f"❌ Error en loop principal: {e}")
            self.estado = EstadoMotor.ERROR
        log_evento("🏁 Loop principal terminado")
```

Cada tick llama a `_procesar_componentes` y `_procesar_eventos` para que las cartas y acciones se resuelvan:

```python
    def _procesar_tick(self):
        """Procesa un tick completo del sistema"""
        tiempo_actual = time.time()
        delta_time = tiempo_actual - self.ultimo_tick
        self.ultimo_tick = tiempo_actual
        # Procesar componentes activos
        self._procesar_componentes(delta_time)
        # Procesar eventos programados
        self._procesar_eventos()
        # Actualizar contadores
        self.total_ticks += 1
        self.stats['ticks_procesados'] += 1
```

`MotorJuego` coordina la transición entre fases y espera a que el motor de tiempo real termine antes de volver a la preparación:

```python
    def iniciar_fase_enfrentamiento(self):
        self._ejecutar_fase_combate()
```

En la simulación (`main_simulacion.py`) un bucle principal avanza de ronda mientras quede más de un jugador con vida:

```python
    while len(motor.jugadores_vivos) > 1 and motor.ronda <= ronda_maxima:
        ronda = motor.ronda
        log_evento(f"\n{'=' * 60}")
        log_evento(f"🎯 RONDA {ronda} - {len(motor.jugadores_vivos)} jugadores vivos")
        ...
```

Los jugadores tienen un método para subir de nivel automáticamente utilizando un ciclo `while`:

```python
    def intentar_subir_nivel_automatico(self):
        """Intenta subir de nivel automáticamente si es posible"""
        niveles_subidos = 0
        while self.puede_subir_nivel():
            self.subir_nivel()
            niveles_subidos += 1
        return niveles_subidos
```

Estos bucles coordinados permiten que el juego avance por rondas ejecutando acciones en tiempo real y actualizando el estado de cada jugador.

