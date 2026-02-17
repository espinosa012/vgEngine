"""
ScrollView container for scrollable content.
"""

from typing import Optional, Tuple

import pygame

from .container import Container
from ..widget import Widget


class ScrollView(Container):
    """
    A scrollable container widget.

    Allows content larger than the visible area to be scrolled.

    Features:
    - Vertical and horizontal scrolling
    - Mouse wheel support
    - Optional scrollbars
    - Clipping of content to visible area

    Example:
        scroll = ScrollView(
            x=10, y=10,
            width=200, height=300,
            content_height=600,
            show_scrollbar=True
        )
        for i in range(20):
            scroll.add_child(Label(y=i*30, text=f"Item {i+1}"))
    """

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 200,
        height: int = 200,
        content_width: int = 0,  # 0 = same as viewport width
        content_height: int = 0,  # 0 = auto-calculate from children
        scroll_x: float = 0,
        scroll_y: float = 0,
        scroll_speed: int = 20,
        show_scrollbar: bool = True,
        scrollbar_width: int = 10,
        bg_color: Optional[Tuple[int, int, int, int]] = None,
        scrollbar_color: Optional[Tuple[int, int, int]] = None,
        scrollbar_track_color: Optional[Tuple[int, int, int]] = None,
        border_radius: int = 0,
        border_width: int = 0,
        border_color: Optional[Tuple[int, int, int]] = None,
        padding: int = 0,
        parent: Optional[Widget] = None,
    ):
        """
        Initialize a ScrollView.

        Args:
            x: X position.
            y: Y position.
            width: Viewport width.
            height: Viewport height.
            content_width: Total content width (0 = viewport width).
            content_height: Total content height (0 = auto from children).
            scroll_x: Initial horizontal scroll offset.
            scroll_y: Initial vertical scroll offset.
            scroll_speed: Pixels to scroll per mouse wheel tick.
            show_scrollbar: Whether to show scrollbar.
            scrollbar_width: Width of scrollbar.
            bg_color: Background color.
            scrollbar_color: Scrollbar thumb color.
            scrollbar_track_color: Scrollbar track color.
            border_radius: Corner radius.
            border_width: Border width.
            border_color: Border color.
            padding: Internal padding.
            parent: Parent widget.
            
        """
        super().__init__(
            x, y, width, height,
            bg_color, border_radius, border_width, border_color,
            padding, False, parent
        )

        self._content_width = content_width
        self._content_height = content_height
        self._scroll_x = scroll_x
        self._scroll_y = scroll_y
        self._scroll_speed = scroll_speed
        self._show_scrollbar = show_scrollbar
        self._scrollbar_width = scrollbar_width
        self._scrollbar_color = scrollbar_color
        self._scrollbar_track_color = scrollbar_track_color

        # Scrollbar dragging state
        self._dragging_scrollbar = False
        self._drag_start_y = 0
        self._scroll_start_y = 0

    @property
    def scroll_x(self) -> float:
        """Get horizontal scroll offset."""
        return self._scroll_x

    @scroll_x.setter
    def scroll_x(self, value: float) -> None:
        """Set horizontal scroll offset."""
        max_scroll = max(0, self.actual_content_width - self.viewport_width)
        self._scroll_x = max(0, min(value, max_scroll))

    @property
    def scroll_y(self) -> float:
        """Get vertical scroll offset."""
        return self._scroll_y

    @scroll_y.setter
    def scroll_y(self, value: float) -> None:
        """Set vertical scroll offset."""
        max_scroll = max(0, self.actual_content_height - self.viewport_height)
        self._scroll_y = max(0, min(value, max_scroll))

    @property
    def viewport_width(self) -> int:
        """Get visible area width."""
        w = self.content_width
        if self._show_scrollbar and self._needs_vertical_scroll():
            w -= self._scrollbar_width
        return max(0, w)

    @property
    def viewport_height(self) -> int:
        """Get visible area height."""
        h = self.content_height
        if self._show_scrollbar and self._needs_horizontal_scroll():
            h -= self._scrollbar_width
        return max(0, h)

    @property
    def actual_content_width(self) -> int:
        """Get actual content width."""
        if self._content_width > 0:
            return self._content_width

        # Calculate from children
        max_x = 0
        for child in self._children:
            max_x = max(max_x, child.x + child.width)
        return max(self.viewport_width, max_x)

    @property
    def actual_content_height(self) -> int:
        """Get actual content height."""
        if self._content_height > 0:
            return self._content_height

        # Calculate from children
        max_y = 0
        for child in self._children:
            max_y = max(max_y, child.y + child.height)
        return max(self.viewport_height, max_y)

    def _needs_horizontal_scroll(self) -> bool:
        """Check if horizontal scroll is needed."""
        return self.actual_content_width > self.content_width

    def _needs_vertical_scroll(self) -> bool:
        """Check if vertical scroll is needed."""
        return self.actual_content_height > self.content_height

    def scroll_to(self, x: float = None, y: float = None) -> None:
        """
        Scroll to a specific position.

        Args:
            x: Target horizontal scroll (None = don't change).
            y: Target vertical scroll (None = don't change).
        """
        if x is not None:
            self.scroll_x = x
        if y is not None:
            self.scroll_y = y

    def scroll_to_top(self) -> None:
        """Scroll to top."""
        self.scroll_y = 0

    def scroll_to_bottom(self) -> None:
        """Scroll to bottom."""
        self.scroll_y = self.actual_content_height

    def scroll_to_widget(self, widget: Widget) -> None:
        """
        Scroll to make a widget visible.

        Args:
            widget: Widget to scroll to.
        """
        if widget not in self._children:
            return

        # Check if widget is above viewport
        if widget.y < self._scroll_y:
            self.scroll_y = widget.y
        # Check if widget is below viewport
        elif widget.y + widget.height > self._scroll_y + self.viewport_height:
            self.scroll_y = widget.y + widget.height - self.viewport_height

    def get_absolute_position(self) -> Tuple[int, int]:
        """Get absolute position, accounting for parent scroll."""
        if self._parent:
            parent_x, parent_y = self._parent.get_absolute_position()
            return self._rect.x + parent_x, self._rect.y + parent_y
        return self._rect.x, self._rect.y

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events including scroll."""
        if not self._state.visible or not self._state.enabled:
            return False

        # Handle scrollbar drag
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._show_scrollbar and self._needs_vertical_scroll():
                scrollbar_rect = self._get_scrollbar_rect()
                if scrollbar_rect and scrollbar_rect.collidepoint(event.pos):
                    self._dragging_scrollbar = True
                    self._drag_start_y = event.pos[1]
                    self._scroll_start_y = self._scroll_y
                    return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._dragging_scrollbar:
                self._dragging_scrollbar = False
                return True

        elif event.type == pygame.MOUSEMOTION:
            if self._dragging_scrollbar:
                # Calculate new scroll position
                delta_y = event.pos[1] - self._drag_start_y

                # Scale delta by content/viewport ratio
                track_height = self.content_height - (self._scrollbar_width * 2)
                content_height = self.actual_content_height
                viewport_height = self.viewport_height

                if track_height > 0:
                    scroll_ratio = content_height / track_height
                    self.scroll_y = self._scroll_start_y + delta_y * scroll_ratio
                return True

        # Handle mouse wheel
        if event.type == pygame.MOUSEWHEEL:
            if self.contains_point(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
                self.scroll_y = self._scroll_y - event.y * self._scroll_speed
                return True

        # Transform child events by scroll offset
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            # Check if inside viewport
            abs_rect = self.absolute_rect
            viewport_rect = pygame.Rect(
                abs_rect.x + self._padding,
                abs_rect.y + self._padding,
                self.viewport_width,
                self.viewport_height
            )

            if viewport_rect.collidepoint(event.pos):
                # Create modified event with offset position
                # This is a simplified approach - children check their absolute position
                pass

        # Let children handle events
        for child in reversed(self._children):
            if child.handle_event(event):
                return True

        return super().handle_event(event)

    def _get_scrollbar_rect(self) -> Optional[pygame.Rect]:
        """Get the scrollbar thumb rectangle."""
        if not self._needs_vertical_scroll():
            return None

        abs_rect = self.absolute_rect

        content_height = self.actual_content_height
        viewport_height = self.viewport_height
        track_height = self.content_height

        # Calculate thumb size (proportional to viewport/content ratio)
        thumb_height = max(30, int(track_height * (viewport_height / content_height)))

        # Calculate thumb position
        scroll_ratio = self._scroll_y / (content_height - viewport_height) if content_height > viewport_height else 0
        thumb_y = int(scroll_ratio * (track_height - thumb_height))

        return pygame.Rect(
            abs_rect.x + abs_rect.width - self._padding - self._scrollbar_width,
            abs_rect.y + self._padding + thumb_y,
            self._scrollbar_width,
            thumb_height
        )

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the scroll view."""
        if not self.visible:
            return

        abs_rect = self.absolute_rect

        # Draw background
        if self._bg_color:
            if self._border_radius > 0:
                pygame.draw.rect(
                    surface,
                    self._bg_color[:3],
                    abs_rect,
                    border_radius=self._border_radius
                )
            else:
                pygame.draw.rect(surface, self._bg_color[:3], abs_rect)

        # Create viewport clip rect
        viewport_rect = pygame.Rect(
            abs_rect.x + self._padding,
            abs_rect.y + self._padding,
            self.viewport_width,
            self.viewport_height
        )

        # Save current clip
        old_clip = surface.get_clip()
        surface.set_clip(viewport_rect)

        # Draw children with scroll offset
        for child in self._children:
            if child.visible:
                # Temporarily offset child position
                original_x, original_y = child.x, child.y
                child._rect.x = original_x - int(self._scroll_x) + self._padding
                child._rect.y = original_y - int(self._scroll_y) + self._padding

                # Check if child is visible in viewport
                child_abs_rect = child.absolute_rect
                if viewport_rect.colliderect(child_abs_rect):
                    child.draw(surface)

                # Restore position
                child._rect.x = original_x
                child._rect.y = original_y

        # Restore clip
        surface.set_clip(old_clip)

        # Draw scrollbar
        if self._show_scrollbar and self._needs_vertical_scroll():
            # Track
            track_rect = pygame.Rect(
                abs_rect.x + abs_rect.width - self._padding - self._scrollbar_width,
                abs_rect.y + self._padding,
                self._scrollbar_width,
                self.content_height
            )

            track_color = self._scrollbar_track_color or (40, 40, 40)

            pygame.draw.rect(surface, track_color, track_rect, border_radius=self._scrollbar_width // 2)

            # Thumb
            thumb_rect = self._get_scrollbar_rect()
            if thumb_rect:
                thumb_color = self._scrollbar_color or (100, 100, 100)

                pygame.draw.rect(surface, thumb_color, thumb_rect, border_radius=self._scrollbar_width // 2)

        # Draw border
        if self._border_width > 0:
            border_color = self._border_color or (80, 80, 80)

            pygame.draw.rect(
                surface,
                border_color,
                abs_rect,
                width=self._border_width,
                border_radius=self._border_radius
            )

