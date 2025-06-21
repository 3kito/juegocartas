# Requerimientos Técnicos

## Plataforma de Desarrollo
### Godot Engine
- Versión: 4.x
- Lenguaje: GDScript
- Renderizado: 3D con Vulkan/OpenGL

### Backend
- Python con FastAPI
- WebSockets para tiempo real
- Base de datos: SQLite/PostgreSQL

## Estructura de Proyecto Godot

### Scenes principales
scenes/
├── Main.tscn                 # Escena principal
├── GameBoard.tscn           # Tablero de juego
├── UI/
│   ├── PrepUI.tscn         # Interfaz preparación
│   ├── CombatUI.tscn       # Interfaz combate
│   ├── AuctionPanel.tscn   # Panel subastas
│   └── Components/         # Componentes reutilizables
└── Transitions/
└── PhaseTransition.tscn # Transiciones

### Scripts principales
scripts/
├── GameManager.gd           # Gestor principal
├── NetworkManager.gd        # Comunicación WebSocket
├── CameraController.gd      # Control de cámara
├── UIManager.gd            # Gestión de interfaces
└── CardSystem.gd           # Sistema de cartas

## Especificaciones de Rendimiento

### Framerate Target
- **Preparación**: 60 FPS estables
- **Combate**: 45-60 FPS (mínimo 30)
- **Transiciones**: 60 FPS para fluidez

### Límites de Objetos
- **Cartas simultáneas**: Máximo 200 en pantalla
- **Partículas**: Máximo 1000 activas
- **Efectos de luz**: Máximo 50 dinámicas

## Comunicación Cliente-Servidor

### Protocolo WebSocket
```json
// Mensaje de estado del juego
{
  "type": "game_state",
  "phase": "preparation|combat",
  "time_remaining": 30,
  "player_data": {
    "gold": 50,
    "level": 3,
    "health": 85
  },
  "board_state": [...],
  "shop_cards": [...],
  "auction_data": {...}
}

// Mensaje de acción del jugador
{
  "type": "player_action",
  "action": "place_card|buy_card|bid_auction|move_card",
  "data": {...}
}
Frecuencia de Actualización

Preparación: 2 Hz (cada 500ms)
Combate: 10 Hz (cada 100ms)
Transiciones: 20 Hz (cada 50ms)

Recursos Visuales
Modelos 3D

Cartas: Low-poly, máximo 500 tris
Tablero: Hexágonos modulares
Efectos: Planes con texturas animadas

Texturas

Resolución: 512x512 para cartas
Formato: Comprimido (DXT/ETC2)
Mipmaps: Habilitados para optimización

Animaciones

Interpolación: Tween suaves (ease-in-out)
Duración estándar: 0.3-0.5 segundos
Transiciones: 2-3 segundos máximo

Audio
Efectos de Sonido

Formato: OGG Vorbis comprimido
Frecuencia: 44.1 kHz máximo
Canales simultáneos: Máximo 32

Categorías de Audio

UI: Clicks, hovers, transiciones
Gameplay: Colocar cartas, ataques, habilidades
Ambiente: Música de fondo adaptativa
Notificaciones: Alertas, warnings, tiempo

Configuración de Calidad
Niveles de Detalle

Alto: Todas las funciones habilitadas
Medio: Reducir partículas y sombras
Bajo: Solo geometría básica

Opciones Configurables

Calidad de sombras (Off/Low/High)
Densidad de partículas (25%/50%/100%)
Calidad de texturas (Half/Full)
Antialiasing (Off/MSAA 2x/4x)
VSync (On/Off)

Compatibilidad
Sistemas Operativos

Windows 10/11 (DirectX 11+)
macOS 10.14+ (Metal)
Linux (Vulkan/OpenGL 3.3+)

Hardware Mínimo

CPU: Dual-core 2.5GHz
RAM: 4GB
GPU: DirectX 11 compatible
Espacio: 2GB disponible
Red: Conexión estable a internet

Hardware Recomendado

CPU: Quad-core 3.0GHz+
RAM: 8GB+
GPU: Dedicated con 2GB VRAM
Espacio: 4GB disponible
Red: Banda ancha estable

Configuración de Desarrollo
Variables de Entorno
DEBUG_MODE=true
SERVER_URL=ws://localhost:8000
LOG_LEVEL=verbose
ENABLE_PROFILER=true
Herramientas de Debug

Profiler de rendimiento integrado
Log de mensajes de red
Inspector de estado del juego
Métricas de framerate en tiempo real

Seguridad
Validación Cliente

Todas las acciones validadas en servidor
Estado del juego autoritativo en backend
Timeouts para prevenir spam de acciones

Autenticación

Token de sesión para WebSocket
Reconexión automática con mismo token
Expiración de sesión configurable