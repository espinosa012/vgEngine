"""
Slider widget for numeric value input.
"""

from typing import Optional, Tuple, Callable

import pygame

from ..widget import Widget


class Slider(Widget):
    """
    A slider widget for selecting numeric values within a range.

    Features:
    - Horizontal or vertical orientation
    - Configurable min/max/step values
    - Visual feedback for hover and drag states
    - Optional value display
    - Change callback

    Example:
        slider = Slider(
            x=10, y=10,
            width=200,
            min_value=0,
            max_value=100,
            value=50,
            on_change=lambda s: print(f"Value: {s.value}")
        )
    """

    # Orientation constants
    HORIZONTAL = 'horizontal'
    VERTICAL = 'vertical'

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 200,
        height: int = 24,
        min_value: float = 0.0,
        max_value: float = 100.0,
        value: float = 50.0,
        step: float = 1.0,
        orientation: str = HORIZONTAL,
        track_color: Optional[Tuple[int, int, int]] = None,
        fill_color: Optional[Tuple[int, int, int]] = None,
        handle_color: Optional[Tuple[int, int, int]] = None,
        handle_size: int = 16,
        track_height: int = 6,
        show_value: bool = False,
        parent: Optional[Widget] = None,
    ):
        """
        Initialize a Slider.

        Args:
            x: X position.
            y: Y position.
            width: Slider width (length for horizontal).
            height: Slider height (length for vertical).
            min_value: Minimum value.
            max_value: Maximum value.
            value: Initial value.
            step: Value step increment.
            orientation: 'horizontal' or 'vertical'.
            track_color: Color of the track background.
            fill_color: Color of the filled portion.
            handle_color: Color of the handle.
            handle_size: Size of the handle in pixels.
            track_height: Thickness of the track.
            show_value: Whether to show the current value.
            parent: Parent widget.
        """
        super().__init__(x, y, width, height, parent)

        self._min_value = min_value
        self._max_value = max_value
        self._value = max(min_value, min(max_value, value))
        self._step = step
        self._orientation = orientation
        self._track_color = track_color
        self._fill_color = fill_color
        self._handle_color = handle_color
        self._handle_size = handle_size
        self._track_height = track_height
        self._show_value = show_value

        # Dragging state
        self._dragging = False

        # Change callback
        self._on_change: Optional[Callable[[Slider], None]] = None

    @property
    def value(self) -> float:
        """Get the current value."""
        return self._value

    @value.setter
    def value(self, val: float) -> None:
        """Set the current value."""
        # Clamp to range
        val = max(self._min_value, min(self._max_value, val))

        # Apply step
        if self._step > 0:
            val = round((val - self._min_value) / self._step) * self._step + self._min_value

        if self._value != val:
            self._value = val
            if self._on_change:
                self._on_change(self)

    @property
    def min_value(self) -> float:
        """Get the minimum value."""
        return self._min_value

    @min_value.setter
    def min_value(self, val: float) -> None:
        """Set the minimum value."""
        self._min_value = val
        self.value = self._value  # Re-clamp

    @property
    def max_value(self) -> float:
        """Get the maximum value."""
        return self._max_value

    @max_value.setter
    def max_value(self, val: float) -> None:
        """Set the maximum value."""
        self._max_value = val
        self.value = self._value  # Re-clamp

    @property
    def normalized_value(self) -> float:
        """Get the value normalized to 0.0-1.0 range."""
        range_val = self._max_value - self._min_value
        if range_val == 0:
            return 0.0
        return (self._value - self._min_value) / range_val

    def on_change(self, callback: Callable[['Slider'], None]) -> 'Slider':
        """
        Set the change callback.

        Args:
            callback: Function to call when value changes.

        Returns:
            Self for method chaining.
        """
        self._on_change = callback
        return self

    def _get_handle_rect(self) -> pygame.Rect:
        """Get the handle rectangle in local coordinates."""
        abs_x, abs_y = self.get_absolute_position()

        if self._orientation == self.HORIZONTAL:
            # Track area (excluding handle radius at ends)
            track_start = self._handle_size // 2
            track_length = self.width - self._handle_size

            handle_x = abs_x + track_start + int(self.normalized_value * track_length) - self._handle_size // 2
            handle_y = abs_y + (self.height - self._handle_size) // 2
        else:
            track_start = self._handle_size // 2
            track_length = self.height - self._handle_size

            # Invert for vertical (0 at bottom)
            handle_x = abs_x + (self.width - self._handle_size) // 2
            handle_y = abs_y + track_start + int((1 - self.normalized_value) * track_length) - self._handle_size // 2

        return pygame.Rect(handle_x, handle_y, self._handle_size, self._handle_size)

    def _position_to_value(self, x: int, y: int) -> float:
        """Convert a screen position to a value."""
        abs_x, abs_y = self.get_absolute_position()

        if self._orientation == self.HORIZONTAL:
            track_start = self._handle_size // 2
            track_length = self.width - self._handle_size

            local_x = x - abs_x - track_start
            normalized = max(0, min(1, local_x / track_length if track_length > 0 else 0))
        else:
            track_start = self._handle_size // 2
            track_length = self.height - self._handle_size

            local_y = y - abs_y - track_start
            normalized = max(0, min(1, 1 - (local_y / track_length if track_length > 0 else 0)))

        return self._min_value + normalized * (self._max_value - self._min_value)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events including drag."""
        if not self._state.visible or not self._state.enabled:
            return False

        # Let parent handle children first
        for child in reversed(self._children):
            if child.handle_event(event):
                return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.contains_point(event.pos[0], event.pos[1]):
                self._dragging = True
                self._state.pressed = True
                self.value = self._position_to_value(event.pos[0], event.pos[1])
                self.focus()
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._dragging:
                self._dragging = False
                self._state.pressed = False
                return True

        elif event.type == pygame.MOUSEMOTION:
            # Handle hover
            was_hovered = self._state.hovered
            is_hovered = self.contains_point(event.pos[0], event.pos[1])

            if is_hovered and not was_hovered:
                self._state.hovered = True
                if self._on_hover_enter:
                    self._on_hover_enter(self)
            elif not is_hovered and was_hovered and not self._dragging:
                self._state.hovered = False
                if self._on_hover_exit:
                    self._on_hover_exit(self)

            # Handle dragging
            if self._dragging:
                self.value = self._position_to_value(event.pos[0], event.pos[1])
                return True

        return False

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the slider."""
        if not self.visible:
            return

        abs_x, abs_y = self.get_absolute_position()

        # Get colors
        track_color = self._track_color or (60, 60, 60)
        fill_color = self._fill_color or (66, 135, 245)

        handle_color = self._handle_color
        if not handle_color:
            if self._dragging or self.hovered:
                handle_color = (100, 160, 255)
            else:
                handle_color = (66, 135, 245)

        if self._orientation == self.HORIZONTAL:
            # Draw track
            track_y = abs_y + (self.height - self._track_height) // 2
            track_rect = pygame.Rect(
                abs_x + self._handle_size // 2,
                track_y,
                self.width - self._handle_size,
                self._track_height
            )
            pygame.draw.rect(surface, track_color, track_rect, border_radius=self._track_height // 2)

            # Draw fill
            fill_width = int(self.normalized_value * (self.width - self._handle_size))
            if fill_width > 0:
                fill_rect = pygame.Rect(
                    abs_x + self._handle_size // 2,
                    track_y,
                    fill_width,
                    self._track_height
                )
                pygame.draw.rect(surface, fill_color, fill_rect, border_radius=self._track_height // 2)
        else:
            # Draw track (vertical)
            track_x = abs_x + (self.width - self._track_height) // 2
            track_rect = pygame.Rect(
                track_x,
                abs_y + self._handle_size // 2,
                self._track_height,
                self.height - self._handle_size
            )
            pygame.draw.rect(surface, track_color, track_rect, border_radius=self._track_height // 2)

            # Draw fill (from bottom)
            fill_height = int(self.normalized_value * (self.height - self._handle_size))
            if fill_height > 0:
                fill_rect = pygame.Rect(
                    track_x,
                    abs_y + self.height - self._handle_size // 2 - fill_height,
                    self._track_height,
                    fill_height
                )
                pygame.draw.rect(surface, fill_color, fill_rect, border_radius=self._track_height // 2)

        # Draw handle
        handle_rect = self._get_handle_rect()
        pygame.draw.circle(
            surface,
            handle_color,
            handle_rect.center,
            self._handle_size // 2
        )

        # Draw value text if enabled
        if self._show_value:
            font = pygame.font.Font(None, 14)
            text_color = (255, 255, 255)

            # Format value
            if self._step >= 1:
                text = str(int(self._value))
            else:
                decimals = len(str(self._step).split('.')[-1])
                text = f"{self._value:.{decimals}f}"

            text_surface = font.render(text, True, text_color)
            text_rect = text_surface.get_rect()

            # Position above/beside handle
            if self._orientation == self.HORIZONTAL:
                text_rect.centerx = handle_rect.centerx
                text_rect.bottom = handle_rect.top - 4
            else:
                text_rect.left = handle_rect.right + 4
                text_rect.centery = handle_rect.centery

            surface.blit(text_surface, text_rect)

        # Draw children
        self.draw_children(surface)

