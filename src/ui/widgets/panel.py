"""
Panel widget for grouping and decorating other widgets.
"""

from typing import Optional, Tuple, Union

import pygame

from ..widget import Widget


class Panel(Widget):
    """
    A container panel widget with optional background and border.

    Panels can be used to:
    - Group related widgets visually
    - Create cards or sections
    - Add decorative backgrounds

    Example:
        panel = Panel(
            x=10, y=10,
            width=200, height=150,
            bg_color=(50, 50, 50),
            border_radius=8
        )
        panel.add_child(label)
        panel.add_child(button)
    """

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 200,
        height: int = 100,
        bg_color: Optional[Union[Tuple[int, int, int], Tuple[int, int, int, int]]] = None,
        border_radius: int = 0,
        border_width: int = 0,
        border_color: Optional[Tuple[int, int, int]] = None,
        padding: int = 0,
        parent: Optional[Widget] = None
    ):
        """
        Initialize a Panel.

        Args:
            x: X position.
            y: Y position.
            width: Panel width.
            height: Panel height.
            bg_color: Background color as RGB or RGBA tuple.
            border_radius: Corner radius in pixels.
            border_width: Border width in pixels (0 = no border).
            border_color: Border color (default gray if None).
            padding: Internal padding for child positioning.
            parent: Parent widget.
        """
        super().__init__(x, y, width, height, parent)

        self._bg_color = bg_color
        self._border_radius = border_radius
        self._border_width = border_width
        self._border_color = border_color
        self._padding = padding

    @property
    def bg_color(self) -> Optional[Tuple]:
        """Get the background color."""
        return self._bg_color

    @bg_color.setter
    def bg_color(self, value: Optional[Tuple]) -> None:
        """Set the background color."""
        self._bg_color = value

    @property
    def padding(self) -> int:
        """Get the padding."""
        return self._padding

    @padding.setter
    def padding(self, value: int) -> None:
        """Set the padding."""
        self._padding = max(0, value)

    @property
    def content_width(self) -> int:
        """Get the content area width (excluding padding)."""
        return self.width - (self._padding * 2)

    @property
    def content_height(self) -> int:
        """Get the content area height (excluding padding)."""
        return self.height - (self._padding * 2)

    @property
    def inner_rect(self) -> pygame.Rect:
        """
        Get the inner rect (excluding padding).

        Returns:
            Rect representing the content area inside padding.
        """
        return pygame.Rect(
            self._rect.x + self._padding,
            self._rect.y + self._padding,
            self._rect.width - (self._padding * 2),
            self._rect.height - (self._padding * 2)
        )

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the panel."""
        if not self.visible:
            return

        abs_rect = self.absolute_rect

        # Draw background
        bg = self.bg_color
        if bg:
            # Check if we need alpha blending
            if len(bg) == 4 and bg[3] < 255:
                # Create a temporary surface with per-pixel alpha
                temp_surface = pygame.Surface(
                    (abs_rect.width, abs_rect.height),
                    pygame.SRCALPHA
                )
                if self._border_radius > 0:
                    pygame.draw.rect(
                        temp_surface,
                        bg,
                        pygame.Rect(0, 0, abs_rect.width, abs_rect.height),
                        border_radius=self._border_radius
                    )
                else:
                    temp_surface.fill(bg)
                surface.blit(temp_surface, (abs_rect.x, abs_rect.y))
            else:
                # Solid color
                if self._border_radius > 0:
                    pygame.draw.rect(
                        surface,
                        bg[:3],  # RGB only
                        abs_rect,
                        border_radius=self._border_radius
                    )
                else:
                    pygame.draw.rect(surface, bg[:3], abs_rect)

        # Draw border
        if self._border_width > 0:
            border_color = self._border_color or (80, 80, 80)

            if self._border_radius > 0:
                pygame.draw.rect(
                    surface,
                    border_color,
                    abs_rect,
                    width=self._border_width,
                    border_radius=self._border_radius
                )
            else:
                pygame.draw.rect(
                    surface,
                    border_color,
                    abs_rect,
                    width=self._border_width
                )

        # Draw children
        self.draw_children(surface)

