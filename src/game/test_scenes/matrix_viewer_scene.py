"""
Matrix Viewer Scene - Generates a Matrix2D from a noise defined in config.json
and visualises it as a grayscale tilemap.

Flow:
1. A menu is shown with a dropdown listing all noise names from config.json,
   plus inputs for matrix width and height.
2. On pressing "Aceptar" a NoiseGenerator2D is created from the selected
   noise configuration and a Matrix2D is built from its values.
3. A tilemap backed by a 32-step grayscale tileset renders the matrix.
4. Standard camera controls (WASD/arrows + Q/E zoom) allow navigation.
"""

import json
from pathlib import Path

import pygame
import numpy as np
from typing import Optional, List, Dict, Any

from src.core.tilemap.tilemap import TileMap
from src.core.tilemap.tileset import TileSet
from src.core.camera.camera import Camera
from src.ui import UIManager, Label, Button, TextInput, VBox, HBox, Dropdown
from .base_scene import BaseScene

# Lazy imports
_Matrix2D = None
_NoiseGenerator2D = None

CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "configs" / "config.json"


def _get_matrix2d_class():
    global _Matrix2D
    if _Matrix2D is None:
        from src.virigir_math_utilities.matrix.matrix2d import Matrix2D
        _Matrix2D = Matrix2D
    return _Matrix2D


def _get_noise_generator_class():
    global _NoiseGenerator2D
    if _NoiseGenerator2D is None:
        from src.virigir_math_utilities.noise.generators.noise2d import NoiseGenerator2D
        _NoiseGenerator2D = NoiseGenerator2D
    return _NoiseGenerator2D


def _load_noise_configs() -> Dict[str, Dict[str, Any]]:
    """Load the noise section from config.json and return {name: config_dict}."""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("noise", {})
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[MatrixViewerScene] Failed to load config.json: {e}")
        return {}


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GRAYSCALE_STEPS = 32
TILE_SIZE = 8       # px – small so we can see big matrices
CAMERA_SPEED = 500  # px/s
ZOOM_SPEED = 1.5    # ×/s


class MatrixViewerScene(BaseScene):
    """Scene that lets the user pick a noise from config.json, generate a
    matrix from it, and visualise the result."""

    # -- States ---------------------------------------------------------------
    STATE_MENU = "menu"
    STATE_VIEWER = "viewer"

    def __init__(self):
        super().__init__(
            name="Matrix Viewer",
            description="Generate and visualise a noise-based Matrix2D as a grayscale tilemap"
        )

        self.running = True
        self._state = self.STATE_MENU

        # Noise data loaded from config.json
        self._noise_configs: Dict[str, Dict[str, Any]] = {}
        self._noise_names: List[str] = []

        # UI (menu)
        self._ui: Optional[UIManager] = None
        self._dropdown: Optional[Dropdown] = None
        self._input_width: Optional[TextInput] = None
        self._input_height: Optional[TextInput] = None
        self._error_label: Optional[Label] = None

        # Viewer
        self._matrix = None
        self._tilemap: Optional[TileMap] = None
        self._tileset: Optional[TileSet] = None
        self._camera: Optional[Camera] = None
        self._map_w = 0
        self._map_h = 0
        self._selected_noise_name = ""

    # -- Lifecycle ------------------------------------------------------------

    def on_enter(self):
        # Load noise definitions from config.json
        self._noise_configs = _load_noise_configs()
        self._noise_names = list(self._noise_configs.keys())

        screen = pygame.display.get_surface()
        sw, sh = screen.get_size()
        self._build_menu(sw, sh)

    def on_exit(self):
        self._tilemap = None
        self._tileset = None
        self._camera = None
        self._matrix = None

    # -- Menu -----------------------------------------------------------------

    def _build_menu(self, sw: int, sh: int):
        """Build the dimension-input menu centred on screen."""
        self._state = self.STATE_MENU
        self._ui = UIManager(sw, sh)

        # Container
        form_w = 380
        form_h = 320
        form_x = (sw - form_w) // 2
        form_y = (sh - form_h) // 2

        vbox = VBox(
            x=form_x, y=form_y, width=form_w,
            spacing=12, align=VBox.ALIGN_CENTER,
            bg_color=(35, 35, 50, 230),
            border_radius=8,
            padding=20,
            auto_size=True,
        )

        # Title
        vbox.add_child(Label(
            text="Matrix Viewer",
            font_size=28, color=(220, 220, 255),
            auto_size=True,
        ))

        # Noise selector row
        row_noise = HBox(spacing=8, align='center', auto_size=True)
        row_noise.add_child(Label(
            text="Noise:", font_size=20, color=(200, 200, 200), auto_size=True,
        ))

        self._dropdown = Dropdown(
            width=220, height=28,
            options=self._noise_names if self._noise_names else ["(sin noises)"],
            selected_index=0,
            font_size=20,
            bg_color=(50, 50, 65),
            text_color=(255, 255, 255),
            border_color=(100, 100, 130),
            selected_color=(50, 130, 80),
            hover_color=(70, 70, 90),
            max_visible=6,
        )
        row_noise.add_child(self._dropdown)
        vbox.add_child(row_noise)

        # Width row
        row_w = HBox(spacing=8, align='center', auto_size=True)
        row_w.add_child(Label(text="Width:", font_size=20, color=(200, 200, 200), auto_size=True))
        self._input_width = TextInput(
            width=120, height=28, text="256",
            font_size=20, max_length=5,
            bg_color=(50, 50, 65), text_color=(255, 255, 255),
            border_color=(100, 100, 130), focus_border_color=(100, 160, 255),
            placeholder="cols",
        )
        row_w.add_child(self._input_width)
        vbox.add_child(row_w)

        # Height row
        row_h = HBox(spacing=8, align='center', auto_size=True)
        row_h.add_child(Label(text="Height:", font_size=20, color=(200, 200, 200), auto_size=True))
        self._input_height = TextInput(
            width=120, height=28, text="256",
            font_size=20, max_length=5,
            bg_color=(50, 50, 65), text_color=(255, 255, 255),
            border_color=(100, 100, 130), focus_border_color=(100, 160, 255),
            placeholder="rows",
        )
        row_h.add_child(self._input_height)
        vbox.add_child(row_h)

        # Error label (hidden by default)
        self._error_label = Label(
            text="", font_size=18, color=(255, 80, 80), auto_size=True
        )
        vbox.add_child(self._error_label)

        # Aceptar button
        btn = Button(
            width=160, height=36,
            text="Aceptar",
            font_size=20,
            bg_color=(50, 130, 80),
            hover_color=(70, 160, 100),
            pressed_color=(40, 100, 65),
            border_radius=6,
        )
        btn.on_click(lambda _b: self._on_accept())
        vbox.add_child(btn)

        self._ui.add(vbox)

    def _on_accept(self):
        """Validate inputs and switch to viewer state."""
        # Validate noise selection
        if not self._noise_names:
            self._error_label.text = "No hay noises en config.json"
            return

        noise_name = self._dropdown.selected_text
        if noise_name not in self._noise_configs:
            self._error_label.text = "Selecciona un noise válido"
            return

        # Validate dimensions
        try:
            w = int(self._input_width.text)
            h = int(self._input_height.text)
        except ValueError:
            self._error_label.text = "Introduce valores enteros válidos"
            return

        if w < 1 or h < 1:
            self._error_label.text = "Las dimensiones deben ser ≥ 1"
            return
        if w > 4096 or h > 4096:
            self._error_label.text = "Dimensión máxima: 4096"
            return

        self._error_label.text = ""
        self._selected_noise_name = noise_name
        self._generate_and_show(noise_name, w, h)

    # -- Generation -----------------------------------------------------------

    def _generate_and_show(self, noise_name: str, width: int, height: int):
        """Create a noise generator from config, build the matrix, then show."""
        Matrix2D = _get_matrix2d_class()
        NoiseGenerator2D = _get_noise_generator_class()

        noise_config = self._noise_configs[noise_name]
        noise = NoiseGenerator2D.from_dict(noise_config)

        # Build matrix from noise
        matrix = Matrix2D.create_from_noise(noise, height, width)
        self._matrix = matrix
        self._map_w = width
        self._map_h = height

        # Generate grayscale tileset (white → black, 32 steps)
        self._tileset = TileSet.generate_grayscale_tileset(
            nsteps=GRAYSCALE_STEPS,
            tile_size=(TILE_SIZE, TILE_SIZE),
            columns=GRAYSCALE_STEPS,
            white_to_black=True,
        )

        # Create tilemap
        self._tilemap = TileMap(
            width=width,
            height=height,
            tile_size=(TILE_SIZE, TILE_SIZE),
        )
        self._tilemap.tileset = self._tileset

        # Map matrix values to tile ids:
        # value 0.0 → tile 0  (white / lightest)
        # value 1.0 → tile 31 (black / darkest)
        tile_ids = np.clip(
            (matrix._data * (GRAYSCALE_STEPS - 1)).astype(int),
            0, GRAYSCALE_STEPS - 1,
        )
        for row in range(height):
            for col in range(width):
                self._tilemap.set_tile(col, row, int(tile_ids[row, col]))

        # Camera centred on the map
        screen = pygame.display.get_surface()
        sw, sh = screen.get_size()

        world_w = width * TILE_SIZE
        world_h = height * TILE_SIZE

        self._camera = Camera(
            x=max(0.0, (world_w - sw) / 2),
            y=max(0.0, (world_h - sh) / 2),
            width=sw, height=sh,
            zoom=1.0,
            min_zoom=0.1, max_zoom=10.0,
        )

        self._state = self.STATE_VIEWER
        print(f"[MatrixViewerScene] noise='{noise_name}', matrix {height}×{width} generated.")

    # -- Events ---------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self._state == self.STATE_VIEWER:
                # Back to menu
                screen = pygame.display.get_surface()
                sw, sh = screen.get_size()
                self._build_menu(sw, sh)
                return
            else:
                self.running = False
                return

        if self._state == self.STATE_MENU and self._ui:
            self._ui.handle_event(event)

    # -- Update ---------------------------------------------------------------

    def update(self, dt: float) -> None:
        if self._state == self.STATE_MENU:
            if self._ui:
                self._ui.update(dt)
            return

        # Viewer
        if not self._camera:
            return

        keys = pygame.key.get_pressed()

        # Zoom
        if keys[pygame.K_e]:
            self._camera.zoom *= ZOOM_SPEED ** dt
        elif keys[pygame.K_q]:
            self._camera.zoom /= ZOOM_SPEED ** dt

        # Update bounds for current zoom
        zoom = self._camera.zoom
        visible_w = self._camera.width / zoom
        visible_h = self._camera.height / zoom
        world_w = self._map_w * TILE_SIZE
        world_h = self._map_h * TILE_SIZE
        self._camera.set_bounds(
            min_x=0, max_x=max(0.0, world_w - visible_w),
            min_y=0, max_y=max(0.0, world_h - visible_h),
        )

        # Movement
        speed = CAMERA_SPEED / zoom
        dx = dy = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += speed * dt
        if dx or dy:
            self._camera.move(dx, dy)

    # -- Draw -----------------------------------------------------------------

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((20, 20, 30))

        if self._state == self.STATE_MENU:
            if self._ui:
                self._ui.draw(screen)
            return

        # Viewer — use chunk-based rendering
        if not self._tilemap or not self._camera:
            return

        self._tilemap.draw(screen, self._camera, self._tileset)

        self._draw_ui(screen)

    def _draw_ui(self, screen: pygame.Surface) -> None:
        small = pygame.font.Font(None, 20)

        cam = self._camera
        info = (
            f"Noise: {self._selected_noise_name}  "
            f"Matrix: {self._map_h}x{self._map_w}  "
            f"Camera: ({int(cam.x)},{int(cam.y)})  "
            f"Zoom: {cam.zoom:.2f}x"
        )
        screen.blit(small.render(info, True, (200, 200, 200)), (10, 10))

        hint = "WASD/Arrows: Move | Q/E: Zoom | ESC: Back to menu"
        surf = small.render(hint, True, (150, 150, 150))
        rect = surf.get_rect(bottomleft=(10, screen.get_height() - 10))
        screen.blit(surf, rect)

