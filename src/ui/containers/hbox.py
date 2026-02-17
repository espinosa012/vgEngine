"""
HBox container for horizontal layout.
"""

from typing import Optional, Tuple

from .container import Container
from ..widget import Widget


class HBox(Container):
    """
    Horizontal box layout container.

    Arranges children horizontally from left to right with
    configurable spacing and alignment.

    Features:
    - Automatic horizontal arrangement
    - Configurable spacing between items
    - Vertical alignment (top, center, bottom, stretch)
    - Optional auto-sizing to fit children

    Example:
        hbox = HBox(
            x=10, y=10,
            height=40,
            spacing=10,
            align='center'
        )
        hbox.add_child(Button(text="Save"))
        hbox.add_child(Button(text="Cancel"))
        hbox.add_child(Button(text="Help"))
    """

    # Alignment constants
    ALIGN_TOP = 'top'
    ALIGN_CENTER = 'center'
    ALIGN_BOTTOM = 'bottom'
    ALIGN_STRETCH = 'stretch'  # Stretch children to fill height

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 200,
        height: int = 40,
        spacing: int = 8,
        align: str = ALIGN_CENTER,
        bg_color: Optional[Tuple[int, int, int, int]] = None,
        border_radius: int = 0,
        border_width: int = 0,
        border_color: Optional[Tuple[int, int, int]] = None,
        padding: int = 0,
        auto_size: bool = True,
        parent: Optional[Widget] = None,
    ):
        """
        Initialize an HBox.

        Args:
            x: X position.
            y: Y position.
            width: Container width (ignored if auto_size is True).
            height: Container height.
            spacing: Horizontal spacing between children.
            align: Vertical alignment ('top', 'center', 'bottom', 'stretch').
            bg_color: Background color.
            border_radius: Corner radius.
            border_width: Border width.
            border_color: Border color.
            padding: Internal padding.
            auto_size: If True, auto-size width to fit children.
            parent: Parent widget.
            
        """
        super().__init__(
            x, y, width, height,
            bg_color, border_radius, border_width, border_color,
            padding, auto_size, parent
        )

        self._spacing = spacing
        self._align = align

    @property
    def spacing(self) -> int:
        """Get the spacing between children."""
        return self._spacing

    @spacing.setter
    def spacing(self, value: int) -> None:
        """Set the spacing between children."""
        self._spacing = max(0, value)
        self._layout_children()

    @property
    def align(self) -> str:
        """Get the vertical alignment."""
        return self._align

    @align.setter
    def align(self, value: str) -> None:
        """Set the vertical alignment."""
        self._align = value
        self._layout_children()

    def _layout_children(self) -> None:
        """Arrange children horizontally."""
        if not self._children:
            return

        content_height = self.content_height
        current_x = self._padding

        for child in self._children:
            # Position horizontally
            child.x = current_x

            # Vertical alignment
            if self._align == self.ALIGN_CENTER:
                child.y = self._padding + (content_height - child.height) // 2
            elif self._align == self.ALIGN_BOTTOM:
                child.y = self._padding + content_height - child.height
            elif self._align == self.ALIGN_STRETCH:
                child.y = self._padding
                child.height = content_height
            else:  # TOP
                child.y = self._padding

            current_x += child.width + self._spacing

        # Auto-size width
        if self._auto_size:
            # Remove last spacing
            total_width = current_x - self._spacing + self._padding
            self._rect.width = max(self._padding * 2, total_width)

