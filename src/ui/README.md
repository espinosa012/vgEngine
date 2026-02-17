# vgEngine UI Framework

Framework de componentes UI orientado a objetos para Pygame.

## 📋 Descripción

Un sistema completo de componentes UI construido sobre Pygame, diseñado con principios de programación orientada a objetos. Proporciona widgets, contenedores de layout, sistema de temas, y gestión de eventos para crear interfaces de usuario en juegos y aplicaciones.

## ✨ Características

### 🎨 Componentes Base

- **Widget**: Clase base abstracta para todos los componentes UI
- **UIManager**: Gestor central para jerarquía de widgets y distribución de eventos
- **Theme System**: Sistema de temas con colores, fuentes y dimensiones configurables

### 🧩 Widgets

| Widget | Descripción | Características |
|--------|-------------|-----------------|
| **Label** | Texto estático | Alineación, auto-tamaño, múltiples estilos de fuente |
| **Button** | Botón interactivo | Estados (hover, pressed, disabled), callbacks |
| **Panel** | Panel decorativo | Fondo, bordes, padding, alpha blending |
| **ImageWidget** | Mostrar imágenes | Múltiples modos de escala (fit, fill, stretch) |
| **Checkbox** | Input booleano | Check/uncheck, label opcional |
| **Slider** | Input numérico | Horizontal/vertical, min/max/step configurables |
| **TextInput** | Entrada de texto | Cursor, placeholder, límite de caracteres |

### 📦 Contenedores

| Container | Descripción | Uso |
|-----------|-------------|-----|
| **Container** | Contenedor base | Posicionamiento manual |
| **VBox** | Layout vertical | Apila widgets verticalmente |
| **HBox** | Layout horizontal | Apila widgets horizontalmente |
| **Grid** | Layout en cuadrícula | Organiza en filas y columnas |
| **ScrollView** | Vista desplazable | Contenido scrollable con scrollbar |

### 🎭 Sistema de Temas

Tres temas predefinidos:
- **Dark** (por defecto): Tema oscuro moderno
- **Light**: Tema claro
- **High Contrast**: Alto contraste para accesibilidad

## 🚀 Inicio Rápido

### Instalación

```python
# El framework está en src/ui/
from src.ui import UIManager, Button, Label, VBox
```

### Ejemplo Básico

```python
import pygame
from src.ui import UIManager, Button, Label, VBox

# Inicializar Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Crear UI Manager
ui = UIManager(800, 600)

# Crear componentes
vbox = VBox(x=50, y=50, spacing=10)
vbox.add_child(Label(text="¡Hola Mundo!", font_size=24))
vbox.add_child(Button(text="Haz clic").on_click(lambda btn: print("¡Clic!")))

ui.add(vbox)

# Game loop
running = True
while running:
    dt = clock.tick(60) / 1000.0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        ui.handle_event(event)
    
    ui.update(dt)
    
    screen.fill((30, 30, 30))
    ui.draw(screen)
    
    pygame.display.flip()

pygame.quit()
```

## 📚 Ejemplos Detallados

### Crear un Botón con Callback

```python
button = Button(
    x=100, y=100,
    width=150, height=40,
    text="Guardar"
).on_click(lambda btn: save_game())
```

### Layout Vertical (VBox)

```python
menu = VBox(x=50, y=50, spacing=10, align='center')
menu.add_child(Label(text="Menú Principal", font_size=28))
menu.add_child(Button(text="Nueva Partida"))
menu.add_child(Button(text="Cargar"))
menu.add_child(Button(text="Opciones"))
menu.add_child(Button(text="Salir"))
```

### Layout Horizontal (HBox)

```python
toolbar = HBox(x=10, y=10, spacing=5, align='center')
toolbar.add_child(Button(text="Abrir", width=80))
toolbar.add_child(Button(text="Guardar", width=80))
toolbar.add_child(Button(text="Cerrar", width=80))
```

### Grid Layout

```python
grid = Grid(
    x=50, y=50,
    width=400, height=400,
    columns=3,
    spacing_x=10,
    spacing_y=10
)

for i in range(9):
    grid.add_child(Button(text=f"Botón {i+1}"))
```

### Slider con Callback

```python
volume_slider = Slider(
    x=100, y=100,
    width=200,
    min_value=0,
    max_value=100,
    value=75,
    show_value=True
).on_change(lambda s: set_volume(s.value))
```

### TextInput con Validación

```python
name_input = TextInput(
    x=100, y=100,
    width=250,
    placeholder="Ingresa tu nombre...",
    max_length=20
).on_submit(lambda ti: process_name(ti.text))
```

### Checkbox

```python
checkbox = Checkbox(
    x=100, y=100,
    text="Activar música",
    checked=True
).on_change(lambda cb: toggle_music(cb.checked))
```

### Panel con Contenido

```python
panel = Panel(
    x=50, y=50,
    width=300, height=200,
    bg_color=(50, 50, 50),
    border_width=2,
    border_radius=8,
    padding=15
)

panel.add_child(Label(text="Panel con contenido"))
panel.add_child(Button(y=50, text="Botón interno"))
```

### ScrollView

```python
scroll = ScrollView(
    x=50, y=50,
    width=300, height=400,
    show_scrollbar=True
)

for i in range(50):
    scroll.add_child(Label(y=i*30, text=f"Elemento {i+1}"))
```

### Cambiar Tema

```python
from src.ui import UITheme, set_default_theme

# Cambiar a tema claro
ui.theme = UITheme.light()

# Cambiar a tema de alto contraste
ui.theme = UITheme.high_contrast()

# Crear tema personalizado
custom_theme = UITheme(
    name="custom",
    colors=UIColors(
        primary=(255, 100, 0),
        background=(10, 10, 20)
    )
)
ui.theme = custom_theme
```

## 🏗️ Arquitectura

### Jerarquía de Clases

```
Widget (ABC)
├── Label
├── Button
├── Panel
├── ImageWidget
├── Checkbox
├── Slider
├── TextInput
└── Container
    ├── VBox
    ├── HBox
    ├── Grid
    └── ScrollView
```

### Widget Base

Todos los widgets heredan de `Widget` que proporciona:

- **Posición y Tamaño**: `x`, `y`, `width`, `height`
- **Estado**: `visible`, `enabled`, `focused`, `hovered`, `pressed`
- **Jerarquía**: `parent`, `children`
- **Eventos**: `on_click()`, `on_hover_enter()`, `on_hover_exit()`, `on_focus()`, `on_blur()`
- **Métodos**: `draw()`, `update()`, `handle_event()`

### Sistema de Eventos

El sistema de eventos propaga eventos de Pygame a través de la jerarquía de widgets:

1. `UIManager.handle_event()` recibe eventos de Pygame
2. Los eventos se distribuyen a widgets (primero los de arriba)
3. Los widgets pueden consumir eventos retornando `True`
4. Los widgets hijos reciben eventos antes que los padres

### Sistema de Coordenadas

- **Posición Local**: Relativa al padre
- **Posición Absoluta**: En coordenadas de pantalla
- Los widgets calculan automáticamente posiciones absolutas

## 🎨 Personalización

### Colores Personalizados

```python
button = Button(
    text="Custom",
    bg_color=(255, 100, 0),
    hover_color=(255, 150, 50),
    pressed_color=(200, 80, 0),
    text_color=(255, 255, 255)
)
```

### Fuentes Personalizadas

```python
label = Label(
    text="Custom Font",
    font_family="Arial",
    font_size=20,
    bold=True,
    italic=False
)
```

### Temas Personalizados

```python
from src.ui import UITheme, UIColors, UIFonts

my_theme = UITheme(
    name="my_theme",
    colors=UIColors(
        primary=(0, 200, 100),
        background=(15, 15, 25),
        text=(240, 240, 240)
    ),
    fonts=UIFonts(
        family="Consolas",
        size_normal=14
    )
)

ui.theme = my_theme
```

## 🔧 API Reference

### UIManager

```python
UIManager(width: int, height: int, theme: Optional[UITheme] = None)
```

**Métodos:**
- `add(widget)`: Agregar widget al manager
- `remove(widget)`: Remover widget
- `clear()`: Limpiar todos los widgets
- `handle_event(event)`: Procesar evento de Pygame
- `update(dt)`: Actualizar widgets
- `draw(surface)`: Dibujar widgets

### Widget (Base)

**Propiedades:**
- `x`, `y`: Posición
- `width`, `height`: Tamaño
- `visible`: Visibilidad
- `enabled`: Si puede recibir input
- `focused`: Si tiene foco
- `hovered`: Si el mouse está encima
- `parent`: Widget padre
- `children`: Lista de hijos

**Métodos:**
- `add_child(widget)`: Agregar hijo
- `remove_child(widget)`: Remover hijo
- `focus()`: Dar foco
- `blur()`: Quitar foco
- `on_click(callback)`: Callback de clic
- `on_hover_enter(callback)`: Callback al entrar mouse
- `on_hover_exit(callback)`: Callback al salir mouse

## 🎯 Casos de Uso

### Menú de Juego

```python
menu = VBox(x=300, y=200, spacing=15, align='center')
menu.add_child(Label(text="JUEGO", font_size=48, bold=True))
menu.add_child(Button(text="Nueva Partida", width=200))
menu.add_child(Button(text="Continuar", width=200))
menu.add_child(Button(text="Opciones", width=200))
menu.add_child(Button(text="Salir", width=200))
```

### Panel de Configuración

```python
settings = VBox(x=50, y=50, spacing=10)

settings.add_child(Label(text="Configuración", font_size=24))

volume = HBox(spacing=10)
volume.add_child(Label(text="Volumen:"))
volume.add_child(Slider(width=200, value=75))
settings.add_child(volume)

settings.add_child(Checkbox(text="Pantalla completa"))
settings.add_child(Checkbox(text="VSync"))
```

### Inventario con Grid

```python
inventory = Grid(
    x=100, y=100,
    width=400, height=400,
    columns=5,
    rows=5,
    spacing_x=5,
    spacing_y=5
)

for i in range(25):
    slot = Panel(bg_color=(60, 60, 60), border_width=1)
    inventory.add_child(slot)
```

## 🧪 Demo

Ejecuta el demo completo:

```bash
python demo_ui_framework.py
```

El demo muestra:
- Todos los tipos de widgets
- Diferentes layouts
- Sistema de temas
- Interacciones y callbacks

## 📝 Notas

- **Rendimiento**: Optimizado para 60 FPS con cientos de widgets
- **Extensibilidad**: Fácil de extender creando subclases de `Widget`
- **Integración**: Compatible con cualquier juego basado en Pygame
- **Type Hints**: Código completamente tipado para mejor autocompletado

## 🔮 Futuro

Características planeadas:
- [ ] Navegación por teclado (Tab)
- [ ] Tooltips
- [ ] Drag & Drop
- [ ] Animaciones
- [ ] Menús contextuales
- [ ] Diálogos modales
- [ ] ProgressBar
- [ ] RadioButton
- [ ] ComboBox / Dropdown
- [ ] Integración con `core.color.Color`

## 📄 Licencia

Parte del proyecto vgEngine.

---

**Creado con ❤️ para vgEngine**

