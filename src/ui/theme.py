"""
UI Theme system for styling widgets.

Provides configurable colors, fonts, and dimensions for consistent UI appearance.
"""

from dataclasses import dataclass, field
from typing import Optional, Tuple

import pygame

# TODO: Integrar con src.core.color.Color para mayor flexibilidad (soporte RGBA, HSL, etc.)
# Por ahora usamos tuplas RGB/RGBA directamente con Pygame

@dataclass
class UIColors:
    """
    Color scheme for UI widgets.

    All colors are stored as RGB or RGBA tuples for direct use with Pygame.
    """
    # Primary colors
    primary: Tuple[int, int, int] = (66, 135, 245)       # Blue
    primary_hover: Tuple[int, int, int] = (100, 160, 255)
    primary_pressed: Tuple[int, int, int] = (40, 100, 200)
    primary_disabled: Tuple[int, int, int] = (120, 140, 160)

    # Secondary colors
    secondary: Tuple[int, int, int] = (100, 100, 100)
    secondary_hover: Tuple[int, int, int] = (130, 130, 130)
    secondary_pressed: Tuple[int, int, int] = (70, 70, 70)

    # Background colors
    background: Tuple[int, int, int] = (30, 30, 30)
    background_light: Tuple[int, int, int] = (45, 45, 45)
    background_dark: Tuple[int, int, int] = (20, 20, 20)

    # Surface colors (for panels, cards, etc.)
    surface: Tuple[int, int, int] = (50, 50, 50)
    surface_hover: Tuple[int, int, int] = (60, 60, 60)
    surface_selected: Tuple[int, int, int] = (70, 80, 90)

    # Text colors
    text: Tuple[int, int, int] = (255, 255, 255)
    text_secondary: Tuple[int, int, int] = (180, 180, 180)
    text_disabled: Tuple[int, int, int] = (100, 100, 100)
    text_on_primary: Tuple[int, int, int] = (255, 255, 255)

    # Border colors
    border: Tuple[int, int, int] = (80, 80, 80)
    border_focused: Tuple[int, int, int] = (66, 135, 245)
    border_error: Tuple[int, int, int] = (220, 60, 60)

    # State colors
    success: Tuple[int, int, int] = (76, 175, 80)
    warning: Tuple[int, int, int] = (255, 193, 7)
    error: Tuple[int, int, int] = (244, 67, 54)
    info: Tuple[int, int, int] = (33, 150, 243)

    # Transparent
    transparent: Tuple[int, int, int, int] = (0, 0, 0, 0)


@dataclass
class UIFonts:
    """
    Font configuration for UI widgets.

    Attributes:
        family: Font family name (None uses Pygame default).
        size_small: Small text size.
        size_normal: Normal text size.
        size_large: Large text size.
        size_title: Title text size.
    """
    family: Optional[str] = None
    size_small: int = 12
    size_normal: int = 16
    size_large: int = 20
    size_title: int = 24

    # Cached font objects
    _fonts: dict = field(default_factory=dict, repr=False)

    def get_font(self, size: int, bold: bool = False, italic: bool = False) -> pygame.font.Font:
        """
        Get a pygame Font object with the specified parameters.

        Args:
            size: Font size in points.
            bold: Whether to use bold style.
            italic: Whether to use italic style.

        Returns:
            Pygame Font object.
        """
        key = (self.family, size, bold, italic)

        if key not in self._fonts:
            try:
                font = pygame.font.SysFont(self.family, size, bold=bold, italic=italic)
            except:
                font = pygame.font.Font(None, size)
            self._fonts[key] = font

        return self._fonts[key]

    @property
    def small(self) -> pygame.font.Font:
        """Get small font."""
        return self.get_font(self.size_small)

    @property
    def normal(self) -> pygame.font.Font:
        """Get normal font."""
        return self.get_font(self.size_normal)

    @property
    def large(self) -> pygame.font.Font:
        """Get large font."""
        return self.get_font(self.size_large)

    @property
    def title(self) -> pygame.font.Font:
        """Get title font."""
        return self.get_font(self.size_title, bold=True)


@dataclass
class UIDimensions:
    """
    Standard dimensions for UI elements.
    """
    # Padding
    padding_small: int = 4
    padding_normal: int = 8
    padding_large: int = 16

    # Margins
    margin_small: int = 4
    margin_normal: int = 8
    margin_large: int = 16

    # Border
    border_width: int = 1
    border_radius: int = 4

    # Widget sizes
    button_height: int = 32
    input_height: int = 32
    label_height: int = 24

    # Spacing for layouts
    spacing_small: int = 4
    spacing_normal: int = 8
    spacing_large: int = 16


@dataclass
class UITheme:
    """
    Complete UI theme containing colors, fonts, and dimensions.

    Themes can be easily customized and switched at runtime.
    """
    name: str = "default"
    colors: UIColors = field(default_factory=UIColors)
    fonts: UIFonts = field(default_factory=UIFonts)
    dimensions: UIDimensions = field(default_factory=UIDimensions)

    @classmethod
    def dark(cls) -> 'UITheme':
        """Create a dark theme (default)."""
        return cls(
            name="dark",
            colors=UIColors()
        )

    @classmethod
    def light(cls) -> 'UITheme':
        """Create a light theme."""
        return cls(
            name="light",
            colors=UIColors(
                primary=(25, 118, 210),
                primary_hover=(66, 165, 245),
                primary_pressed=(21, 101, 192),

                background=(245, 245, 245),
                background_light=(255, 255, 255),
                background_dark=(224, 224, 224),

                surface=(255, 255, 255),
                surface_hover=(245, 245, 245),
                surface_selected=(232, 240, 254),

                text=(33, 33, 33),
                text_secondary=(97, 97, 97),
                text_disabled=(158, 158, 158),
                text_on_primary=(255, 255, 255),

                border=(189, 189, 189),
                border_focused=(25, 118, 210),
            )
        )

    @classmethod
    def high_contrast(cls) -> 'UITheme':
        """Create a high contrast theme for accessibility."""
        return cls(
            name="high_contrast",
            colors=UIColors(
                primary=(0, 255, 255),
                primary_hover=(100, 255, 255),
                primary_pressed=(0, 200, 200),

                background=(0, 0, 0),
                background_light=(20, 20, 20),
                background_dark=(0, 0, 0),

                surface=(0, 0, 0),
                surface_hover=(30, 30, 30),
                surface_selected=(0, 50, 50),

                text=(255, 255, 255),
                text_secondary=(255, 255, 0),
                text_disabled=(128, 128, 128),
                text_on_primary=(0, 0, 0),

                border=(255, 255, 255),
                border_focused=(0, 255, 255),
            ),
            fonts=UIFonts(size_normal=18, size_large=22, size_title=28)
        )


# Default theme instance
DEFAULT_THEME = UITheme.dark()


def get_default_theme() -> UITheme:
    """Get the default theme."""
    return DEFAULT_THEME


def set_default_theme(theme: UITheme) -> None:
    """Set the default theme globally."""
    global DEFAULT_THEME
    DEFAULT_THEME = theme

