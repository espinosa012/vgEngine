"""
SelectableList widget.

A scrollable panel containing a vertical list of selectable items.
Each item is a labelled row that highlights on hover and stays highlighted
when selected.  Only one item can be selected at a time.

Usage::

    lst = SelectableList(x=0, y=0, width=200, height=300)
    lst.add_item("Hero")
    lst.add_item("Enemy")
    lst.on_select(lambda idx, label: print(idx, label))
    # Later:
    lst.add_item("Wizard")
    lst.remove_item(0)
    lst.clear_items()
"""

from __future__ import annotations

from typing import Callable, List, Optional, Tuple

import pygame

from ..widget import Widget
from ..containers.scroll_view import ScrollView
from ..containers.vbox import VBox


# ---------------------------------------------------------------------------
# Internal row widget
# ---------------------------------------------------------------------------

class _ListRow(Widget):
    """A single selectable row inside a SelectableList."""

    _focusable = True

    # Visual defaults (overridden by SelectableList)
    COLOR_NORMAL:   Tuple[int, int, int] = (38, 38, 55)
    COLOR_HOVER:    Tuple[int, int, int] = (58, 58, 80)
    COLOR_SELECTED: Tuple[int, int, int] = (55, 100, 175)
    COLOR_TEXT:     Tuple[int, int, int] = (210, 210, 230)
    COLOR_TEXT_SEL: Tuple[int, int, int] = (255, 255, 255)
    COLOR_ACCENT:   Tuple[int, int, int] = (80, 140, 255)  # left-edge bar when selected

    def __init__(
        self,
        index: int,
        label: str,
        width: int,
        height: int,
        font_size: int,
        color_normal: Tuple,
        color_hover: Tuple,
        color_selected: Tuple,
        color_text: Tuple,
        color_text_sel: Tuple,
        color_accent: Tuple,
        border_radius: int,
        on_row_click: Callable[[int], None],
    ) -> None:
        super().__init__(0, 0, width, height)
        self.index = index
        self.label = label
        self._font_size = font_size
        self._selected = False
        self._kb_focused = False       # keyboard cursor is on this row

        self._c_normal   = color_normal
        self._c_hover    = color_hover
        self._c_selected = color_selected
        self._c_text     = color_text
        self._c_text_sel = color_text_sel
        self._c_accent   = color_accent
        self._brad       = border_radius

        self._on_row_click = on_row_click
        self._font: Optional[pygame.font.Font] = None

    # ------------------------------------------------------------------

    @property
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, value: bool) -> None:
        self._selected = value

    @property
    def kb_focused(self) -> bool:
        """True when the keyboard cursor is resting on this row."""
        return self._kb_focused

    @kb_focused.setter
    def kb_focused(self, value: bool) -> None:
        self._kb_focused = value

    # ------------------------------------------------------------------

    def _get_bg(self) -> Tuple:
        if self._selected:
            return self._c_selected
        if self._kb_focused:
            # Midpoint between normal and hover — distinct but subtle
            return tuple(
                (a + b) // 2
                for a, b in zip(self._c_normal, self._c_hover)
            )
        if self.hovered:
            return self._c_hover
        return self._c_normal

    def _get_text_color(self) -> Tuple:
        return self._c_text_sel if (self._selected or self._kb_focused) else self._c_text

    def _get_font(self) -> pygame.font.Font:
        if self._font is None:
            self._font = pygame.font.Font(None, self._font_size)
        return self._font

    # ------------------------------------------------------------------

    def _handle_mouse_up(self, event: pygame.event.Event) -> bool:
        if event.button != 1:
            return False
        if self._state.pressed:
            self._state.pressed = False
            if self.contains_point(event.pos[0], event.pos[1]):
                self._on_row_click(self.index)
                return True
        return False

    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        ar = self.absolute_rect
        bg = self._get_bg()

        # Background
        if self._brad > 0:
            pygame.draw.rect(surface, bg, ar, border_radius=self._brad)
        else:
            pygame.draw.rect(surface, bg, ar)

        # Left accent bar when selected
        if self._selected:
            bar = pygame.Rect(ar.x, ar.y + 3, 3, ar.height - 6)
            pygame.draw.rect(surface, self._c_accent, bar,
                             border_radius=min(2, self._brad))

        # Keyboard-cursor outline (dashed-style: thin border)
        if self._kb_focused and not self._selected:
            pygame.draw.rect(surface, self._c_accent, ar,
                             width=1,
                             border_radius=self._brad)

        # Label text (left-aligned, vertically centred, small left padding)
        font = self._get_font()
        txt_surf = font.render(self.label, True, self._get_text_color())
        tx = ar.x + 12
        ty = ar.y + (ar.height - txt_surf.get_height()) // 2
        surface.blit(txt_surf, (tx, ty))

    def update(self, dt: float) -> None:
        pass  # no animation needed


# ---------------------------------------------------------------------------
# SelectableList
# ---------------------------------------------------------------------------

class SelectableList(Widget):
    """
    Scrollable panel containing selectable labelled items.

    Keyboard navigation
    -------------------
    The widget must have focus (click anywhere on it, or call .focus()).
    • ↑ / ↓   — move the keyboard cursor up / down (wraps around).
    • Space    — confirm: selects the row under the cursor (same toggle
                 behaviour as a mouse click).
    • ↑ / ↓ also scroll the view so the cursor row is always visible.

    Callbacks
    ---------
    on_select(index: int, label: str)
        Fired every time the selection changes (including programmatic ones).

    Parameters
    ----------
    x, y            Widget top-left position.
    width, height   Outer dimensions including border and title bar (if any).
    title           Optional title rendered above the list. Pass ``""`` to hide.
    item_height     Height of each row in pixels (default 28).
    font_size       Font size used for row labels (default 15).
    auto_scroll     If True, scroll to the newly added item automatically.
    bg_color        Background of the scroll area.
    item_normal     Normal row background colour.
    item_hover      Hovered row background colour.
    item_selected   Selected row background colour.
    item_text       Normal text colour.
    item_text_sel   Selected text colour.
    item_accent     Left-edge accent bar colour on selected row.
    border_radius   Corner radius for the outer widget and each row.
    border_color    Outer border colour.
    border_width    Outer border width (0 = none).
    title_color     Title text colour.
    title_font_size Title font size.
    """

    # SelectableList is focusable so the UIManager routes keyboard events to it
    _focusable = True

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 200,
        height: int = 300,
        title: str = "",
        item_height: int = 28,
        font_size: int = 15,
        auto_scroll: bool = True,
        bg_color: Tuple = (28, 28, 44, 240),
        item_normal: Tuple = (38, 38, 55),
        item_hover: Tuple = (55, 55, 78),
        item_selected: Tuple = (50, 95, 170),
        item_text: Tuple = (205, 205, 225),
        item_text_sel: Tuple = (255, 255, 255),
        item_accent: Tuple = (80, 140, 255),
        border_radius: int = 4,
        border_color: Optional[Tuple] = (70, 70, 100),
        border_width: int = 1,
        title_color: Tuple = (200, 200, 230),
        title_font_size: int = 15,
        parent: Optional[Widget] = None,
    ) -> None:
        super().__init__(x, y, width, height, parent)

        self._title       = title
        self._item_height = item_height
        self._font_size   = font_size
        self._auto_scroll = auto_scroll

        self._bg_color      = bg_color
        self._item_normal   = item_normal
        self._item_hover    = item_hover
        self._item_selected = item_selected
        self._item_text     = item_text
        self._item_text_sel = item_text_sel
        self._item_accent   = item_accent
        self._border_radius = border_radius
        self._border_color  = border_color
        self._border_width  = border_width
        self._title_color   = title_color
        self._title_fsize   = title_font_size

        self._on_select_cb: Optional[Callable[[int, str], None]] = None

        # Internal state
        self._items:        List[str]      = []   # labels in order
        self._rows:         List[_ListRow] = []   # matching row widgets
        self._selected_idx: int            = -1   # -1 = nothing selected
        self._cursor_idx:   int            = -1   # keyboard navigation cursor

        self._title_font:  Optional[pygame.font.Font] = None
        self._title_h: int = (title_font_size + 8) if title else 0

        # Scroll area fills the widget below the (optional) title bar
        scroll_y = self._title_h
        scroll_h = height - scroll_y
        self._scroll_view = ScrollView(
            x=0, y=scroll_y,
            width=width,
            height=scroll_h,
            bg_color=tuple(bg_color) if bg_color else None,  # type: ignore[arg-type]
            scroll_speed=item_height,
            show_scrollbar=True,
            scrollbar_color=(95, 95, 128),
            scrollbar_track_color=(38, 38, 55),
            border_radius=border_radius if not title else 0,
            padding=4,
        )
        # VBox inside the scroll view – auto-sized, no spacing between rows
        self._vbox = VBox(
            width=width - 12,   # leave room for scrollbar
            spacing=2,
            align=VBox.ALIGN_LEFT,
            auto_size=True,
            padding=0,
        )
        self._scroll_view.add_child(self._vbox)
        self.add_child(self._scroll_view)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def on_select(self, callback: Callable[[int, str], None]) -> "SelectableList":
        """
        Register a callback invoked whenever the selection changes.

        Signature: ``callback(index: int, label: str)``

        Returns self for chaining.
        """
        self._on_select_cb = callback
        return self

    def add_item(self, label: str) -> int:
        """
        Append a new item to the list.

        Returns the index of the newly added item.
        """
        idx = len(self._items)
        self._items.append(label)

        row = _ListRow(
            index=idx,
            label=label,
            width=self._vbox.width,
            height=self._item_height,
            font_size=self._font_size,
            color_normal=self._item_normal,
            color_hover=self._item_hover,
            color_selected=self._item_selected,
            color_text=self._item_text,
            color_text_sel=self._item_text_sel,
            color_accent=self._item_accent,
            border_radius=self._border_radius,
            on_row_click=self._on_row_click,
        )
        self._rows.append(row)
        self._vbox.add_child(row)

        if self._auto_scroll:
            # Scroll to the bottom so the new item is visible
            sv = self._scroll_view
            content_h = sum(r.height + 2 for r in self._rows) + 4
            sv.scroll_y = max(0.0, float(content_h - sv.height))

        return idx

    def remove_item(self, index: int) -> None:
        """Remove the item at *index* (0-based)."""
        if not (0 <= index < len(self._items)):
            return

        row = self._rows[index]
        self._vbox.remove_child(row)
        self._items.pop(index)
        self._rows.pop(index)

        # Re-index rows after the removed one
        for i in range(index, len(self._rows)):
            self._rows[i].index = i

        # Fix selection
        if self._selected_idx == index:
            self._selected_idx = -1
        elif self._selected_idx > index:
            self._selected_idx -= 1

        # Fix cursor
        if self._cursor_idx >= len(self._rows):
            self._cursor_idx = len(self._rows) - 1

    def clear_items(self) -> None:
        """Remove all items."""
        for row in self._rows:
            self._vbox.remove_child(row)
        self._items.clear()
        self._rows.clear()
        self._selected_idx = -1
        self._cursor_idx   = -1

    def select(self, index: int) -> None:
        """Programmatically select an item by index."""
        self._set_selection(index)

    def deselect(self) -> None:
        """Clear the current selection."""
        self._set_selection(-1)

    @property
    def selected_index(self) -> int:
        """Currently selected index, or -1 if nothing is selected."""
        return self._selected_idx

    @property
    def selected_label(self) -> Optional[str]:
        """Label of the currently selected item, or None."""
        if 0 <= self._selected_idx < len(self._items):
            return self._items[self._selected_idx]
        return None

    @property
    def item_count(self) -> int:
        """Number of items in the list."""
        return len(self._items)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _on_row_click(self, index: int) -> None:
        """Called by a _ListRow when it is clicked."""
        # Move keyboard cursor to the clicked row
        self._set_cursor(index)
        # Clicking an already-selected row deselects it
        if self._selected_idx == index:
            self._set_selection(-1)
        else:
            self._set_selection(index)

    def _set_selection(self, index: int) -> None:
        """Update the selection state and fire the callback."""
        # Deselect previous
        if 0 <= self._selected_idx < len(self._rows):
            self._rows[self._selected_idx].selected = False

        self._selected_idx = index

        # Select new
        if 0 <= index < len(self._rows):
            self._rows[index].selected = True

        if self._on_select_cb:
            label = self._items[index] if 0 <= index < len(self._items) else ""
            self._on_select_cb(index, label)

    def _set_cursor(self, index: int) -> None:
        """Move the keyboard cursor to *index* without changing the selection."""
        if not self._rows:
            self._cursor_idx = -1
            return

        # Clear old cursor highlight
        if 0 <= self._cursor_idx < len(self._rows):
            self._rows[self._cursor_idx].kb_focused = False

        self._cursor_idx = max(0, min(index, len(self._rows) - 1))

        # Apply new cursor highlight
        self._rows[self._cursor_idx].kb_focused = True

        # Ensure the cursor row is visible in the scroll view
        self._scroll_view.scroll_to_widget(self._rows[self._cursor_idx])

    # ------------------------------------------------------------------
    # Widget overrides
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> bool:
        # Let the scroll view (and its children / rows) handle mouse events first
        if event.type != pygame.KEYDOWN:
            return self._scroll_view.handle_event(event)

        # ── Keyboard navigation ──────────────────────────────────────
        if not self._state.focused or not self._rows:
            return self._scroll_view.handle_event(event)

        key = event.key

        if key == pygame.K_DOWN:
            if self._cursor_idx < 0:
                self._set_cursor(0)
            else:
                self._set_cursor((self._cursor_idx + 1) % len(self._rows))
            return True

        if key == pygame.K_UP:
            if self._cursor_idx < 0:
                self._set_cursor(len(self._rows) - 1)
            else:
                self._set_cursor((self._cursor_idx - 1) % len(self._rows))
            return True

        if key == pygame.K_SPACE and self._cursor_idx >= 0:
            self._on_row_click(self._cursor_idx)
            return True

        return self._scroll_view.handle_event(event)

    def _handle_mouse_down(self, event: pygame.event.Event) -> bool:
        """Gain focus when clicked anywhere on the widget."""
        if event.button == 1 and self.contains_point(event.pos[0], event.pos[1]):
            self.focus()
        return super()._handle_mouse_down(event)

    def update(self, dt: float) -> None:
        self._scroll_view.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        ar = self.absolute_rect

        # Outer background + border
        if self._bg_color:
            tmp = pygame.Surface((ar.width, ar.height), pygame.SRCALPHA)
            if self._border_radius > 0:
                pygame.draw.rect(
                    tmp, self._bg_color,
                    pygame.Rect(0, 0, ar.width, ar.height),
                    border_radius=self._border_radius,
                )
            else:
                tmp.fill(self._bg_color)
            surface.blit(tmp, (ar.x, ar.y))

        # Border — brighten slightly when the widget has keyboard focus
        b_color = self._border_color or (70, 70, 100)
        if self._border_width > 0:
            if self._state.focused:
                b_color = tuple(min(255, c + 55) for c in b_color)  # type: ignore[assignment]
            pygame.draw.rect(
                surface, b_color, ar,
                width=self._border_width,
                border_radius=self._border_radius,
            )

        # Title bar
        if self._title:
            if self._title_font is None:
                self._title_font = pygame.font.Font(None, self._title_fsize)
            txt = self._title_font.render(self._title, True, self._title_color)
            tx = ar.x + 10
            ty = ar.y + (self._title_h - txt.get_height()) // 2
            surface.blit(txt, (tx, ty))

            # Thin separator line
            sep_y = ar.y + self._title_h - 1
            pygame.draw.line(
                surface,
                b_color,
                (ar.x + 4, sep_y),
                (ar.x + ar.width - 4, sep_y),
            )

        # Scroll area
        self._scroll_view.draw(surface)

