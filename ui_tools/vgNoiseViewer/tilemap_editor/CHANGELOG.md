# Tilemap Editor - Changelog
## [v1.1] - 2026-02-14
### ✨ Nuevas Funcionalidades
#### 🔍 Zoom en Tileset
- **Controles de zoom** con botones +/- y Reset
- **Zoom con rueda del ratón** (scroll up/down)
- **Rango de zoom**: 25% a 400%
- **Indicador visual** del nivel de zoom actual
- El zoom se aplica a la imagen del tileset y al grid
- Zoom suave con incrementos de 25%
#### 🎯 Selección Visual de Tiles
- **Borde naranja brillante** alrededor de la tile seleccionada
- **Grosor de 3px** para máxima visibilidad
- La selección se mantiene visible al hacer zoom
- Se actualiza automáticamente al cambiar de tile
- Color distintivo (#ffaa00) para no confundirse con el grid
### 🔧 Mejoras Técnicas
#### Zoom
- `zoom_level`: Variable de estado (1.0 = 100%)
- `_zoom_in()`: Incrementa zoom en 25%
- `_zoom_out()`: Reduce zoom en 25%
- `_zoom_reset()`: Vuelve a 100%
- `_on_mouse_wheel()`: Maneja scroll del mouse
- `_update_zoom()`: Actualiza visualización
#### Selección
- `selection_rect_id`: ID del rectángulo de selección
- `_draw_selection()`: Dibuja el borde de selección
- Se usa tag "selection" para fácil eliminación/actualización
- Coordenadas ajustadas según el nivel de zoom
### 📋 Controles
#### Barra de Zoom
```
[Zoom:] [-] [100%] [+] [Reset]
```
- **Botón "-"**: Zoom out (reduce)
- **Label central**: Muestra porcentaje actual
- **Botón "+"**: Zoom in (aumenta)
- **Botón "Reset"**: Vuelve a 100%
#### Mouse
- **Scroll arriba**: Zoom in
- **Scroll abajo**: Zoom out
- **Click en tile**: Selecciona y marca con borde naranja
### 🎨 Aspectos Visuales
#### Grid
- Color: #444444 (gris oscuro)
- Grosor: 1px
- Se escala con el zoom
#### Selección
- Color: #ffaa00 (naranja brillante)
- Grosor: 3px
- Tag: "selection"
- Siempre visible sobre el grid
### 💡 Casos de Uso
#### Tilesets Pequeños
- Zoom in (200-400%) para ver detalles
- Útil para tiles de 8x8 o 16x16
#### Tilesets Grandes
- Zoom out (25-50%) para ver todo el tileset
- Facilita navegación en grids grandes
#### Selección Precisa
- Borde naranja elimina ambigüedad
- Sabes exactamente qué tile está activa
- No se pierde al hacer zoom
### 🐛 Correcciones
- Eliminada línea duplicada en callback de selección
- Ajustadas coordenadas de click para funcionar con zoom
- Grid se dibuja correctamente en todos los niveles de zoom
### 📊 Estadísticas
- **Nuevas líneas de código**: ~100
- **Nuevos métodos**: 5 (zoom) + 1 (selección)
- **Nuevas variables**: 2 (zoom_level, selection_rect_id)
- **Nuevos controles UI**: 4 botones + 1 label
### ⚡ Rendimiento
- Zoom usa `Image.Resampling.NEAREST` para pixelart
- Selección usa canvas tags para eficiencia
- No impacto en la funcionalidad de pintado del tilemap
### 🔮 Futuro
Posibles mejoras:
- Zoom con atajos de teclado (Ctrl +/-)
- Pan/arrastre con botón medio del mouse
- Mini-mapa para navegación rápida
- Memoria de zoom por tileset
- Animación suave de zoom
---
## [v1.0] - 2026-02-14
### Lanzamiento Inicial
- Carga de múltiples tilesets desde PNG/JPG
- Selector de tileset activo
- Visualización con grid
- Selección de tiles por click
- Pintado con mouse en tilemap
- Crear mapas personalizados
- Limpiar mapa completo
