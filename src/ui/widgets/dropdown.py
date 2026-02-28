"""
Dropdown (select / combo-box) widget for the UI framework.

Displays a button that, when clicked, shows a scrollable list of options.
The user can pick one option which then becomes the current selection.
"""

from typing import Optional, Tuple, List, Callable

import pygame

from ..widget import Widget


class Dropdown(Widget):
    """
    A dropdown / combo-box widget.

    Features:
    - Shows the currently selected option as a button.
    - Clicking the button opens a list of options below it.
    - Clicking an option selects it and closes the list.
    - Clicking anywhere outside the open list closes it.
    - Optional on_change callback.

    Example::

        dd = Dropdown(
            x=10, y=10, width=200, height=30,
            options=["Perlin", "Simplex", "Value"],
            selected_index=0,
        )
        dd.on_change(lambda idx, name: print(f"Selected: {name}"))
    """

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 180,
        height: int = 30,
        options: Optional[List[str]] = None,
        selected_index: int = 0,
        font_size: int = 18,
        text_color: Tuple[int, int, int] = (255, 255, 255),
        bg_color: Tuple[int, int, int] = (50, 50, 65),
        hover_color: Tuple[int, int, int] = (70, 70, 90),
        selected_color: Tuple[int, int, int] = (50, 130, 80),
        border_color: Tuple[int, int, int] = (100, 100, 130),
        border_radius: int = 4,
        max_visible: int = 6,
        parent: Optional[Widget] = None,
    ):
        super().__init__(x, y, width, height, parent)

        self._options: List[str] = list(options or [])
        self._selected_index: int = selected_index if self._options else -1
        self._font_size = font_size
        self._text_color = text_color
        self._bg_color = bg_color
        self._hover_color = hover_color
        self._selected_color = selected_color
        self._border_color = border_color
        self._border_radius = border_radius
        self._max_visible = max_visible

        self._open = False
        self._hovered_option: int = -1
        self._scroll_offset: int = 0

        self._on_change_cb: Optional[Callable[[int, str], None]] = None

    # -- Public API -----------------------------------------------------------

    @property
    def options(self) -> List[str]:
        return list(self._options)

    @options.setter
    def options(self, value: List[str]) -> None:
        self._options = list(value)
        if self._selected_index >= len(self._options):
            self._selected_index = 0 if self._options else -1
        self._scroll_offset = 0

    @property
    def selected_index(self) -> int:
        return self._selected_index

    @selected_index.setter
    def selected_index(self, value: int) -> None:
        if 0 <= value < len(self._options):
            self._selected_index = value

    @property
    def selected_text(self) -> str:
        if 0 <= self._selected_index < len(self._options):
            return self._options[self._selected_index]
        return ""

    @property
    def is_open(self) -> bool:
        return self._open

    def on_change(self, callback: Callable[[int, str], None]) -> "Dropdown":
        """Set callback invoked when the selection changes: ``cb(index, text)``."""
        self._on_change_cb = callback
        return self

    # -- Geometry helpers -----------------------------------------------------

    def _item_height(self) -> int:
        return self._rect.height

    def _list_rect(self) -> pygame.Rect:
        """Return the absolute rect of the open option list."""
        abs_x, abs_y = self.get_absolute_position()
        ih = self._item_height()
        visible = min(len(self._options), self._max_visible)
        return pygame.Rect(abs_x, abs_y + self._rect.height, self._rect.width, ih * visible)

    def _can_scroll_up(self) -> bool:
        return self._scroll_offset > 0

    def _can_scroll_down(self) -> bool:
        visible = min(len(self._options), self._max_visible)
        return self._scroll_offset + visible < len(self._options)

    # -- Event handling -------------------------------------------------------

    def handle_overlay_event(self, event: pygame.event.Event) -> bool:
        """Handle list interactions with priority before normal event dispatch.

        When the list is open, consume clicks inside it so that widgets drawn
        below the list (e.g. another dropdown's HBox row) cannot steal them.
        Outside clicks close the list without consuming the event so the click
        can still reach its real target.
        """
        if super().handle_overlay_event(event):
            return True

        if not self.visible or not self.enabled or not self._open:
            return False

        lr = self._list_rect()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if lr.collidepoint(mx, my):
                rel_y = my - lr.y
                idx = self._scroll_offset + rel_y // self._item_height()
                if 0 <= idx < len(self._options):
                    old = self._selected_index
                    self._selected_index = idx
                    self._open = False
                    self._hovered_option = -1
                    if idx != old and self._on_change_cb:
                        self._on_change_cb(idx, self._options[idx])
                else:
                    self._open = False
                return True  # Consume — prevent widgets behind the list from seeing this

            # Click outside both the list and the button → close but don't consume
            abs_rect = self.absolute_rect
            if not abs_rect.collidepoint(mx, my):
                self._open = False
            return False

        if event.type == pygame.MOUSEWHEEL:
            if lr.collidepoint(*pygame.mouse.get_pos()):
                if event.y > 0 and self._can_scroll_up():
                    self._scroll_offset -= 1
                elif event.y < 0 and self._can_scroll_down():
                    self._scroll_offset += 1
                return True

        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            if lr.collidepoint(mx, my):
                self._hovered_option = self._scroll_offset + (my - lr.y) // self._item_height()
            else:
                self._hovered_option = -1

        return False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False

        # Only handle clicks on the button itself; list interactions are in handle_overlay_event.
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            abs_rect = self.absolute_rect
            if abs_rect.collidepoint(event.pos[0], event.pos[1]):
                self._open = not self._open
                self._hovered_option = -1
                if self._open:
                    self._ensure_visible(self._selected_index)
                return True

        return False

    def _ensure_visible(self, idx: int) -> None:
        visible = min(len(self._options), self._max_visible)
        if idx < self._scroll_offset:
            self._scroll_offset = idx
        elif idx >= self._scroll_offset + visible:
            self._scroll_offset = idx - visible + 1

    # -- Update / Draw --------------------------------------------------------

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the dropdown button only.  The open list is drawn in draw_overlay."""
        if not self.visible:
            return

        abs_rect = self.absolute_rect
        font = pygame.font.Font(None, self._font_size)

        # Button background
        bg = self._hover_color if self._state.hovered and not self._open else self._bg_color
        pygame.draw.rect(surface, bg, abs_rect, border_radius=self._border_radius)
        pygame.draw.rect(surface, self._border_color, abs_rect, width=1, border_radius=self._border_radius)

        # Selected text
        text = self.selected_text or "—"
        txt_surf = font.render(text, True, self._text_color)
        txt_rect = txt_surf.get_rect(midleft=(abs_rect.x + 8, abs_rect.centery))
        surface.blit(txt_surf, txt_rect)

        # Arrow indicator
        arrow = "▼" if not self._open else "▲"
        arr_surf = font.render(arrow, True, self._text_color)
        arr_rect = arr_surf.get_rect(midright=(abs_rect.right - 8, abs_rect.centery))
        surface.blit(arr_surf, arr_rect)

        self.draw_children(surface)

    def draw_overlay(self, surface: pygame.Surface) -> None:
        """Draw the open option list on top of all other widgets.

        Called by UIManager after the full widget tree has been drawn so the
        list is never obscured by sibling or parent widgets.
        """
        super().draw_overlay(surface)

        if not self.visible or not self._open or not self._options:
            return

        font = pygame.font.Font(None, self._font_size)
        lr = self._list_rect()
        ih = self._item_height()
        visible = min(len(self._options), self._max_visible)

        # List background + border
        pygame.draw.rect(surface, self._bg_color, lr, border_radius=self._border_radius)
        pygame.draw.rect(surface, self._border_color, lr, width=1, border_radius=self._border_radius)

        for i in range(visible):
            idx = self._scroll_offset + i
            if idx >= len(self._options):
                break

            item_rect = pygame.Rect(lr.x, lr.y + i * ih, lr.width, ih)

            if idx == self._selected_index:
                pygame.draw.rect(surface, self._selected_color, item_rect)
            elif idx == self._hovered_option:
                pygame.draw.rect(surface, self._hover_color, item_rect)

            opt_surf = font.render(self._options[idx], True, self._text_color)
            opt_rect = opt_surf.get_rect(midleft=(item_rect.x + 8, item_rect.centery))
            surface.blit(opt_surf, opt_rect)

        # Scroll indicators
        if self._can_scroll_up():
            up_surf = font.render("▲", True, (180, 180, 180))
            surface.blit(up_surf, (lr.right - 18, lr.y + 2))
        if self._can_scroll_down():
            dn_surf = font.render("▼", True, (180, 180, 180))
            surface.blit(dn_surf, (lr.right - 18, lr.bottom - ih + 2))

