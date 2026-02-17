"""
VBox container for vertical layout.
"""

from typing import Optional, Tuple

from .container import Container
from ..widget import Widget


class VBox(Container):
    """
    Vertical box layout container.

    Arranges children vertically from top to bottom with
    configurable spacing and alignment.

    Features:
    - Automatic vertical arrangement
    - Configurable spacing between items
    - Horizontal alignment (left, center, right, stretch)
    - Optional auto-sizing to fit children

    Example:
        vbox = VBox(
            x=10, y=10,
            width=200,
            spacing=10,
            align='center'
        )
        vbox.add_child(Label(text="Title"))
        vbox.add_child(Button(text="Option 1"))
        vbox.add_child(Button(text="Option 2"))
    """

    # Alignment constants
    ALIGN_LEFT = 'left'
    ALIGN_CENTER = 'center'
    ALIGN_RIGHT = 'right'
    ALIGN_STRETCH = 'stretch'  # Stretch children to fill width

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 200,
        height: int = 100,
        spacing: int = 8,
        align: str = ALIGN_LEFT,
        bg_color: Optional[Tuple[int, int, int, int]] = None,
        border_radius: int = 0,
        border_width: int = 0,
        border_color: Optional[Tuple[int, int, int]] = None,
        padding: int = 0,
        auto_size: bool = True,
        parent: Optional[Widget] = None
    ):
        """
        Initialize a VBox.

        Args:
            x: X position.
            y: Y position.
            width: Container width.
            height: Container height (ignored if auto_size is True).
            spacing: Vertical spacing between children.
            align: Horizontal alignment ('left', 'center', 'right', 'stretch').
            bg_color: Background color.
            border_radius: Corner radius.
            border_width: Border width.
            border_color: Border color.
            padding: Internal padding.
            auto_size: If True, auto-size height to fit children.
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
        """Get the horizontal alignment."""
        return self._align

    @align.setter
    def align(self, value: str) -> None:
        """Set the horizontal alignment."""
        self._align = value
        self._layout_children()

    def _layout_children(self) -> None:
        """Arrange children vertically."""
        if not self._children:
            return

        content_width = self.content_width
        current_y = self._padding

        for child in self._children:
            # Position vertically
            child.y = current_y

            # Horizontal alignment
            if self._align == self.ALIGN_CENTER:
                child.x = self._padding + (content_width - child.width) // 2
            elif self._align == self.ALIGN_RIGHT:
                child.x = self._padding + content_width - child.width
            elif self._align == self.ALIGN_STRETCH:
                child.x = self._padding
                child.width = content_width
            else:  # LEFT
                child.x = self._padding

            current_y += child.height + self._spacing

        # Auto-size height
        if self._auto_size:
            # Remove last spacing
            total_height = current_y - self._spacing + self._padding
            self._rect.height = max(self._padding * 2, total_height)

