# Flujos de Interacción

## Flujo Principal: Una Ronda Completa

### 1. Inicio de Ronda
Usuario inicia sesión → Lobby → Sala de espera → Cuenta regresiva → Fase Preparación

### 2. Fase Preparación (30 segundos)
Temporizador cuenta regresiva
↓
Usuario ve:

Banco de cartas actual
Tienda con 5 cartas aleatorias
[Opcional] Panel subastas se abre
↓
Acciones posibles:
Comprar cartas de tienda
Hacer reroll (si tiene tokens)
Ofertar en subastas (si están activas)
Colocar cartas del banco al tablero
Reorganizar cartas en tablero
↓
Últimos 5 segundos: Warning visual
↓
Tiempo agotado → Transición a Combate


### 3. Transición a Combate (3 segundos)
Auto-completar tablero con cartas del banco
↓
Animación de transición
↓
Cámara cambia a modo libre
↓
Mapa global aparece

### 4. Fase Combate (60 segundos)
Sistema de turnos inicia
↓
Turno Equipo Rojo (15 seg)

Cartas rojas pueden actuar
Usuario puede dar órdenes si tiene cartas rojas
↓
Turno Equipo Azul (15 seg)
Cartas azules pueden actuar
Usuario puede dar órdenes si tiene cartas azules
↓
[Repetir turnos hasta tiempo agotado o victoria]
↓
Calcular daño a jugadores según cartas supervivientes
↓
Transición de vuelta a Preparación


## Flujo Secundario: Gestión de Subastas

### Apertura de Subastas
Sistema determina si hay subastas esta ronda
↓
Panel desliza desde la derecha
↓
Usuario ve cartas disponibles y ofertas actuales
↓
Temporizador específico de subastas (15 segundos)

### Proceso de Oferta
Usuario selecciona carta
↓
Ingresa monto mayor a oferta actual
↓
Sistema valida que tenga oro suficiente
↓
Oferta se registra y se muestra
↓
Otros jugadores pueden contra-ofertar
↓
Al terminar tiempo: mayor oferta gana

### Cierre de Subastas
Tiempo agotado O todas las cartas vendidas
↓
Panel se cierra automáticamente
↓
Cartas van al banco del ganador
↓
Oro se descuenta automáticamente

## Flujo de Interacción: Tablero

### Colocar Carta desde Banco
Usuario hace click en carta del banco
↓
Carta se "levanta" visualmente
↓
Tablero muestra posiciones válidas (destacadas)
↓
Usuario hace click en hexágono válido
↓
Carta se anima hacia la posición
↓
Verificar fusiones automáticas
↓
[Si hay fusión] Animación de fusión

### Mover Carta en Tablero
Usuario hace click en carta ya colocada
↓
Carta se selecciona (outline destacado)
↓
Posiciones válidas se iluminan
↓
Usuario hace click en nueva posición
↓
Carta se desliza a nueva ubicación

### Quitar Carta del Tablero
Usuario hace click derecho en carta
↓
Menú contextual aparece
↓
Selecciona "Quitar del tablero"
↓
Carta regresa al banco con animación

## Flujo de Interacción: Combate

### Dar Órdenes a Cartas (Solo si es tu turno)
Usuario hace click en su carta
↓
Carta se selecciona (outline de color del equipo)
↓
Panel de órdenes aparece
↓
Opciones disponibles:

Mover a posición
Atacar enemigo específico
Usar habilidad
Cambiar comportamiento
↓
Usuario selecciona acción
↓
[Si es movimiento] Hace click en destino válido
[Si es ataque] Hace click en enemigo válido
[Si es habilidad] Selecciona de lista disponible
↓
Orden se ejecuta inmediatamente


### Control de Cámara
Usuario mueve mouse al borde → Cámara se desplaza
WASD → Movimiento direccional
Rueda mouse → Zoom in/out
Click derecho + drag → Rotar cámara
Click en minimapa → Saltar a esa ubicación
Botón "Mis cartas" → Centrar en cartas propias

## Manejo de Errores

### Sin Conexión
Detectar pérdida de conexión
↓
Mostrar overlay "Reconectando..."
↓
Intentar reconexión automática (3 intentos)
↓
[Si falla] Mostrar "Conexión perdida" + botón manual

### Acción Inválida
Usuario intenta acción no permitida
↓
Mostrar mensaje de error breve (2 segundos)
↓
Resaltar visualmente el problema
↓
Sugerir acción correcta si es posible

### Tiempo Agotado
Últimos 5 segundos de cualquier fase
↓
Warning visual (color rojo, pulsación)
↓
Sonido de advertencia
↓
Tiempo 0: Transición forzada inmediata