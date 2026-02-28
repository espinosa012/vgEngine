"""
TabBar widget – a horizontal row of tab buttons with an active-tab indicator.
"""

from __future__ import annotations

from typing import Callable, List, Optional

import pygame

from ..widget import Widget


class TabBar(Widget):
    """
    Horizontal row of tabs.  One tab is selected at a time.

    Visual:
      ┌──────┬──────┬──────┐
      │ Tab1 │ Tab2 │ Tab3 │
      └──────┴══════┴──────┘   (active tab has a coloured bottom bar)

    Usage::

        bar = TabBar(tabs=["A", "B", "C"], width=300, height=36)
        bar.on_tab_change(lambda idx: print(f"Selected: {idx}"))
        ui.add(bar)
    """

    _focusable = False

    # Defaults
    _ACTIVE_BG     = (50, 90, 160)
    _INACTIVE_BG   = (38, 38, 55)
    _HOVER_BG      = (55, 55, 78)
    _ACTIVE_LINE   = (100, 170, 255)
    _SEPARATOR     = (65, 65, 90)
    _TEXT_ACTIVE   = (255, 255, 255)
    _TEXT_INACTIVE = (155, 155, 185)
    _INDICATOR_H   = 3   # height of the bottom active-tab bar

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 300,
        height: int = 36,
        tabs: List[str] = (),
        selected_index: int = 0,
        font_size: int = 17,
        active_bg_color=None,
        inactive_bg_color=None,
        active_line_color=None,
        parent: Optional[Widget] = None,
    ):
        super().__init__(x, y, width, height, parent)
        self._tabs: List[str] = list(tabs)
        self._selected_index: int = max(0, min(selected_index, len(self._tabs) - 1))
        self._font_size = font_size
        self._active_bg    = active_bg_color   or self._ACTIVE_BG
        self._inactive_bg  = inactive_bg_color or self._INACTIVE_BG
        self._active_line  = active_line_color or self._ACTIVE_LINE
        self._hovered_index: int = -1
        self._on_change: Optional[Callable[[int], None]] = None

    # ── Properties ──────────────────────────────────────────────────────────

    @property
    def selected_index(self) -> int:
        return self._selected_index

    @selected_index.setter
    def selected_index(self, value: int) -> None:
        value = max(0, min(value, len(self._tabs) - 1))
        if value != self._selected_index:
            self._selected_index = value
            if self._on_change:
                self._on_change(value)

    @property
    def selected_text(self) -> str:
        if 0 <= self._selected_index < len(self._tabs):
            return self._tabs[self._selected_index]
        return ""

    @property
    def tabs(self) -> List[str]:
        return list(self._tabs)

    # ── Callbacks ────────────────────────────────────────────────────────────

    def on_tab_change(self, callback: Callable[[int], None]) -> "TabBar":
        self._on_change = callback
        return self

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _tab_rects(self):
        """Return list of (screen_rect, index) for each tab."""
        n = len(self._tabs)
        if n == 0:
            return []
        ax, ay = self.get_absolute_position()
        w = self._rect.width
        h = self._rect.height
        base_w = w // n
        rects = []
        for i in range(n):
            # Distribute rounding remainder to last tab
            tab_w = base_w if i < n - 1 else w - base_w * (n - 1)
            rects.append(pygame.Rect(ax + i * base_w, ay, tab_w, h))
        return rects

    def _index_at(self, mx: int, my: int) -> int:
        """Return the tab index under pixel (mx, my), or -1."""
        for i, rect in enumerate(self._tab_rects()):
            if rect.collidepoint(mx, my):
                return i
        return -1

    # ── Event handling ───────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self._hovered_index = self._index_at(*event.pos)
            return False  # motion events are not consumed

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            idx = self._index_at(*event.pos)
            if idx >= 0:
                self.selected_index = idx
                return True

        return False

    # ── Drawing ──────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        font = pygame.font.Font(None, self._font_size)
        rects = self._tab_rects()
        ind_h = self._INDICATOR_H

        for i, (label, rect) in enumerate(zip(self._tabs, rects)):
            is_active  = (i == self._selected_index)
            is_hovered = (i == self._hovered_index) and not is_active

            # Background
            if is_active:
                bg = self._active_bg
            elif is_hovered:
                bg = self._HOVER_BG
            else:
                bg = self._inactive_bg
            pygame.draw.rect(surface, bg, rect)

            # Active bottom indicator
            if is_active:
                ind_rect = pygame.Rect(rect.x, rect.bottom - ind_h, rect.width, ind_h)
                pygame.draw.rect(surface, self._active_line, ind_rect)

            # Separator between tabs (skip first)
            if i > 0:
                pygame.draw.line(
                    surface, self._SEPARATOR,
                    (rect.x, rect.y + 4), (rect.x, rect.bottom - 4),
                )

            # Label
            color = self._TEXT_ACTIVE if is_active else self._TEXT_INACTIVE
            text_surf = font.render(label, True, color)
            text_rect = text_surf.get_rect(center=rect.center)
            if is_active:
                text_rect.centery -= ind_h // 2  # shift up slightly for indicator
            surface.blit(text_surf, text_rect)

        # Bottom border of the whole bar
        ax, ay = self.get_absolute_position()
        pygame.draw.line(
            surface, self._SEPARATOR,
            (ax, ay + self._rect.height - 1),
            (ax + self._rect.width - 1, ay + self._rect.height - 1),
        )

        self.draw_children(surface)
