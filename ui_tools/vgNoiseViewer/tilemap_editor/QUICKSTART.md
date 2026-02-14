# Tilemap Editor - Inicio Rápido
## 🚀 Instalación
```bash
# Instalar dependencia (solo si no está instalada)
pip install Pillow
```
## ▶️ Ejecutar
```bash
cd /home/deck/Documents/virigir/vgNoise/ui_tools/vgNoiseViewer
python3 run_tilemap_editor.py
```
## 🎮 Uso en 5 Pasos
### 1️⃣ Cargar Tileset
- Click **"Add"** en el panel izquierdo
- Selecciona una imagen PNG o JPG
- Ingresa el tamaño de cada tile (ej: 32x32)
### 2️⃣ Seleccionar Tile
- Click en cualquier tile del grid mostrado
- Verás el tile seleccionado en la parte inferior
### 3️⃣ Pintar
- Click en el canvas principal (derecha) para colocar el tile
- Click y arrastra para pintar múltiples tiles
### 4️⃣ Crear Nuevo Mapa (Opcional)
- Click **"New Map"** en la toolbar
- Configura dimensiones (ej: 30x20)
- Configura tamaño de tile (ej: 32)
### 5️⃣ Limpiar (Opcional)
- Click **"Clear"** para borrar todo el mapa
## 📸 Ejemplo Visual
```
┌──────────────────────────────────────┐
│ File | Help                         │
├─────────────┬────────────────────────┤
│  Tilesets   │ Map: 20x15  [New][Clear]│
│             ├────────────────────────┤
│ [Add]       │                        │
│ ┌─────────┐ │    ← Click aquí para   │
│ │ 🎨 🎨 🎨│ │       pintar tiles     │
│ │ 🎨 🎨 🎨│ │                        │
│ │ 🎨 🎨 🎨│ │    [Grid del mapa]     │
│ └─────────┘ │                        │
│ ↑           │                        │
│ Click aquí  │                        │
│ para        │                        │
│ seleccionar │                        │
└─────────────┴────────────────────────┘
```
## 💡 Tips
- **Múltiples tilesets**: Puedes cargar varios y cambiar entre ellos
- **Scroll**: Usa las barras de desplazamiento para explorar mapas grandes
- **Dimensiones**: Las imágenes deben ser divisibles por el tamaño de tile
## ⚠️ Requisitos de Imagen
Tu imagen de tileset debe:
- ✅ Ser PNG o JPG
- ✅ Tener dimensiones divisibles por el tamaño de tile
- ✅ Ejemplo: 256x128 con tiles de 32x32 = ✅ OK (8x4 grid)
- ❌ Ejemplo: 250x130 con tiles de 32x32 = ❌ Error
## 🐛 Troubleshooting
**Error: "Image width is not divisible by tile_width"**
- La imagen no es compatible con ese tamaño de tile
- Prueba con otro tamaño de tile o ajusta la imagen
**No se muestra nada al pintar**
- Verifica que has seleccionado un tile (debe aparecer en "Selected:")
- Verifica que has cargado un tileset
**El tileset no se carga**
- Verifica que Pillow está instalado: `pip install Pillow`
- Verifica que el archivo existe y es una imagen válida
## 📚 Más Información
Ver `README_TILEMAP_EDITOR.md` para documentación completa.
