"""
Label widget for displaying text.
"""

from typing import Optional, Tuple

import pygame

from ..widget import Widget


class Label(Widget):
    """
    A simple text label widget.

    Displays static or dynamic text with configurable font, color, and alignment.

    Example:
        label = Label(
            x=10, y=10,
            text="Hello, World!",
            font_size=16,
            color=(255, 255, 255)
        )
    """

    # Text alignment constants
    ALIGN_LEFT = 'left'
    ALIGN_CENTER = 'center'
    ALIGN_RIGHT = 'right'

    VALIGN_TOP = 'top'
    VALIGN_CENTER = 'center'
    VALIGN_BOTTOM = 'bottom'

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 0,
        height: int = 0,
        text: str = "",
        font_size: Optional[int] = None,
        color: Optional[Tuple[int, int, int]] = None,
        font_family: Optional[str] = None,
        bold: bool = False,
        italic: bool = False,
        align: str = ALIGN_LEFT,
        valign: str = VALIGN_TOP,
        auto_size: bool = True,
        parent: Optional[Widget] = None
    ):
        """
        Initialize a Label.

        Args:
            x: X position.
            y: Y position.
            width: Widget width (used if auto_size is False).
            height: Widget height (used if auto_size is False).
            text: Text to display.
            font_size: Font size (default 16 if None).
            color: Text color as RGB tuple (default white if None).
            font_family: Font family name (uses pygame default if None).
            bold: Whether to use bold text.
            italic: Whether to use italic text.
            align: Horizontal alignment ('left', 'center', 'right').
            valign: Vertical alignment ('top', 'center', 'bottom').
            auto_size: If True, resize to fit text.
            parent: Parent widget.
        """
        super().__init__(x, y, width, height, parent)

        self._text = text
        self._font_size = font_size
        self._color = color
        self._font_family = font_family
        self._bold = bold
        self._italic = italic
        self._align = align
        self._valign = valign
        self._auto_size = auto_size

        # Cached rendered surface
        self._rendered_text: Optional[pygame.Surface] = None
        self._needs_render = True

        # Initial render
        self._update_size()

    @property
    def text(self) -> str:
        """Get the label text."""
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        """Set the label text."""
        if self._text != value:
            self._text = value
            self._needs_render = True
            self._update_size()

    @property
    def color(self) -> Tuple[int, int, int]:
        """Get the text color."""
        if self._color:
            return self._color
        return (255, 255, 255)  # Default white

    @color.setter
    def color(self, value: Tuple[int, int, int]) -> None:
        """Set the text color."""
        self._color = value
        self._needs_render = True

    @property
    def font_size(self) -> int:
        """Get the font size."""
        if self._font_size:
            return self._font_size
        return 16  # Default font size

    @font_size.setter
    def font_size(self, value: int) -> None:
        """Set the font size."""
        self._font_size = value
        self._needs_render = True
        self._update_size()

    def _get_font(self) -> pygame.font.Font:
        """Get the pygame font object."""
        return pygame.font.Font(None, self.font_size)

    def _update_size(self) -> None:
        """Update widget size based on text if auto_size is enabled."""
        if self._auto_size and self._text:
            font = self._get_font()
            text_size = font.size(self._text)
            self._rect.width = text_size[0]
            self._rect.height = text_size[1]

    def _render_text(self) -> None:
        """Render the text to a surface."""
        if not self._text:
            self._rendered_text = None
            return

        font = self._get_font()

        # Use gray color if widget is disabled
        if not self.enabled:
            color = (100, 100, 100)
        else:
            color = self.color

        self._rendered_text = font.render(self._text, True, color)
        self._needs_render = False

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the label."""
        if not self.visible or not self._text:
            return

        # Render text if needed
        if self._needs_render:
            self._render_text()

        if not self._rendered_text:
            return

        # Calculate position
        abs_x, abs_y = self.get_absolute_position()

        # Horizontal alignment
        text_width = self._rendered_text.get_width()
        if self._align == self.ALIGN_CENTER:
            x = abs_x + (self.width - text_width) // 2
        elif self._align == self.ALIGN_RIGHT:
            x = abs_x + self.width - text_width
        else:  # LEFT
            x = abs_x

        # Vertical alignment
        text_height = self._rendered_text.get_height()
        if self._valign == self.VALIGN_CENTER:
            y = abs_y + (self.height - text_height) // 2
        elif self._valign == self.VALIGN_BOTTOM:
            y = abs_y + self.height - text_height
        else:  # TOP
            y = abs_y

        surface.blit(self._rendered_text, (x, y))

        # Draw children
        self.draw_children(surface)

