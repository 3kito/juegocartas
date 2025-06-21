# Transiciones de Interfaz

## Transición: Preparación → Combate

### Duración Total: 3 segundos

### Secuencia
1. **Segundo 0-0.5**: Fade out elementos UI preparación
   - Banco de cartas desaparece
   - Tienda se oculta
   - Panel subastas se cierra

2. **Segundo 0.5-1.5**: Efecto visual principal
   - Cámara se aleja del tablero personal
   - Efecto de "portal" o "zoom out" estilo TFT
   - Partículas o efectos mágicos

3. **Segundo 1.5-2.5**: Aparición mapa global
   - Mapa global se materializa
   - Zonas rojas y azules se iluminan
   - Cartas aparecen en sus posiciones

4. **Segundo 2.5-3**: Fade in elementos combate
   - Controles de cámara aparecen
   - Indicadores de turno se muestran
   - Temporizador cambia a modo combate

### Elementos Visuales
- Partículas doradas/mágicas
- Efecto de zoom cinematográfico
- Sonido de transición épico
- Iluminación que cambia gradualmente

## Transición: Combate → Preparación

### Duración Total: 2 segundos

### Secuencia
1. **Segundo 0-0.5**: Recolección de resultados
   - Efectos de daño/curación en jugadores
   - Cartas regresan a origen

2. **Segundo 0.5-1.5**: Transición visual
   - Fade out del mapa global
   - Efecto inverso al de entrada
   - Partículas que "recogen" las cartas

3. **Segundo 1.5-2**: Vuelta a preparación
   - Tablero personal aparece
   - Banco y tienda se materializan
   - Cámara se fija en posición isométrica

## Micro-transiciones

### Colocar Carta en Tablero
- Duración: 0.3 segundos
- Carta se levanta ligeramente
- Efecto de "snap" al colocarse
- Partículas sutiles en la posición

### Abrir Panel Subastas
- Duración: 0.5 segundos
- Desliza desde borde derecho
- Tablero se oscurece ligeramente
- Sonido de panel abriéndose

### Cerrar Panel Subastas
- Duración: 0.3 segundos
- Desliza hacia borde derecho
- Tablero recupera iluminación
- Sonido de panel cerrándose

### Cambio de Turno (Combate)
- Duración: 0.2 segundos
- Flash de color del equipo activo
- Sonido distintivo por equipo
- Actualización de temporizador

### Compra en Tienda
- Duración: 0.4 segundos
- Carta se ilumina
- Efecto de "absorción" hacia banco
- Sonido de monedas
- Actualización de oro con animación

## Estados de Carga
### Cargando Partida
- Spinner con logo del juego
- Texto: "Conectando con otros jugadores..."
- Barra de progreso si es necesible

### Esperando Jugadores
- Lista de jugadores conectados
- Indicadores de estado (listo/no listo)
- Botón cancelar para host