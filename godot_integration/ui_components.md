# Componentes de Interfaz

## Temporizador Central
### Función
- Mostrar tiempo restante de fase actual
- Indicar qué fase está activa (Preparación/Combate)

### Ubicación
- Centro superior de la pantalla
- Siempre visible

### Estados
- Preparación: "Preparación - 00:30"
- Combate: "Combate - Turno Rojo - 00:15"
- Transición: "Transicionando..."

## Indicadores de Recursos
### Vida del Jugador
- Posición: Superior izquierda
- Formato: "❤️ 85/100"
- Color: Verde > Amarillo > Rojo

### Oro
- Posición: Junto a vida
- Formato: "💰 45"
- Animación al cambiar

### Nivel
- Posición: Junto a oro
- Formato: "⭐ Nivel 3"
- Barra de experiencia debajo

## Tablero Hexagonal
### Preparación
- Vista isométrica fija
- Hexágonos resaltados al hover
- Cartas con animación al colocar
- Indicadores de posición válida

### Combate
- Expande a mapa global
- Múltiples zonas de color
- Cartas con estados de vida
- Efectos de habilidades

## Banco de Cartas
### Ubicación
- Parte inferior izquierda
- Scroll horizontal si excede espacio

### Comportamiento
- Drag & drop hacia tablero
- Información al hover
- Fusiones automáticas visuales

## Tienda
### Ubicación
- Parte inferior derecha
- 5 cartas disponibles

### Elementos
- Cartas con precio
- Botón "Reroll" con contador
- Indicador de tokens disponibles

## Panel de Subastas
### Comportamiento
- Aparece deslizando desde derecha
- Solo durante fase de preparación
- Se cierra automáticamente al finalizar

### Contenido
- Lista de cartas disponibles
- Ofertas actuales
- Campo para ofertar
- Tiempo restante de subasta

## Controles de Cámara (Solo Combate)
### Ubicación
- Esquina inferior derecha

### Elementos
- Minimapa del mapa global
- Botones de zoom +/-
- Indicador de posición actual
- Botón "Centrar en mis cartas"