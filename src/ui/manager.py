"""
UI Manager for handling the widget hierarchy and event distribution.

The UIManager acts as the root container for all UI widgets and integrates
with the game loop.
"""

from typing import Optional, List

import pygame

from .widget import Widget


class UIManager:
    """
    Central manager for the UI system.

    Responsibilities:
    - Acts as root container for widgets
    - Distributes events to the widget tree
    - Manages focus
    - Coordinates updates and rendering

    Usage:
        ui = UIManager(screen_width, screen_height)
        ui.add(button)
        ui.add(panel)

        # In game loop:
        for event in pygame.event.get():
            ui.handle_event(event)

        ui.update(dt)
        ui.draw(screen)
    """

    def __init__(
        self,
        width: int,
        height: int
    ):
        """
        Initialize the UI manager.

        Args:
            width: Screen width.
            height: Screen height.
        """
        self._width = width
        self._height = height
        self._widgets: List[Widget] = []
        self._focused_widget: Optional[Widget] = None
        self._hovered_widget: Optional[Widget] = None

    @property
    def width(self) -> int:
        """Screen width."""
        return self._width

    @property
    def height(self) -> int:
        """Screen height."""
        return self._height

    @property
    def focused_widget(self) -> Optional[Widget]:
        """Currently focused widget."""
        return self._focused_widget

    def add(self, widget: Widget) -> None:
        """
        Add a widget to the UI manager.

        Args:
            widget: Widget to add.
        """
        if widget not in self._widgets:
            self._widgets.append(widget)

    def remove(self, widget: Widget) -> None:
        """
        Remove a widget from the UI manager.

        Args:
            widget: Widget to remove.
        """
        if widget in self._widgets:
            self._widgets.remove(widget)
            if self._focused_widget == widget:
                self._focused_widget = None
            if self._hovered_widget == widget:
                self._hovered_widget = None

    def clear(self) -> None:
        """Remove all widgets."""
        self._widgets.clear()
        self._focused_widget = None
        self._hovered_widget = None

    def get_widget_at(self, x: int, y: int) -> Optional[Widget]:
        """
        Get the topmost widget at a screen position.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Returns:
            The widget at the position, or None.
        """
        # Iterate in reverse to get topmost widget first
        for widget in reversed(self._widgets):
            if widget.visible and widget.contains_point(x, y):
                # Check children
                child = widget.get_child_at(x, y)
                if child:
                    return child
                return widget
        return None

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle a pygame event and distribute to widgets.

        Args:
            event: Pygame event to handle.

        Returns:
            True if any widget consumed the event.
        """
        # Overlay pass first — open popups (e.g. dropdowns) get priority so
        # that clicks on their lists are not stolen by widgets drawn below them.
        for widget in reversed(self._widgets):
            if widget.handle_overlay_event(event):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self._update_focus(event.pos[0], event.pos[1])
                return True

        # Handle hover tracking
        if event.type == pygame.MOUSEMOTION:
            self._update_hover(event.pos[0], event.pos[1])

        # Distribute to widgets (topmost first)
        for widget in reversed(self._widgets):
            if widget.handle_event(event):
                # Track focus changes
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self._update_focus(event.pos[0], event.pos[1])
                return True

        # Click outside any widget - clear focus
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._focused_widget:
                self._focused_widget.blur()
                self._focused_widget = None

        return False

    def _update_hover(self, x: int, y: int) -> None:
        """Update hover state based on mouse position."""
        widget = self.get_widget_at(x, y)

        if widget != self._hovered_widget:
            # Mouse left old widget
            if self._hovered_widget:
                self._hovered_widget._state.hovered = False
                if self._hovered_widget._on_hover_exit:
                    self._hovered_widget._on_hover_exit(self._hovered_widget)

            # Mouse entered new widget
            if widget:
                widget._state.hovered = True
                if widget._on_hover_enter:
                    widget._on_hover_enter(widget)

            self._hovered_widget = widget

    def _update_focus(self, x: int, y: int) -> None:
        """Update focus based on click position."""
        widget = self.get_widget_at(x, y)

        if widget != self._focused_widget:
            # Blur old widget
            if self._focused_widget:
                self._focused_widget.blur()

            # Focus new widget
            if widget and widget.enabled:
                widget.focus()
                self._focused_widget = widget
            else:
                self._focused_widget = None

    def update(self, dt: float) -> None:
        """
        Update all widgets.

        Args:
            dt: Delta time since last update in seconds.
        """
        for widget in self._widgets:
            widget.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw all visible widgets, then draw overlay content on top.

        The two-pass approach ensures that popup elements such as open
        dropdowns are always rendered above every other widget regardless
        of their position in the hierarchy.

        Args:
            surface: Pygame surface to draw on.
        """
        for widget in self._widgets:
            if widget.visible:
                widget.draw(surface)

        # Overlay pass — drawn after everything else, no clip restrictions.
        for widget in self._widgets:
            if widget.visible:
                widget.draw_overlay(surface)

    def resize(self, width: int, height: int) -> None:
        """
        Handle screen resize.

        Args:
            width: New screen width.
            height: New screen height.
        """
        self._width = width
        self._height = height

    def __len__(self) -> int:
        """Number of top-level widgets."""
        return len(self._widgets)

    def __iter__(self):
        """Iterate over widgets."""
        return iter(self._widgets)

