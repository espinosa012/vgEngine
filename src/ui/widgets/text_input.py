"""
TextInput widget for text entry.
"""

from typing import Optional, Tuple, Callable

import pygame

from ..widget import Widget


class TextInput(Widget):
    """
    A single-line text input widget.

    Features:
    - Text editing with cursor
    - Selection support (future)
    - Placeholder text
    - Character limit
    - Visual feedback for focus and hover states
    - Change and submit callbacks

    Example:
        text_input = TextInput(
            x=10, y=10,
            width=200,
            placeholder="Enter your name...",
            on_change=lambda ti: print(f"Text: {ti.text}"),
            on_submit=lambda ti: print(f"Submitted: {ti.text}")
        )
    """

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 200,
        height: int = 32,
        text: str = "",
        placeholder: str = "",
        max_length: int = 0,
        font_size: Optional[int] = None,
        text_color: Optional[Tuple[int, int, int]] = None,
        placeholder_color: Optional[Tuple[int, int, int]] = None,
        bg_color: Optional[Tuple[int, int, int]] = None,
        border_color: Optional[Tuple[int, int, int]] = None,
        focus_border_color: Optional[Tuple[int, int, int]] = None,
        border_width: int = 1,
        border_radius: int = 4,
        padding: int = 8,
        parent: Optional[Widget] = None,
    ):
        """
        Initialize a TextInput.

        Args:
            x: X position.
            y: Y position.
            width: Input width.
            height: Input height.
            text: Initial text.
            placeholder: Placeholder text shown when empty.
            max_length: Maximum character limit (0 = unlimited).
            font_size: Font size (uses theme default if None).
            text_color: Text color.
            placeholder_color: Placeholder text color.
            bg_color: Background color.
            border_color: Border color.
            focus_border_color: Border color when focused.
            border_width: Border width in pixels.
            border_radius: Corner radius.
            padding: Internal padding.
            parent: Parent widget.
        """
        super().__init__(x, y, width, height, parent)

        self._text = text
        self._placeholder = placeholder
        self._max_length = max_length
        self._font_size = font_size
        self._text_color = text_color
        self._placeholder_color = placeholder_color
        self._bg_color = bg_color
        self._border_color = border_color
        self._focus_border_color = focus_border_color
        self._border_width = border_width
        self._border_radius = border_radius
        self._padding = padding

        # Cursor state
        self._cursor_pos = len(text)
        self._cursor_visible = True
        self._cursor_timer = 0.0
        self._cursor_blink_rate = 0.5  # seconds

        # Scroll offset for long text
        self._scroll_offset = 0

        # Callbacks
        self._on_change: Optional[Callable[[TextInput], None]] = None
        self._on_submit: Optional[Callable[[TextInput], None]] = None

    @property
    def text(self) -> str:
        """Get the current text."""
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        """Set the text."""
        if self._max_length > 0:
            value = value[:self._max_length]

        if self._text != value:
            self._text = value
            self._cursor_pos = min(self._cursor_pos, len(value))
            self._update_scroll()
            if self._on_change:
                self._on_change(self)

    @property
    def placeholder(self) -> str:
        """Get the placeholder text."""
        return self._placeholder

    @placeholder.setter
    def placeholder(self, value: str) -> None:
        """Set the placeholder text."""
        self._placeholder = value

    def on_change(self, callback: Callable[['TextInput'], None]) -> 'TextInput':
        """
        Set the change callback.

        Args:
            callback: Function to call when text changes.

        Returns:
            Self for method chaining.
        """
        self._on_change = callback
        return self

    def on_submit(self, callback: Callable[['TextInput'], None]) -> 'TextInput':
        """
        Set the submit callback (called on Enter key).

        Args:
            callback: Function to call when Enter is pressed.

        Returns:
            Self for method chaining.
        """
        self._on_submit = callback
        return self

    def _get_font(self) -> pygame.font.Font:
        """Get the pygame font object."""
        size = self._font_size or 16
        return pygame.font.Font(None, size)

    def _update_scroll(self) -> None:
        """Update scroll offset to keep cursor visible."""
        font = self._get_font()
        content_width = self.width - (self._padding * 2)

        # Get text width up to cursor
        text_to_cursor = self._text[:self._cursor_pos]
        cursor_x = font.size(text_to_cursor)[0]

        # Adjust scroll to keep cursor visible
        if cursor_x - self._scroll_offset > content_width:
            self._scroll_offset = cursor_x - content_width + 10
        elif cursor_x - self._scroll_offset < 0:
            self._scroll_offset = max(0, cursor_x - 10)

    def _insert_text(self, text: str) -> None:
        """Insert text at cursor position."""
        new_text = self._text[:self._cursor_pos] + text + self._text[self._cursor_pos:]

        if self._max_length > 0:
            new_text = new_text[:self._max_length]

        self._text = new_text
        self._cursor_pos = min(self._cursor_pos + len(text), len(self._text))
        self._update_scroll()

        if self._on_change:
            self._on_change(self)

    def _delete_char(self, forward: bool = False) -> None:
        """Delete a character at cursor position."""
        if forward:
            if self._cursor_pos < len(self._text):
                self._text = self._text[:self._cursor_pos] + self._text[self._cursor_pos + 1:]
                if self._on_change:
                    self._on_change(self)
        else:
            if self._cursor_pos > 0:
                self._text = self._text[:self._cursor_pos - 1] + self._text[self._cursor_pos:]
                self._cursor_pos -= 1
                self._update_scroll()
                if self._on_change:
                    self._on_change(self)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events including keyboard input."""
        if not self._state.visible or not self._state.enabled:
            return False

        # Let parent handle children first
        for child in reversed(self._children):
            if child.handle_event(event):
                return True

        # Handle mouse events for focus
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.contains_point(event.pos[0], event.pos[1]):
                self._state.pressed = True
                self.focus()

                # Set cursor position based on click
                self._set_cursor_from_mouse(event.pos[0])
                return True
            else:
                if self.focused:
                    self.blur()

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._state.pressed = False

        elif event.type == pygame.MOUSEMOTION:
            was_hovered = self._state.hovered
            is_hovered = self.contains_point(event.pos[0], event.pos[1])

            if is_hovered != was_hovered:
                self._state.hovered = is_hovered

        # Handle keyboard input when focused
        if self.focused and event.type == pygame.KEYDOWN:
            return self._handle_key(event)

        return False

    def _set_cursor_from_mouse(self, mouse_x: int) -> None:
        """Set cursor position based on mouse x coordinate."""
        abs_x, _ = self.get_absolute_position()
        local_x = mouse_x - abs_x - self._padding + self._scroll_offset

        font = self._get_font()

        # Find closest character position
        best_pos = 0
        best_dist = abs(local_x)

        for i in range(1, len(self._text) + 1):
            char_x = font.size(self._text[:i])[0]
            dist = abs(local_x - char_x)
            if dist < best_dist:
                best_dist = dist
                best_pos = i

        self._cursor_pos = best_pos

    def _handle_key(self, event: pygame.event.Event) -> bool:
        """Handle keyboard input."""
        if event.key == pygame.K_BACKSPACE:
            self._delete_char(forward=False)
            return True

        elif event.key == pygame.K_DELETE:
            self._delete_char(forward=True)
            return True

        elif event.key == pygame.K_LEFT:
            if self._cursor_pos > 0:
                self._cursor_pos -= 1
                self._update_scroll()
            return True

        elif event.key == pygame.K_RIGHT:
            if self._cursor_pos < len(self._text):
                self._cursor_pos += 1
                self._update_scroll()
            return True

        elif event.key == pygame.K_HOME:
            self._cursor_pos = 0
            self._update_scroll()
            return True

        elif event.key == pygame.K_END:
            self._cursor_pos = len(self._text)
            self._update_scroll()
            return True

        elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            if self._on_submit:
                self._on_submit(self)
            return True

        elif event.key == pygame.K_ESCAPE:
            self.blur()
            return True

        elif event.unicode and event.unicode.isprintable():
            self._insert_text(event.unicode)
            return True

        return False

    def update(self, dt: float) -> None:
        """Update cursor blink."""
        super().update(dt)

        if self.focused:
            self._cursor_timer += dt
            if self._cursor_timer >= self._cursor_blink_rate:
                self._cursor_timer = 0
                self._cursor_visible = not self._cursor_visible
        else:
            self._cursor_visible = False

    def focus(self) -> None:
        """Override to reset cursor blink on focus."""
        super().focus()
        self._cursor_visible = True
        self._cursor_timer = 0

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the text input."""
        if not self.visible:
            return

        abs_rect = self.absolute_rect

        # Get colors
        bg_color = self._bg_color or (50, 50, 50)

        # Draw background
        pygame.draw.rect(
            surface,
            bg_color,
            abs_rect,
            border_radius=self._border_radius
        )

        # Draw border
        if self._border_width > 0:
            if self.focused:
                border_color = self._focus_border_color or (66, 135, 245)
            else:
                border_color = self._border_color or (80, 80, 80)

            pygame.draw.rect(
                surface,
                border_color,
                abs_rect,
                width=self._border_width,
                border_radius=self._border_radius
            )

        # Create clipping rect for text
        content_rect = pygame.Rect(
            abs_rect.x + self._padding,
            abs_rect.y,
            abs_rect.width - (self._padding * 2),
            abs_rect.height
        )

        # Save clip and set new one
        old_clip = surface.get_clip()
        surface.set_clip(content_rect)

        font = self._get_font()

        # Draw text or placeholder
        if self._text:
            text_color = self._text_color or (255, 255, 255)

            text_surface = font.render(self._text, True, text_color)
            text_y = abs_rect.y + (abs_rect.height - text_surface.get_height()) // 2
            surface.blit(text_surface, (content_rect.x - self._scroll_offset, text_y))
        elif self._placeholder and not self.focused:
            placeholder_color = self._placeholder_color or (100, 100, 100)

            text_surface = font.render(self._placeholder, True, placeholder_color)
            text_y = abs_rect.y + (abs_rect.height - text_surface.get_height()) // 2
            surface.blit(text_surface, (content_rect.x, text_y))

        # Draw cursor when focused
        if self.focused and self._cursor_visible:
            cursor_x = font.size(self._text[:self._cursor_pos])[0] - self._scroll_offset
            cursor_color = self._text_color or (255, 255, 255)

            cursor_rect = pygame.Rect(
                content_rect.x + cursor_x,
                abs_rect.y + self._padding,
                2,
                abs_rect.height - (self._padding * 2)
            )
            pygame.draw.rect(surface, cursor_color, cursor_rect)

        # Restore clip
        surface.set_clip(old_clip)

        # Draw children
        self.draw_children(surface)

