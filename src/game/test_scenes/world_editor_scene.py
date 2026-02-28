"""
World Editor Scene – visualise and edit VGWorld generation parameters.

Layout
──────
Left panel (resizable via divider)
  ┌──────────────────────────────────┐
  │ [Parámetros] [Noises] [Matrices] │  ← TabBar
  ├──────────────────────────────────┤
  │  (scrollable content per tab)    │
  └──────────────────────────────────┘
Right area: grayscale tilemap viewer (Camera + TileMap)

Tabs
────
• Parámetros – all WorldParameterName values as editable NumericInputs.
              "Aplicar" syncs them to the VGWorld object.
• Noises     – sub-tabs per noise from config.json; shows key fields and a
              "Previsualizar" button that renders the noise in the tilemap.
• Matrices   – list of WorldMatrixName entries; each row has a "Generar"
              button that generates a preview-size matrix and shows it.
"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pygame

from src.core.tilemap.tilemap import TileMap
from src.core.tilemap.tileset import TileSet
from src.core.camera.camera import Camera
from src.ui import (
    UIManager, Label, Button, Checkbox, Dropdown,
    VBox, HBox, ScrollView, NumericInput, TabBar,
)
from .base_scene import BaseScene

# ── Lazy imports ─────────────────────────────────────────────────────────────
_Matrix2D = None
_NoiseGenerator2D = None
_VGWorld = None
_WorldParameterName = None
_WorldNoiseName = None
_WorldMatrixName = None


def _get_Matrix2D():
    global _Matrix2D
    if _Matrix2D is None:
        from virigir_math_utilities.matrix.matrix2d import Matrix2D
        _Matrix2D = Matrix2D
    return _Matrix2D


def _get_NoiseGenerator2D():
    global _NoiseGenerator2D
    if _NoiseGenerator2D is None:
        from virigir_math_utilities.noise.generators.noise2d import NoiseGenerator2D
        _NoiseGenerator2D = NoiseGenerator2D
    return _NoiseGenerator2D


def _get_world_classes():
    global _VGWorld, _WorldParameterName, _WorldNoiseName, _WorldMatrixName
    if _VGWorld is None:
        from vgworld.world.world import (
            VGWorld, WorldParameterName, WorldNoiseName, WorldMatrixName,
        )
        _VGWorld = VGWorld
        _WorldParameterName = WorldParameterName
        _WorldNoiseName = WorldNoiseName
        _WorldMatrixName = WorldMatrixName
    return _VGWorld, _WorldParameterName, _WorldNoiseName, _WorldMatrixName


# ── Config paths ──────────────────────────────────────────────────────────────
_ROOT = Path(__file__).parent.parent.parent.parent
CONFIG_JSON  = _ROOT / "configs" / "config.json"
CONFIG_TOML  = _ROOT / "configs" / "world_configs.toml"

# ── Visual constants ──────────────────────────────────────────────────────────
PANEL_WIDTH    = 420
TAB_H          = 36
SCROLL_PAD     = 10
SCROLLBAR_W    = 12
ROW_LABEL_W    = 152
ROW_SPACING    = 8
GRAYSCALE_STEPS = 32
TILE_SIZE       = 4
CAMERA_SPEED    = 500
ZOOM_SPEED      = 1.5
_PANEL_MIN_W    = 180
_DIVIDER_W      = 4
_DIVIDER_HIT_W  = 10
BOTTOM_BAR_H    = 46   # fixed bottom bar height (holds "Previsualizar")

PANEL_BG      = (28, 28, 42, 245)
SECTION_BG    = (38, 38, 55, 200)
LABEL_COLOR   = (185, 185, 210)
TITLE_COLOR   = (215, 215, 255)
VALUE_COLOR   = (130, 200, 130)
INPUT_BG      = (48, 48, 62)
INPUT_BORDER  = (95, 95, 128)
FOCUS_BORDER  = (95, 155, 255)
BTN_GEN_BG    = (48, 125, 78)
BTN_GEN_HV    = (68, 155, 98)
BTN_PRV_BG    = (55, 85, 155)
BTN_PRV_HV    = (75, 110, 185)
BTN_APL_BG    = (130, 90, 40)
BTN_APL_HV    = (165, 115, 60)

# ── Noise types ───────────────────────────────────────────────────────────────
_NOISE_TYPE_NAMES  = ["PERLIN", "SIMPLEX", "SIMPLEX_SMOOTH", "CELLULAR", "VALUE_CUBIC", "VALUE"]
_FRACTAL_TYPE_NAMES = ["NONE", "FBM", "RIDGED", "PING_PONG"]

# Editable noise fields: (label, config_key, widget_type, *args)
# widget_type: 'int' | 'float' | 'dropdown' | 'bool'
_NOISE_FIELD_CONFIG = [
    ("Seed",            "seed",                       'int',      0,      2**31-1, 1),
    ("Noise Type",      "noise_type",                 'dropdown', _NOISE_TYPE_NAMES, None, None),
    ("Frequency",       "frequency",                  'float',    0.0001, 10.0,    0.001),
    ("Offset X",        "offset_x",                   'int',      -10000, 10000,   10),
    ("Offset Y",        "offset_y",                   'int',      -10000, 10000,   10),
    ("Fractal Type",    "fractal_type",               'dropdown', _FRACTAL_TYPE_NAMES, None, None),
    ("Octaves",         "octaves",                    'int',      1,      16,      1),
    ("Lacunarity",      "lacunarity",                 'float',    0.1,    8.0,     0.1),
    ("Persistence",     "persistence",                'float',    0.0,    1.0,     0.05),
    ("Weighted Str.",   "weighted_strength",          'float',    -1.0,   2.0,     0.05),
    ("Domain Warp",     "domain_warp_enabled",        'bool',     None,   None,    None),
    ("DW Amplitude",    "domain_warp_amplitude",      'float',    0.0,    500.0,   1.0),
    ("DW Frequency",    "domain_warp_frequency",      'float',    0.0001, 1.0,     0.005),
    ("DW Octaves",      "domain_warp_fractal_octaves",'int',      1,      16,      1),
]

# WorldParameterName display config: (label, is_int, min, max, step)
_PARAM_CONFIG: Dict[str, tuple] = {
    "global_seed":              ("Global Seed",           True,  0,      2**31-1, 1),
    "world_size_x":             ("World Size X",          True,  1,      8192,    16),
    "world_size_y":             ("World Size Y",          True,  1,      8192,    16),
    "equator_latitude":         ("Equator Latitude",      True,  -90,    90,      1),
    "min_continental_height":   ("Min. Continental H.",   False, 0.0,    1.0,     0.001),
    "peaks_and_valleys_scale":  ("PV Scale",              False, 0.0,    10.0,    0.01),
    "continental_scale":        ("Continental Scale",     False, 0.0,    10.0,    0.01),
    "sea_scale":                ("Sea Scale",             False, 0.0,    10.0,    0.01),
    "sea_elevation_threshold":  ("Sea Threshold",         False, 0.0,    1.0,     0.001),
    "island_scale":             ("Island Scale",          False, 0.0,    1.0,     0.01),
    "volcanic_island_scale":    ("Volcanic Island Scale", False, 0.0,    1.0,     0.01),
    "island_threshold":         ("Island Threshold",      False, 0.0,    1.0,     0.01),
    "out_to_sea_factor":        ("Out to Sea Factor",     False, 0.0,    1.0,     0.01),
}

# WorldMatrixName → (display label, noise key to generate from, binarize?)
_MATRIX_CONFIG: Dict[str, tuple] = {
    "continental_elevation": ("Continental Elevation", "base_elevation",  False),
    "elevation":             ("Elevation",             "base_elevation",  False),
    "is_volcanic_land":      ("Is Volcanic Land",      "volcanic_noise",  True),
    "is_continent":          ("Is Continent",          "base_elevation",  True),
    "latitude":              ("Latitude",              None,              False),
    "river":                 ("River",                 None,              False),
    "river_birth_positions": ("River Birth Positions", None,              False),
    "river_flow":            ("River Flow",            None,              False),
    "temperature":           ("Temperature",           None,              False),
}


# ── Helper widget factories ───────────────────────────────────────────────────

def _lbl(text: str, font_size: int = 16, color=LABEL_COLOR) -> Label:
    return Label(text=text, font_size=font_size, color=color, auto_size=True)


def _title(text: str) -> Label:
    return Label(text=text, font_size=19, color=TITLE_COLOR, auto_size=True)


def _spacer() -> Label:
    return Label(text="", font_size=6, auto_size=True)


def _numeric(value, *, min_value, max_value, step, w=90) -> NumericInput:
    return NumericInput(
        width=w, height=26, value=value,
        min_value=min_value, max_value=max_value, step=step,
        font_size=16, bg_color=INPUT_BG, text_color=(255, 255, 255),
        border_color=INPUT_BORDER, focus_border_color=FOCUS_BORDER,
        border_radius=4,
    )


def _btn(text, bg, hv, w=120, h=30) -> Button:
    return Button(
        width=w, height=h, text=text, font_size=16,
        bg_color=bg, hover_color=hv,
        pressed_color=tuple(max(0, c - 25) for c in bg),
        border_radius=5,
    )


def _row(label_text: str, widget, content_w: int) -> HBox:
    widget_w = max(50, content_w - ROW_LABEL_W - ROW_SPACING)
    widget.width = widget_w
    row = HBox(width=content_w, height=widget.height,
                spacing=ROW_SPACING, align='center', auto_size=False)
    lbl = _lbl(label_text)
    lbl.width = ROW_LABEL_W
    row.add_child(lbl)
    row.add_child(widget)
    return row


def _dropdown_small(options: List[str], index: int = 0, w: int = 150) -> Dropdown:
    return Dropdown(
        width=w, height=26, options=options, selected_index=index,
        font_size=15, bg_color=INPUT_BG, text_color=(255, 255, 255),
        border_color=INPUT_BORDER, selected_color=(45, 115, 70),
        hover_color=(60, 60, 80), max_visible=6,
        border_radius=4,
    )


def _make_noise_widget(field_type: str, config_value, arg0, arg1, arg2):
    """Create the right widget for a noise field."""
    if field_type == 'int':
        val = int(config_value) if config_value is not None else int(arg0)
        return _numeric(val, min_value=arg0, max_value=arg1, step=arg2)
    elif field_type == 'float':
        val = float(config_value) if config_value is not None else float(arg0)
        return _numeric(val, min_value=arg0, max_value=arg1, step=arg2)
    elif field_type == 'dropdown':
        options = arg0  # arg0 is the list
        if isinstance(config_value, int):
            idx = max(0, min(config_value, len(options) - 1))
        elif isinstance(config_value, str):
            upper = config_value.upper()
            idx = options.index(upper) if upper in options else 0
        else:
            idx = 0
        return _dropdown_small(options, idx)
    elif field_type == 'bool':
        return Checkbox(checked=bool(config_value), box_size=18,
                        text_color=LABEL_COLOR, font_size=16)
    return Label(text=str(config_value), auto_size=True)


def _read_noise_widget(widget, field_type: str):
    """Read the current value from an editable noise widget."""
    if field_type == 'int':
        try:
            return int(float(widget.text))
        except (ValueError, AttributeError):
            return 0
    elif field_type == 'float':
        try:
            return float(widget.text)
        except (ValueError, AttributeError):
            return 0.0
    elif field_type == 'dropdown':
        return widget.selected_index
    elif field_type == 'bool':
        return 1 if widget.checked else 0
    return 0


# ═══════════════════════════════════════════════════════════════════════════════
# Scene
# ═══════════════════════════════════════════════════════════════════════════════

class WorldEditorScene(BaseScene):
    """Editor that exposes VGWorld parameters, noise preview, and matrix generation."""

    TABS = ["Parámetros", "Noises", "Matrices"]
    TAB_PARAMS   = 0
    TAB_NOISES   = 1
    TAB_MATRICES = 2

    def __init__(self):
        super().__init__(
            name="World Editor",
            description="Edit VGWorld parameters and visualise generation results",
        )
        self.running = True

        # World data
        self._world = None               # VGWorld instance (or None on failure)
        self._noise_configs: Dict[str, Dict[str, Any]] = {}   # from config.json
        self._noise_names: List[str] = []

        # UI
        self._ui: Optional[UIManager] = None
        self._main_tab_bar: Optional[TabBar] = None
        self._scroll_view: Optional[ScrollView] = None
        self._active_tab: int = 0

        # Per-tab VBoxes (built lazily, cached)
        self._tab_vboxes: List[Optional[VBox]] = [None, None, None]

        # Params tab controls
        self._param_controls: Dict[str, NumericInput] = {}
        self._param_status: Optional[Label] = None

        # Noises tab state
        self._noise_sub_bar: Optional[TabBar] = None
        self._noise_inner_scroll: Optional[ScrollView] = None
        self._active_noise_idx: int = 0
        self._noise_tab_vboxes: Dict[str, VBox] = {}   # noise_name → VBox (cached)
        self._noise_controls: Dict[str, Dict[str, tuple]] = {}  # noise_name → {key: (widget, type)}

        # Matrices tab controls
        self._preview_w: Optional[NumericInput] = None
        self._preview_h: Optional[NumericInput] = None
        self._matrix_status: Dict[str, Label] = {}
        self._matrix_generated: Dict[str, bool] = {}
        self._generated_matrices: Dict[str, Any] = {}   # mat_key → Matrix2D
        self._matrix_view_buttons: Dict[str, Button] = {}

        # Fixed bottom bar
        self._bottom_bar = None
        self._preview_btn: Optional[Button] = None

        # Viewer
        self._tilemap: Optional[TileMap] = None
        self._tileset: Optional[TileSet] = None
        self._camera: Optional[Camera] = None
        self._current_matrix = None   # Matrix2D shown in viewer
        self._viewer_label: str = ""
        self._map_w: int = 0
        self._map_h: int = 0

        # General status
        self._status_bar: Optional[Label] = None

        # Divider
        self._panel_width: int = PANEL_WIDTH
        self._dragging_divider: bool = False
        self._divider_start_x: int = 0
        self._divider_start_panel_w: int = 0

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def on_enter(self) -> None:
        self._load_data()
        screen = pygame.display.get_surface()
        sw, sh = screen.get_size()
        self._build_ui(sw, sh)

    def on_exit(self) -> None:
        self._tilemap = None
        self._tileset = None
        self._camera = None
        self._current_matrix = None

    def on_resize(self, sw: int, sh: int) -> None:
        if self._ui:
            self._ui.resize(sw, sh)
        if self._main_tab_bar:
            self._main_tab_bar.width = self._panel_width
        if self._scroll_view:
            self._scroll_view.height = sh - TAB_H - BOTTOM_BAR_H
        if self._bottom_bar:
            self._bottom_bar.y = sh - BOTTOM_BAR_H
            self._bottom_bar.width = self._panel_width
        if self._status_bar:
            self._status_bar.x = self._panel_width + 8
            self._status_bar.y = sh - 20
        if self._camera:
            self._camera.width = sw
            self._camera.height = sh

    # ── Data loading ──────────────────────────────────────────────────────────

    def _load_data(self) -> None:
        # Noise configs from config.json
        try:
            with open(CONFIG_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._noise_configs = data.get("noise", {})
            self._noise_names = list(self._noise_configs.keys())
        except Exception as e:
            print(f"[WorldEditor] config.json load error: {e}")

        # VGWorld
        try:
            VGWorld, *_ = _get_world_classes()
            self._world = VGWorld("default_parameters")
            print("[WorldEditor] VGWorld loaded.")
        except Exception as e:
            print(f"[WorldEditor] VGWorld unavailable: {e}")
            self._world = None

    # ── UI construction ───────────────────────────────────────────────────────

    def _panel_content_w(self) -> int:
        return max(60, self._panel_width - 2 * SCROLL_PAD - SCROLLBAR_W)

    def _build_ui(self, sw: int, sh: int) -> None:
        self._ui = UIManager(sw, sh)
        pw = self._panel_width

        # Main TabBar
        self._main_tab_bar = TabBar(
            x=0, y=0, width=pw, height=TAB_H,
            tabs=self.TABS,
            selected_index=self._active_tab,
            font_size=17,
        )
        self._main_tab_bar.on_tab_change(self._on_main_tab_change)
        self._ui.add(self._main_tab_bar)

        # ScrollView for tab content (leaves room for the fixed bottom bar)
        self._scroll_view = ScrollView(
            x=0, y=TAB_H, width=pw, height=sh - TAB_H - BOTTOM_BAR_H,
            bg_color=PANEL_BG,
            scroll_speed=30,
            show_scrollbar=True,
            scrollbar_color=(105, 105, 138),
            scrollbar_track_color=(42, 42, 58),
            padding=SCROLL_PAD,
        )
        self._ui.add(self._scroll_view)

        # ── Fixed bottom bar: always-visible "Previsualizar" button ──────────
        bar_y = sh - BOTTOM_BAR_H
        self._bottom_bar = HBox(
            x=0, y=bar_y, width=pw, height=BOTTOM_BAR_H,
            spacing=10, align='center', justify='center', auto_size=False,
            bg_color=(32, 32, 48, 255),
        )
        self._preview_btn = _btn("Previsualizar", BTN_PRV_BG, BTN_PRV_HV, w=160, h=34)
        self._preview_btn.on_click(lambda _: self._preview_selected_noise())
        self._bottom_bar.add_child(self._preview_btn)
        self._ui.add(self._bottom_bar)

        # Status label below the bottom bar (right side of screen)
        self._status_bar = Label(
            text="", font_size=15, color=(255, 200, 80), auto_size=True,
        )
        self._status_bar.x = self._panel_width + 8
        self._status_bar.y = sh - 20
        self._ui.add(self._status_bar)

        # Show initial tab
        self._show_tab(self._active_tab)

    def _on_main_tab_change(self, idx: int) -> None:
        self._active_tab = idx
        self._show_tab(idx)

    def _show_tab(self, idx: int) -> None:
        """Swap the ScrollView content to the selected tab."""
        if self._scroll_view is None:
            return

        # Build tab content lazily
        if self._tab_vboxes[idx] is None:
            cw = self._panel_content_w()
            if idx == self.TAB_PARAMS:
                self._tab_vboxes[idx] = self._build_params_tab(cw)
            elif idx == self.TAB_NOISES:
                self._tab_vboxes[idx] = self._build_noises_tab(cw)
            elif idx == self.TAB_MATRICES:
                self._tab_vboxes[idx] = self._build_matrices_tab(cw)

        self._scroll_view.clear_children()
        vbox = self._tab_vboxes[idx]
        if vbox:
            self._scroll_view.add_child(vbox)
        # Reset scroll position
        self._scroll_view.scroll_y = 0

    # ═══════════════════════ TAB: PARÁMETROS ══════════════════════════════════

    def _build_params_tab(self, cw: int) -> VBox:
        vbox = VBox(width=cw, spacing=7, align=VBox.ALIGN_LEFT, auto_size=True, padding=0)

        vbox.add_child(_title("── Parámetros del Mundo ──"))
        vbox.add_child(_spacer())

        # Load current values
        raw_params: Dict[str, Any] = {}
        if self._world:
            _, WPN, *_ = _get_world_classes()
            for key, (label, is_int, mn, mx, step) in _PARAM_CONFIG.items():
                try:
                    enum_key = WPN[key]
                    raw_params[key] = self._world.parameters.get(enum_key, 0)
                except Exception:
                    pass
        else:
            try:
                with open(CONFIG_TOML, "rb") as f:
                    toml_data = tomllib.load(f)
                for k, v in toml_data.get("default_parameters", {}).items():
                    # map PascalCase TOML key → snake_case _PARAM_CONFIG key
                    snake = _pascal_to_snake(k)
                    raw_params[snake] = v
            except Exception:
                pass

        self._param_controls = {}
        for key, (label, is_int, mn, mx, step) in _PARAM_CONFIG.items():
            current = raw_params.get(key, mn)
            inp = _numeric(current, min_value=mn, max_value=mx, step=step)
            self._param_controls[key] = inp
            vbox.add_child(_row(label, inp, cw))

        vbox.add_child(_spacer())

        # Apply button
        btn_row = HBox(width=cw, height=32, spacing=12, align='center', justify='center', auto_size=False)
        btn_apply = _btn("Aplicar Cambios", BTN_APL_BG, BTN_APL_HV, w=160)
        btn_apply.on_click(lambda _: self._apply_params())
        btn_row.add_child(btn_apply)
        vbox.add_child(btn_row)

        vbox.add_child(_spacer())
        self._param_status = Label(text="", font_size=15, color=(255, 200, 80), auto_size=True)
        vbox.add_child(self._param_status)

        return vbox

    def _apply_params(self) -> None:
        if self._world is None:
            self._set_status("VGWorld no disponible")
            return
        try:
            _, WPN, *_ = _get_world_classes()
            for key, inp in self._param_controls.items():
                try:
                    enum_key = WPN[key]
                    _, is_int, *_ = _PARAM_CONFIG[key]
                    raw = inp.text
                    self._world.parameters[enum_key] = int(float(raw)) if is_int else float(raw)
                except Exception:
                    pass
            self._set_status("Parámetros aplicados al mundo.")
            if self._param_status:
                self._param_status.text = "✓ Cambios aplicados"
        except Exception as e:
            self._set_status(f"Error: {e}")

    # ═══════════════════════ TAB: NOISES ══════════════════════════════════════

    def _build_noises_tab(self, cw: int) -> VBox:
        outer = VBox(width=cw, spacing=8, align=VBox.ALIGN_LEFT, auto_size=True, padding=0)

        if not self._noise_names:
            outer.add_child(_lbl("No hay noises en config.json", color=(200, 100, 100)))
            return outer

        outer.add_child(_title("── Visualización de Noises ──"))
        outer.add_child(_spacer())

        # Sub-tab bar for each noise
        self._noise_sub_bar = TabBar(
            x=0, y=0, width=cw, height=32,
            tabs=self._noise_names,
            selected_index=self._active_noise_idx,
            font_size=15,
            active_bg_color=(45, 80, 140),
        )
        self._noise_sub_bar.on_tab_change(self._on_noise_sub_tab_change)
        outer.add_child(self._noise_sub_bar)

        # Inner scroll for editable noise fields (fills remaining space in the tab)
        inner_h = 420
        self._noise_inner_scroll = ScrollView(
            x=0, y=0, width=cw, height=inner_h,
            bg_color=(33, 33, 48, 220),
            scroll_speed=25,
            show_scrollbar=True,
            scrollbar_color=(95, 95, 128),
            scrollbar_track_color=(40, 40, 55),
            padding=SCROLL_PAD,
        )
        inner_cw = max(60, cw - 2 * SCROLL_PAD - SCROLLBAR_W)
        self._refresh_noise_view(self._active_noise_idx, inner_cw)
        outer.add_child(self._noise_inner_scroll)

        return outer

    def _on_noise_sub_tab_change(self, idx: int) -> None:
        self._active_noise_idx = idx
        if self._noise_inner_scroll is None or not self._noise_names:
            return
        inner_cw = self._panel_content_w() - 2 * SCROLL_PAD - SCROLLBAR_W
        self._refresh_noise_view(idx, max(60, inner_cw))

    def _refresh_noise_view(self, idx: int, inner_cw: int) -> None:
        """Swap _noise_inner_scroll content to the noise at idx, building lazily."""
        if self._noise_inner_scroll is None:
            return
        name = self._noise_names[idx] if idx < len(self._noise_names) else ""
        if name and name not in self._noise_tab_vboxes:
            self._noise_tab_vboxes[name] = self._build_noise_field_vbox(name, inner_cw)
        self._noise_inner_scroll.clear_children()
        if name in self._noise_tab_vboxes:
            self._noise_inner_scroll.add_child(self._noise_tab_vboxes[name])
        self._noise_inner_scroll.scroll_y = 0

    def _build_noise_field_vbox(self, name: str, inner_cw: int) -> VBox:
        """Build a VBox of editable widgets for one noise config, caching controls."""
        cfg = self._noise_configs.get(name, {})
        fields: Dict[str, tuple] = {}

        vbox = VBox(width=inner_cw, spacing=6, align=VBox.ALIGN_LEFT, auto_size=True, padding=0)
        vbox.add_child(_lbl(name, font_size=18, color=TITLE_COLOR))
        vbox.add_child(_spacer())

        for display_label, key, wtype, arg0, arg1, arg2 in _NOISE_FIELD_CONFIG:
            config_value = cfg.get(key)
            if config_value is None and wtype not in ('bool',):
                continue
            widget = _make_noise_widget(wtype, config_value, arg0, arg1, arg2)
            fields[key] = (widget, wtype)
            vbox.add_child(_row(display_label, widget, inner_cw))

        self._noise_controls[name] = fields
        return vbox

    def _preview_selected_noise(self) -> None:
        if not self._noise_names:
            self._set_status("No hay noises disponibles")
            return
        name = self._noise_names[self._active_noise_idx]
        # Build config from editable controls (if controls exist), else use raw config
        controls = self._noise_controls.get(name, {})
        cfg = dict(self._noise_configs.get(name, {}))  # start from saved config
        for key, (widget, wtype) in controls.items():
            cfg[key] = _read_noise_widget(widget, wtype)
        if not cfg:
            self._set_status(f"Noise '{name}' no encontrado")
            return
        pw, ph = self._get_preview_size()
        try:
            NoiseGenerator2D = _get_NoiseGenerator2D()
            Matrix2D = _get_Matrix2D()
            noise = NoiseGenerator2D.from_dict(cfg)
            matrix = Matrix2D.create_from_noise(noise, ph, pw)
            self._show_matrix(matrix, f"Noise: {name}", pw, ph)
            self._set_status(f"Previsualizado: {name}  ({ph}×{pw})")
        except Exception as e:
            self._set_status(f"Error: {e}")
            print(f"[WorldEditor] {e}")

    # ═══════════════════════ TAB: MATRICES ════════════════════════════════════

    def _build_matrices_tab(self, cw: int) -> VBox:
        vbox = VBox(width=cw, spacing=8, align=VBox.ALIGN_LEFT, auto_size=True, padding=0)

        vbox.add_child(_title("── Matrices del Mundo ──"))
        vbox.add_child(_spacer())

        # Preview size row
        size_row = HBox(width=cw, height=28, spacing=10, align='center', auto_size=False)
        size_row.add_child(_lbl("Tamaño preview:"))
        self._preview_w = _numeric(256, min_value=16, max_value=2048, step=16, w=115)
        self._preview_h = _numeric(256, min_value=16, max_value=2048, step=16, w=115)
        size_row.add_child(_lbl("X:"))
        size_row.add_child(self._preview_w)
        size_row.add_child(_lbl("Y:"))
        size_row.add_child(self._preview_h)
        vbox.add_child(size_row)

        vbox.add_child(_spacer())

        # One row per matrix
        self._matrix_status = {}
        self._matrix_view_buttons = {}
        # keep already-generated state across rebuilds
        for mat_key in _MATRIX_CONFIG:
            if mat_key not in self._matrix_generated:
                self._matrix_generated[mat_key] = False

        GEN_W, VER_W, STA_W = 72, 52, 80
        NAME_W = max(60, cw - GEN_W - VER_W - STA_W - 3 * 8)

        for mat_key, (mat_label, noise_key, do_binarize) in _MATRIX_CONFIG.items():
            row = HBox(width=cw, height=30, spacing=8, align='center', auto_size=False)

            name_lbl = _lbl(mat_label)
            name_lbl.width = NAME_W
            row.add_child(name_lbl)

            if noise_key is not None:
                btn_gen = _btn("Generar", BTN_GEN_BG, BTN_GEN_HV, w=GEN_W, h=26)
                def _make_gen(mk=mat_key, nk=noise_key, bz=do_binarize):
                    return lambda _: self._generate_matrix(mk, nk, bz)
                btn_gen.on_click(_make_gen())
            else:
                btn_gen = _btn("N/I", (55, 55, 55), (65, 65, 65), w=GEN_W, h=26)
                btn_gen.enabled = False
            row.add_child(btn_gen)

            # "Ver" button – enabled only after generation
            btn_ver = _btn("Ver", BTN_PRV_BG, BTN_PRV_HV, w=VER_W, h=26)
            btn_ver.enabled = self._matrix_generated.get(mat_key, False)
            def _make_ver(mk=mat_key):
                return lambda _: self._show_stored_matrix(mk)
            btn_ver.on_click(_make_ver())
            self._matrix_view_buttons[mat_key] = btn_ver
            row.add_child(btn_ver)

            status_lbl = _lbl("—", color=(120, 120, 140))
            status_lbl.width = STA_W
            self._matrix_status[mat_key] = status_lbl
            row.add_child(status_lbl)

            vbox.add_child(row)

        return vbox

    def _generate_matrix(self, mat_key: str, noise_key: str, binarize: bool) -> None:
        cfg = self._noise_configs.get(noise_key)
        if cfg is None:
            self._set_status(f"Noise '{noise_key}' no encontrado en config.json")
            return
        pw, ph = self._get_preview_size()
        try:
            NoiseGenerator2D = _get_NoiseGenerator2D()
            Matrix2D = _get_Matrix2D()
            noise = NoiseGenerator2D.from_dict(cfg)
            matrix = Matrix2D.create_from_noise(noise, ph, pw)
            if binarize and self._world:
                _, WPN, *_ = _get_world_classes()
                threshold = self._world.parameters.get(
                    WPN["island_threshold"], 0.5
                )
                matrix.binarize(threshold)
            elif binarize:
                matrix.binarize(0.5)
            self._matrix_generated[mat_key] = True
            self._generated_matrices[mat_key] = matrix
            btn_ver = self._matrix_view_buttons.get(mat_key)
            if btn_ver:
                btn_ver.enabled = True
            lbl = self._matrix_status.get(mat_key)
            if lbl:
                lbl.text = "✓ Listo"
                lbl.color = (100, 200, 100)
            mat_label = _MATRIX_CONFIG[mat_key][0]
            self._show_matrix(matrix, f"Matriz: {mat_label}", pw, ph)
            self._set_status(f"Generada: {mat_label}  ({ph}×{pw})")
        except Exception as e:
            self._set_status(f"Error: {e}")
            print(f"[WorldEditor] _generate_matrix: {e}")

    # ── Viewer helpers ────────────────────────────────────────────────────────

    def _get_preview_size(self):
        pw = ph = 256
        try:
            if self._preview_w:
                pw = max(16, min(2048, int(self._preview_w.text)))
            if self._preview_h:
                ph = max(16, min(2048, int(self._preview_h.text)))
        except ValueError:
            pass
        return pw, ph

    def _show_matrix(self, matrix, label: str, map_w: int, map_h: int) -> None:
        """Render a Matrix2D into the tilemap viewer."""
        self._current_matrix = matrix
        self._viewer_label = label
        self._map_w = map_w
        self._map_h = map_h

        # Tileset (shared, created once)
        if self._tileset is None:
            self._tileset = TileSet.generate_grayscale_tileset(
                nsteps=GRAYSCALE_STEPS,
                tile_size=(TILE_SIZE, TILE_SIZE),
                columns=GRAYSCALE_STEPS,
                white_to_black=True,
            )

        # Tilemap
        self._tilemap = TileMap(
            width=map_w, height=map_h,
            tile_size=(TILE_SIZE, TILE_SIZE),
        )
        self._tilemap.tileset = self._tileset

        tile_ids = np.clip(
            (matrix._data * (GRAYSCALE_STEPS - 1)).astype(int),
            0, GRAYSCALE_STEPS - 1,
        )
        for r in range(map_h):
            for c in range(map_w):
                self._tilemap.set_tile(c, r, int(tile_ids[r, c]))

        # Camera: create once, then preserve position/zoom
        screen = pygame.display.get_surface()
        sw, sh = screen.get_size()
        if self._camera is None:
            world_w = map_w * TILE_SIZE
            world_h = map_h * TILE_SIZE
            vp_w = sw - self._panel_width
            self._camera = Camera(
                x=max(0.0, (world_w - vp_w) / 2),
                y=max(0.0, (world_h - sh) / 2),
                width=sw, height=sh,
                zoom=1.0, min_zoom=0.05, max_zoom=20.0,
            )

    def _set_status(self, text: str) -> None:
        if self._status_bar:
            self._status_bar.text = text

    # ── Events ────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.running = False
            return

        # Divider drag
        screen = pygame.display.get_surface()
        sw = screen.get_width()
        divx = self._panel_width

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if abs(event.pos[0] - divx) <= _DIVIDER_HIT_W // 2:
                self._dragging_divider = True
                self._divider_start_x = event.pos[0]
                self._divider_start_panel_w = self._panel_width
                return

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._dragging_divider:
                self._dragging_divider = False
                self._rebuild_panel()
                return

        elif event.type == pygame.MOUSEMOTION:
            if self._dragging_divider:
                dx = event.pos[0] - self._divider_start_x
                nw = max(_PANEL_MIN_W, min(sw - 200, self._divider_start_panel_w + dx))
                self._panel_width = nw
                if self._scroll_view:
                    self._scroll_view.width = nw
                if self._main_tab_bar:
                    self._main_tab_bar.width = nw
                return

        if self._ui:
            self._ui.handle_event(event)

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        if self._ui:
            self._ui.update(dt)

        # Cursor
        mx = pygame.mouse.get_pos()[0]
        if self._dragging_divider or abs(mx - self._panel_width) <= _DIVIDER_HIT_W // 2:
            pygame.mouse.set_cursor(
                getattr(pygame, "SYSTEM_CURSOR_SIZEWE", pygame.SYSTEM_CURSOR_ARROW)
            )
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if not self._camera:
            return

        keys = pygame.key.get_pressed()

        # Zoom
        if keys[pygame.K_e]:
            self._camera.zoom *= ZOOM_SPEED ** dt
        elif keys[pygame.K_q]:
            self._camera.zoom /= ZOOM_SPEED ** dt

        zoom = self._camera.zoom
        world_w = self._map_w * TILE_SIZE
        world_h = self._map_h * TILE_SIZE
        vp_w = self._camera.width / zoom
        vp_h = self._camera.height / zoom
        self._camera.set_bounds(
            min_x=0, max_x=max(0.0, world_w - vp_w),
            min_y=0, max_y=max(0.0, world_h - vp_h),
        )

        speed = CAMERA_SPEED / zoom
        dx = dy = 0.0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx -= speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += speed * dt
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy -= speed * dt
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy += speed * dt
        if dx or dy:
            self._camera.move(dx, dy)

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((18, 18, 28))
        sw, sh = screen.get_size()

        # Tilemap viewer (right of panel)
        if self._tilemap and self._camera and self._tileset:
            clip = pygame.Rect(self._panel_width, 0, sw - self._panel_width, sh)
            old_clip = screen.get_clip()
            screen.set_clip(clip)
            sub = screen.subsurface(clip)
            self._tilemap.draw(sub, self._camera, self._tileset)
            screen.set_clip(old_clip)
            self._draw_hud(screen)
        else:
            # Placeholder when nothing is generated
            if sw > self._panel_width + 40:
                font = pygame.font.Font(None, 22)
                txt = font.render(
                    "Previsualiza un noise o genera una matriz →",
                    True, (70, 70, 95),
                )
                screen.blit(txt, (self._panel_width + 20, sh // 2 - 10))

        # UI panel (on top)
        if self._ui:
            self._ui.draw(screen)

        # Divider
        div_color = (145, 145, 195) if self._dragging_divider else (65, 65, 88)
        pygame.draw.rect(
            screen, div_color,
            pygame.Rect(self._panel_width - _DIVIDER_W // 2, 0, _DIVIDER_W, sh),
        )

    def _draw_hud(self, screen: pygame.Surface) -> None:
        font = pygame.font.Font(None, 18)
        cam = self._camera
        info = (
            f"{self._viewer_label}  |  "
            f"Map {self._map_h}×{self._map_w}  "
            f"Cam ({int(cam.x)},{int(cam.y)})  "
            f"Zoom {cam.zoom:.2f}×"
        )
        surf = font.render(info, True, (195, 195, 195))
        screen.blit(surf, (self._panel_width + 8, 6))

        hint = "WASD/Flechas: mover | Q/E: zoom | ESC: salir"
        h_surf = font.render(hint, True, (110, 110, 130))
        screen.blit(h_surf, (self._panel_width + 8, screen.get_height() - 20))

    # ── Panel rebuild (after divider drag) ───────────────────────────────────

    def _rebuild_panel(self) -> None:
        # Invalidate cached tab vboxes (width changed)
        self._tab_vboxes = [None, None, None]
        self._noise_sub_bar = None
        self._noise_inner_scroll = None
        screen = pygame.display.get_surface()
        sw, sh = screen.get_size()
        self._ui.clear()
        self._build_ui(sw, sh)


# ── Utility ───────────────────────────────────────────────────────────────────

def _pascal_to_snake(name: str) -> str:
    """Convert 'PascalCase' → 'snake_case'."""
    import re
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
