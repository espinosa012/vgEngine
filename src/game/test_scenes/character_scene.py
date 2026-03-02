"""
Character Scene – escena para probar el control de personajes.

Layout
──────
Panel izquierdo (fijo, PANEL_W px)
  ┌──────────────────────────────────┐
  │  [Spawn Personaje]               │
  │                                  │
  │  Obstáculos                      │
  │  Densidad: [───────────]  0.20   │
  │  [Aleatorizar obstáculos]        │
  │                                  │
  │  Info: X personajes              │
  │        Y obstáculos              │
  └──────────────────────────────────┘

Área derecha: tilemap 24×24 con cámara
  - Tiles de 16×16 px color gris claro uniforme
  - Personajes como rectángulos de 8px de ancho y alto variable (12–20)
  - Celdas de obstáculo destacadas en color rojizo semitransparente
"""

from __future__ import annotations

import random
from typing import List, Optional, Set, Tuple

import pygame

from src.core.tilemap.tilemap import TileMap
from src.core.tilemap.tileset import TileSet
from src.core.camera.camera import Camera
from src.ui import (
    UIManager, Label, Button, VBox, HBox, NumericInput, ScrollView,
    SelectableList,
)
from core.character.shape import RectShape
from core.color.color import Color
from game.character import GameCharacter

from .base_scene import BaseScene

# ── Constants ─────────────────────────────────────────────────────────────────
MAP_W        = 24           # tiles
MAP_H        = 24           # tiles
TILE_SIZE    = 16           # pixels

PANEL_W      = 220
CAMERA_SPEED = 300          # world px / second
ZOOM_SPEED   = 1.5

# Character dimensions
CHAR_W           = 8
CHAR_H_MIN       = 12
CHAR_H_MAX       = 20
CHAR_MOVE_SPEED  = 5.0   # cells per second

DEFAULT_OBSTACLE_DENSITY = 0.20   # used on scene start

# Path-overlay colours
PATH_COLOR       = (100, 200, 255, 120)   # RGBA – visited path cells
PATH_DEST_COLOR  = (255, 240, 60,  200)   # RGBA – destination cell highlight

# Colors
BG_COLOR       = (22, 22, 34)
PANEL_BG       = (28, 28, 44, 250)
TILE_COLOR     = (185, 185, 190)        # gris claro base
OBSTACLE_COLOR = (200, 60, 60, 160)     # rojo semitransparente
TITLE_COLOR    = (215, 215, 255)
LABEL_COLOR    = (180, 180, 205)
BTN_SPAWN_BG   = (48, 125, 78)
BTN_SPAWN_HV   = (68, 155, 98)
BTN_OBS_BG     = (125, 75, 40)
BTN_OBS_HV     = (160, 100, 60)
INPUT_BG       = (48, 48, 62)
INPUT_BORDER   = (95, 95, 128)
FOCUS_BORDER   = (95, 155, 255)

DIVIDER_W = 3


def _random_char_color() -> Tuple[Color, Color]:
    """Return a vivid random fill colour and a darker border colour."""
    hue = random.random()                        # 0–1
    # Convert HSV (full saturation, high value) → RGB
    import colorsys
    r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 0.90)
    fill   = Color(int(r * 255), int(g * 255), int(b * 255))
    border = Color(
        max(0, int(r * 255) - 60),
        max(0, int(g * 255) - 60),
        max(0, int(b * 255) - 60),
    )
    return fill, border


# ── Small widget helpers ───────────────────────────────────────────────────────

def _lbl(text: str, size: int = 15, color=LABEL_COLOR) -> Label:
    return Label(text=text, font_size=size, color=color, auto_size=True)


def _btn(text: str, bg: tuple, hv: tuple, w: int = 180, h: int = 32) -> Button:
    return Button(
        width=w, height=h, text=text, font_size=15,
        bg_color=bg, hover_color=hv,
        pressed_color=tuple(max(0, c - 25) for c in bg),
        border_radius=5,
    )


def _numeric(value: float, *, min_v: float, max_v: float,
             step: float, w: int = 140, decimals: int = 2) -> NumericInput:
    return NumericInput(
        width=w, height=26, value=value,
        min_value=min_v, max_value=max_v, step=step,
        decimals=decimals,
        font_size=15,
        bg_color=INPUT_BG, text_color=(255, 255, 255),
        border_color=INPUT_BORDER, focus_border_color=FOCUS_BORDER,
        border_radius=4,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Scene
# ═══════════════════════════════════════════════════════════════════════════════

class CharacterScene(BaseScene):
    """Escena de prueba para el control y spawn de personajes sobre un tilemap."""

    def __init__(self) -> None:
        super().__init__(
            name="Character Scene",
            description="Prueba de spawn de personajes y obstáculos sobre un tilemap",
        )
        self.running: bool = True

        # Tilemap / tileset / camera
        self._tilemap: Optional[TileMap] = None
        self._tileset: Optional[TileSet] = None
        self._camera:  Optional[Camera]  = None

        # Obstacle surface (pre-rendered overlay, rebuilt when obstacles change)
        self._obstacle_surf: Optional[pygame.Surface] = None

        # Game state
        self._characters: List[GameCharacter] = []
        self._char_cells: dict = {}
        self._obstacles:  Set[Tuple[int, int]] = set()

        # UI
        self._ui: Optional[UIManager] = None
        self._density_input:  Optional[NumericInput]    = None
        self._info_chars:     Optional[Label]           = None
        self._info_obstacles: Optional[Label]           = None
        self._char_list:      Optional[SelectableList]  = None

        # Selection state
        self._selected_char: Optional[GameCharacter] = None

        # Layout
        self._screen_w: int = 0
        self._screen_h: int = 0

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def on_enter(self) -> None:
        screen = pygame.display.get_surface()
        self._screen_w, self._screen_h = screen.get_size()
        self._build_tilemap()
        self._build_camera()
        self._build_ui()
        # Generate obstacles immediately with the default density
        self._randomize_obstacles(density=DEFAULT_OBSTACLE_DENSITY)

    def on_exit(self) -> None:
        self._tilemap  = None
        self._tileset  = None
        self._camera   = None
        self._characters.clear()
        self._char_cells.clear()
        self._obstacles.clear()
        self._selected_char = None
        self._char_list     = None

    def on_resize(self, sw: int, sh: int) -> None:
        self._screen_w = sw
        self._screen_h = sh
        if self._camera:
            self._camera.width  = sw
            self._camera.height = sh
        # Rebuild UI so list height fills the new screen
        self._build_ui()

    # Also support the BaseScene-style setup() entry point
    def setup(self, screen_width: int, screen_height: int) -> None:
        super().setup(screen_width, screen_height)
        self._screen_w = screen_width
        self._screen_h = screen_height
        self._build_tilemap()
        self._build_camera()
        self._build_ui()

    # ── Tilemap ───────────────────────────────────────────────────────────────

    def _build_tilemap(self) -> None:
        """Create a 24×24 tilemap filled with a single light-grey tile."""
        # Generate a one-tile tileset (gris claro)
        light_grey = Color(*TILE_COLOR)
        self._tileset = TileSet.generate_tileset_from_colors(
            [light_grey],
            tile_size=(TILE_SIZE, TILE_SIZE),
            columns=1,
        )

        self._tilemap = TileMap(
            width=MAP_W, height=MAP_H,
            tile_size=(TILE_SIZE, TILE_SIZE),
        )
        self._tilemap.add_tileset(0, self._tileset)

        # Fill every cell with tile 0
        for ty in range(MAP_H):
            for tx in range(MAP_W):
                self._tilemap.set_tile(tx, ty, tile_id=0, tileset_id=0, layer=0)

    # ── Camera ────────────────────────────────────────────────────────────────

    def _build_camera(self) -> None:
        world_w = MAP_W * TILE_SIZE
        world_h = MAP_H * TILE_SIZE
        vp_w = self._screen_w - PANEL_W

        self._camera = Camera(
            x=max(0.0, (world_w - vp_w) / 2),
            y=max(0.0, (world_h - self._screen_h) / 2),
            width=self._screen_w,
            height=self._screen_h,
            zoom=1.0,
            min_zoom=0.5,
            max_zoom=8.0,
        )

    # ── UI ────────────────────────────────────────────────────────────────────

    # Heights of the fixed top section
    _TOP_H = 280   # px – controls + info + hints

    def _build_ui(self) -> None:
        sw, sh = self._screen_w, self._screen_h
        self._ui = UIManager(sw, sh)

        content_w = PANEL_W - 24

        # ── Top controls (scroll view so they don't overflow on tiny screens) ──
        top_sv = ScrollView(
            x=0, y=0, width=PANEL_W, height=self._TOP_H,
            bg_color=PANEL_BG,
            scroll_speed=24,
            show_scrollbar=False,
            padding=12,
        )

        vbox = VBox(
            width=content_w, spacing=10,
            align=VBox.ALIGN_LEFT, auto_size=True, padding=0,
        )

        vbox.add_child(_lbl("Character Scene", size=18, color=TITLE_COLOR))
        vbox.add_child(_lbl("─" * 22, size=12))

        btn_spawn = _btn("Spawn Personaje", BTN_SPAWN_BG, BTN_SPAWN_HV, w=content_w)
        btn_spawn.on_click(lambda _: self._spawn_character())
        vbox.add_child(btn_spawn)

        vbox.add_child(_lbl(""))

        vbox.add_child(_lbl("Obstáculos", size=16, color=TITLE_COLOR))

        density_row = HBox(
            width=content_w, height=28,
            spacing=8, align="center", auto_size=False,
        )
        density_row.add_child(_lbl("Densidad:"))
        self._density_input = _numeric(
            0.20, min_v=0.0, max_v=1.0, step=0.05, w=content_w - 80,
        )
        density_row.add_child(self._density_input)
        vbox.add_child(density_row)

        btn_obstacles = _btn(
            "Aleatorizar obstáculos", BTN_OBS_BG, BTN_OBS_HV, w=content_w,
        )
        btn_obstacles.on_click(lambda _: self._randomize_obstacles())
        vbox.add_child(btn_obstacles)

        vbox.add_child(_lbl(""))
        vbox.add_child(_lbl("─" * 22, size=12))
        self._info_chars     = _lbl("Personajes: 0")
        self._info_obstacles = _lbl("Obstáculos: 0")
        vbox.add_child(self._info_chars)
        vbox.add_child(self._info_obstacles)

        vbox.add_child(_lbl(""))
        vbox.add_child(_lbl("Controles:", size=14, color=TITLE_COLOR))
        vbox.add_child(_lbl("WASD / ↑↓←→: mover", size=13))
        vbox.add_child(_lbl("Q / E  o rueda: zoom", size=13))
        vbox.add_child(_lbl("ESC: salir", size=13))

        top_sv.add_child(vbox)
        self._ui.add(top_sv)

        # ── Character list (fills the rest of the panel) ──
        list_y = self._TOP_H
        list_h = sh - list_y
        self._char_list = SelectableList(
            x=0, y=list_y,
            width=PANEL_W,
            height=max(60, list_h),
            title="Personajes",
            item_height=26,
            font_size=15,
            auto_scroll=True,
            bg_color=(24, 24, 40, 250),
            item_normal=(38, 38, 58),
            item_hover=(55, 55, 80),
            item_selected=(50, 95, 170),
            item_text=(200, 200, 220),
            item_text_sel=(255, 255, 255),
            item_accent=(80, 140, 255),
            border_radius=4,
            border_color=(60, 60, 90),
            border_width=1,
            title_color=TITLE_COLOR,
            title_font_size=15,
        )
        self._char_list.on_select(self._on_char_list_select)
        # Populate with any characters already spawned (e.g. after resize rebuild)
        for char in self._characters:
            self._char_list.add_item(char.name)
        self._ui.add(self._char_list)

    # ── Selection ─────────────────────────────────────────────────────────────

    def _on_char_list_select(self, index: int, label: str) -> None:
        """Called when a list item is clicked."""
        # Deselect previous
        if self._selected_char is not None:
            self._selected_char.shape.selected = False

        if index < 0 or index >= len(self._characters):
            self._selected_char = None
            return

        char = self._characters[index]
        char.shape.selected = True
        self._selected_char = char

    # ── Game actions ──────────────────────────────────────────────────────────

    def _spawn_character(self) -> None:
        """Spawn a character at a random free tile cell on the map."""
        free_tiles = [
            (tx, ty)
            for tx in range(MAP_W)
            for ty in range(MAP_H)
            if (tx, ty) not in self._obstacles
        ]
        if not free_tiles:
            print("[CharacterScene] No free tiles available for spawn.")
            return

        tx, ty = random.choice(free_tiles)
        char_h = random.randint(CHAR_H_MIN, CHAR_H_MAX)
        fill, border = _random_char_color()

        char = GameCharacter(
            x=0, y=0,
            name=f"char_{len(self._characters)}",
            grid_pos=(tx, ty),
            move_speed=CHAR_MOVE_SPEED,
            tile_w=TILE_SIZE,
            tile_h=TILE_SIZE,
        )
        char.shape = RectShape(
            width=CHAR_W,
            height=char_h,
            color=fill,
            border_color=border,
            border_width=1,
        )
        # Attach a movement component driven by the scene's obstacle set
        from core.character.movement_component import MovementComponent
        char._movement = MovementComponent(
            is_walkable_fn=self._is_walkable,
            move_speed=CHAR_MOVE_SPEED,
            tile_w=TILE_SIZE,
            tile_h=TILE_SIZE,
        )
        char._movement.set_cell((tx, ty))
        # Sync initial pixel position
        char.x = char._movement.pixel_x + (TILE_SIZE - CHAR_W) / 2
        char.y = char._movement.pixel_y + TILE_SIZE - char_h - 2

        self._characters.append(char)
        self._char_cells[id(char)] = (tx, ty)
        if self._char_list:
            self._char_list.add_item(char.name)
        self._update_info()
        print(f"[CharacterScene] Spawned '{char.name}' at cell ({tx},{ty}), "
              f"h={char_h}px, color=({fill.r},{fill.g},{fill.b})")

    def _randomize_obstacles(self, density: Optional[float] = None) -> None:
        """Randomly assign obstacle cells based on density.

        If *density* is None the value is read from the density input widget.
        Characters that are already spawned on a cell that becomes an obstacle
        are NOT evicted — they simply stay, but future spawns will avoid those
        cells.
        """
        if density is None:
            density = DEFAULT_OBSTACLE_DENSITY
            if self._density_input:
                try:
                    density = float(self._density_input.text)
                    density = max(0.0, min(1.0, density))
                except ValueError:
                    pass

        self._obstacles.clear()
        total_cells = MAP_W * MAP_H
        n_obstacles = int(total_cells * density)

        all_tiles = [(tx, ty) for tx in range(MAP_W) for ty in range(MAP_H)]
        chosen = random.sample(all_tiles, min(n_obstacles, len(all_tiles)))
        self._obstacles = set(chosen)

        # Rebuild obstacle surface
        self._build_obstacle_surf()
        self._update_info()
        print(f"[CharacterScene] {len(self._obstacles)} obstáculos (densidad={density:.2f})")

    def _build_obstacle_surf(self) -> None:
        """Pre-render obstacle cells into a cached surface at world resolution."""
        world_w = MAP_W * TILE_SIZE
        world_h = MAP_H * TILE_SIZE
        surf = pygame.Surface((world_w, world_h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))

        color = OBSTACLE_COLOR  # (r, g, b, a)
        for (tx, ty) in self._obstacles:
            rect = pygame.Rect(tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surf, color, rect)

        self._obstacle_surf = surf

    def _is_walkable(self, pos: tuple) -> bool:
        """Walkability predicate passed to pathfinding: in-bounds and not an obstacle."""
        tx, ty = pos
        return (0 <= tx < MAP_W and 0 <= ty < MAP_H
                and (tx, ty) not in self._obstacles)

    def _move_selected_to(self, tile_x: int, tile_y: int) -> None:
        """Order the selected character to move to (tile_x, tile_y) via A*."""
        char = self._selected_char
        if char is None:
            return
        if not self._is_walkable((tile_x, tile_y)):
            print(f"[CharacterScene] Cell ({tile_x},{tile_y}) is not walkable.")
            return
        ok = char.move_to_cell(
            (tile_x, tile_y),
            is_walkable_fn=self._is_walkable,
            move_speed=CHAR_MOVE_SPEED,
        )
        if ok:
            print(f"[CharacterScene] '{char.name}' moving to ({tile_x},{tile_y})")
        else:
            print(f"[CharacterScene] No path from {char.grid_position} to ({tile_x},{tile_y})")

    def _update_info(self) -> None:
        if self._info_chars:
            self._info_chars.text = f"Personajes: {len(self._characters)}"
        if self._info_obstacles:
            self._info_obstacles.text = f"Obstáculos: {len(self._obstacles)}"

    # ── Events ────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.running = False
            return

        # Mouse-wheel zoom centred on cursor
        if event.type == pygame.MOUSEWHEEL and self._camera:
            mx, my = pygame.mouse.get_pos()
            if mx > PANEL_W:
                factor = 1.1 if event.y > 0 else (1 / 1.1)
                self._camera.zoom_at_point(mx - PANEL_W, my, factor)

        # Right-click → move selected character
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3
                and self._camera and self._selected_char):
            mx, my = event.pos
            if mx > PANEL_W:
                zoom = self._camera.zoom
                wx = (mx - PANEL_W) / zoom + self._camera.x
                wy = my / zoom + self._camera.y
                tile_x = int(wx / TILE_SIZE)
                tile_y = int(wy / TILE_SIZE)
                if 0 <= tile_x < MAP_W and 0 <= tile_y < MAP_H:
                    self._move_selected_to(tile_x, tile_y)
                    return   # don't forward right-click to UI

        if self._ui:
            self._ui.handle_event(event)

    # handle_events is called from BaseScene-style runners
    def handle_events(self, events: list) -> None:
        for event in events:
            self.handle_event(event)

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        if self._ui:
            self._ui.update(dt)

        for char in self._characters:
            char.update(dt)
            # Keep _char_cells in sync (grid_x/y updated by _on_step inside update)
            self._char_cells[id(char)] = (char.grid_x, char.grid_y)

        if not self._camera:
            return

        keys = pygame.key.get_pressed()

        # Zoom with keyboard
        if keys[pygame.K_e]:
            self._camera.zoom *= ZOOM_SPEED ** dt
        elif keys[pygame.K_q]:
            self._camera.zoom /= ZOOM_SPEED ** dt

        zoom = self._camera.zoom
        world_w = MAP_W * TILE_SIZE
        world_h = MAP_H * TILE_SIZE
        vp_w = (self._camera.width - PANEL_W) / zoom
        vp_h = self._camera.height / zoom

        self._camera.set_bounds(
            min_x=0.0, max_x=max(0.0, world_w - vp_w),
            min_y=0.0, max_y=max(0.0, world_h - vp_h),
        )

        # Don't move camera with arrow keys while the character list has focus
        list_focused = (
            self._char_list is not None and self._char_list._state.focused
        )

        speed = CAMERA_SPEED / zoom
        dx = dy = 0.0
        if not list_focused:
            if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx -= speed * dt
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += speed * dt
            if keys[pygame.K_UP]    or keys[pygame.K_w]: dy -= speed * dt
            if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy += speed * dt
        if dx or dy:
            self._camera.move(dx, dy)

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(BG_COLOR)
        sw, sh = screen.get_size()

        # ── Tilemap (right side) ──
        vp_w = sw - PANEL_W
        if self._tilemap and self._camera and self._tileset and vp_w > 0:
            viewport_rect = pygame.Rect(PANEL_W, 0, vp_w, sh)
            old_clip = screen.get_clip()
            screen.set_clip(viewport_rect)

            # Draw tilemap onto a subsurface so the camera coords are correct
            sub = screen.subsurface(viewport_rect)
            self._tilemap.draw(sub, self._camera, self._tileset)

            # Draw obstacle overlay
            self._draw_obstacles(screen, viewport_rect)

            # Draw path overlay for selected character
            self._draw_path_overlay(screen, viewport_rect)

            # Draw characters
            self._draw_characters(screen, viewport_rect)

            screen.set_clip(old_clip)

            # HUD
            self._draw_hud(screen)
        else:
            font = pygame.font.Font(None, 22)
            txt = font.render("Cargando tilemap…", True, (80, 80, 100))
            screen.blit(txt, (PANEL_W + 20, sh // 2))

        # ── UI panel ──
        if self._ui:
            self._ui.draw(screen)

        # Divider
        pygame.draw.rect(
            screen, (65, 65, 90),
            pygame.Rect(PANEL_W - DIVIDER_W // 2, 0, DIVIDER_W, sh),
        )

    def _draw_obstacles(
        self, screen: pygame.Surface, viewport: pygame.Rect
    ) -> None:
        """Blit the pre-rendered obstacle surface, scaled by camera zoom."""
        if not self._obstacle_surf or not self._camera:
            return

        cam   = self._camera
        zoom  = cam.zoom
        world_w = MAP_W * TILE_SIZE
        world_h = MAP_H * TILE_SIZE

        # Scale the obstacle surface to current zoom
        scaled_w = max(1, int(world_w * zoom))
        scaled_h = max(1, int(world_h * zoom))
        scaled = pygame.transform.scale(self._obstacle_surf, (scaled_w, scaled_h))

        # Camera offset relative to the viewport origin
        dest_x = int(-cam.x * zoom) + viewport.x
        dest_y = int(-cam.y * zoom)

        old_clip = screen.get_clip()
        screen.set_clip(viewport)
        screen.blit(scaled, (dest_x, dest_y))
        screen.set_clip(old_clip)

    def _draw_path_overlay(
        self, screen: pygame.Surface, viewport: pygame.Rect
    ) -> None:
        """Draw the planned path of the selected character."""
        char = self._selected_char
        if char is None or not self._camera:
            return
        path = char._movement.remaining_path if char._movement else []
        if not path:
            return

        cam  = self._camera
        zoom = cam.zoom
        old_clip = screen.get_clip()
        screen.set_clip(viewport)

        cell_px = max(1, int(TILE_SIZE * zoom))
        for i, (tx, ty) in enumerate(path):
            sx = int((tx * TILE_SIZE - cam.x) * zoom) + viewport.x
            sy = int((ty * TILE_SIZE - cam.y) * zoom)
            color = PATH_DEST_COLOR if i == len(path) - 1 else PATH_COLOR
            cell_surf = pygame.Surface((cell_px, cell_px), pygame.SRCALPHA)
            cell_surf.fill(color)
            screen.blit(cell_surf, (sx, sy))

        screen.set_clip(old_clip)

    def _draw_characters(
        self, screen: pygame.Surface, viewport: pygame.Rect
    ) -> None:
        """Render all characters at their smooth world positions."""
        if not self._characters or not self._camera:
            return

        cam  = self._camera
        zoom = cam.zoom

        old_clip = screen.get_clip()
        screen.set_clip(viewport)

        for char in self._characters:
            # char.x / char.y are kept up to date by BaseCharacter.update()
            sx = int((char.x - cam.x) * zoom) + viewport.x
            sy = int((char.y - cam.y) * zoom)
            cw = max(1, int(char.shape.width  * zoom))
            ch = max(1, int(char.shape.height * zoom))
            rect = pygame.Rect(sx, sy, cw, ch)
            if not viewport.colliderect(rect):
                continue

            # Fill
            pygame.draw.rect(screen, char.shape.color.to_rgba(), rect)
            # Border
            if char.shape.border_width > 0 and char.shape.border_color:
                pygame.draw.rect(screen, char.shape.border_color.to_rgba(),
                                 rect, max(1, char.shape.border_width))
            # Selection outline
            if char.shape.selected:
                sel = rect.inflate(4, 4)
                pygame.draw.rect(screen, char.shape.selection_color.to_rgba(), sel, 2)

        screen.set_clip(old_clip)

    def _draw_hud(self, screen: pygame.Surface) -> None:
        cam  = self._camera
        font = pygame.font.Font(None, 18)

        # Top-left info bar
        info = (
            f"Tilemap {MAP_H}×{MAP_W}  |  "
            f"Cam ({int(cam.x)},{int(cam.y)})  |  "
            f"Zoom {cam.zoom:.2f}×"
        )
        surf = font.render(info, True, (190, 190, 200))
        screen.blit(surf, (PANEL_W + 8, 6))

        # Tile under cursor
        mx, my = pygame.mouse.get_pos()
        if mx > PANEL_W:
            zoom   = cam.zoom
            wx     = (mx - PANEL_W) / zoom + cam.x
            wy     = my / zoom + cam.y
            tile_x = int(wx / TILE_SIZE)
            tile_y = int(wy / TILE_SIZE)
            if 0 <= tile_x < MAP_W and 0 <= tile_y < MAP_H:
                is_obs = (tile_x, tile_y) in self._obstacles
                tag    = "  [OBSTÁCULO]" if is_obs else ""
                cell_txt = f"Celda ({tile_x},{tile_y}){tag}"
                c_surf = font.render(cell_txt, True, (255, 200, 80) if is_obs else (200, 200, 200))
                screen.blit(c_surf, (PANEL_W + 8, 24))

        hint = "WASD/Flechas: cámara  |  Q/E o rueda: zoom  |  Clic dcho: mover seleccionado  |  ESC: salir"
        h_surf = font.render(hint, True, (100, 100, 120))
        screen.blit(h_surf, (PANEL_W + 8, screen.get_height() - 20))

