"""
Configuration for the Tilemap Editor.
"""
from dataclasses import dataclass
@dataclass(frozen=True)
class TilemapThemeColors:
    """Color scheme for the tilemap editor."""
    background: str = "#1e1e1e"
    foreground: str = "#ffffff"
    card: str = "#2d2d2d"
    accent: str = "#4a9eff"
    accent_hover: str = "#5aafff"
    muted: str = "#888888"
    grid_color: str = "#444444"
    selection: str = "#ffaa00"
@dataclass(frozen=True)
class TilemapWindowConfig:
    """Window configuration for tilemap editor."""
    title: str = "Tilemap Editor"
    width: int = 1000
    height: int = 700
    min_width: int = 900
    min_height: int = 600
# Default tilemap settings
DEFAULT_MAP_WIDTH = 20
DEFAULT_MAP_HEIGHT = 15
DEFAULT_TILE_SIZE = 32
# Tileset panel
TILESET_PANEL_WIDTH = 250
TILE_PREVIEW_SIZE = 48
