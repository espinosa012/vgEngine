"""
Base GameObject class for the game framework.
Provides common functionality for all game entities.
"""
from typing import Optional, List
from abc import ABC, abstractmethod


class GameObject(ABC):
    """
    Base class for all game objects (characters, blocks, items, etc.).

    Provides common functionality like:
    - Position, rotation, and scale
    - Parent-child hierarchy
    - Active/visible state management
    - Update and render lifecycle methods
    - Layer system for organization
    """

    _id_counter = 0

    def __init__(self, x: float = 0, y: float = 0, name: Optional[str] = None):
        """
        Initialize a GameObject.

        Args:
            x: Initial x position
            y: Initial y position
            name: Optional name for the object
        """
        # Unique identifier
        GameObject._id_counter += 1
        self.id = GameObject._id_counter

        # Identification
        self.name = name or f"{self.__class__.__name__}_{self.id}"
        self.layer: int = 0

        # Transform properties
        self._x = x
        self._y = y
        self._rotation = 0.0  # in degrees
        self._scale_x = 1.0
        self._scale_y = 1.0

        # State
        self._active = True  # If false, won't update
        self._visible = True  # If false, won't render
        self._destroyed = False

        # Hierarchy
        self._parent: Optional[GameObject] = None
        self._children: List[GameObject] = []

    # ==================== Transform Properties ====================

    @property
    def x(self) -> float:
        """Get world x position."""
        if self._parent:
            return self._parent.x + self._x
        return self._x

    @x.setter
    def x(self, value: float):
        """Set local x position."""
        self._x = value

    @property
    def y(self) -> float:
        """Get world y position."""
        if self._parent:
            return self._parent.y + self._y
        return self._y

    @y.setter
    def y(self, value: float):
        """Set local y position."""
        self._y = value

    @property
    def local_x(self) -> float:
        """Get local x position (relative to parent)."""
        return self._x

    @property
    def local_y(self) -> float:
        """Get local y position (relative to parent)."""
        return self._y

    @property
    def rotation(self) -> float:
        """Get rotation in degrees."""
        return self._rotation

    @rotation.setter
    def rotation(self, value: float):
        """Set rotation in degrees."""
        self._rotation = value % 360

    @property
    def scale_x(self) -> float:
        """Get x scale factor."""
        return self._scale_x

    @scale_x.setter
    def scale_x(self, value: float):
        """Set x scale factor."""
        self._scale_x = value

    @property
    def scale_y(self) -> float:
        """Get y scale factor."""
        return self._scale_y

    @scale_y.setter
    def scale_y(self, value: float):
        """Set y scale factor."""
        self._scale_y = value

    def set_position(self, x: float, y: float):
        """Set local position."""
        self._x = x
        self._y = y

    def set_scale(self, scale_x: float, scale_y: Optional[float] = None):
        """Set scale (uniform if scale_y not provided)."""
        self._scale_x = scale_x
        self._scale_y = scale_y if scale_y is not None else scale_x

    def translate(self, dx: float, dy: float):
        """Move by delta values."""
        self._x += dx
        self._y += dy

    def rotate(self, degrees: float):
        """Rotate by delta degrees."""
        self._rotation = (self._rotation + degrees) % 360

    # ==================== State Properties ====================

    @property
    def active(self) -> bool:
        """Check if object is active (will be updated)."""
        return self._active and not self._destroyed

    @active.setter
    def active(self, value: bool):
        """Set active state."""
        self._active = value

    @property
    def visible(self) -> bool:
        """Check if object is visible (will be rendered)."""
        return self._visible and not self._destroyed

    @visible.setter
    def visible(self, value: bool):
        """Set visible state."""
        self._visible = value

    @property
    def destroyed(self) -> bool:
        """Check if object has been destroyed."""
        return self._destroyed

    # ==================== Hierarchy Methods ====================

    @property
    def parent(self) -> Optional['GameObject']:
        """Get parent object."""
        return self._parent

    @property
    def children(self) -> List['GameObject']:
        """Get list of children (read-only)."""
        return self._children.copy()

    def add_child(self, child: 'GameObject'):
        """
        Add a child object.

        Args:
            child: GameObject to add as child
        """
        if child._parent:
            child._parent.remove_child(child)

        child._parent = self
        if child not in self._children:
            self._children.append(child)

    def remove_child(self, child: 'GameObject'):
        """
        Remove a child object.

        Args:
            child: GameObject to remove
        """
        if child in self._children:
            child._parent = None
            self._children.remove(child)

    def get_child(self, name: str) -> Optional['GameObject']:
        """
        Find a child by name.

        Args:
            name: Name of the child to find

        Returns:
            The child object or None if not found
        """
        for child in self._children:
            if child.name == name:
                return child
        return None


    # ==================== Lifecycle Methods ====================

    def start(self):
        """
        Called when the object is first created/added to scene.
        Override this for initialization logic.
        """
        pass

    @abstractmethod
    def update(self, delta_time: float):
        """
        Called every frame to update object state.
        Must be implemented by subclasses.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        pass

    def fixed_update(self, fixed_delta: float):
        """
        Called at fixed intervals for physics updates.
        Override if needed.

        Args:
            fixed_delta: Fixed time step in seconds
        """
        pass

    @abstractmethod
    def render(self, renderer):
        """
        Called every frame to render the object.
        Must be implemented by subclasses.

        Args:
            renderer: Renderer object to draw with
        """
        pass

    def destroy(self):
        """
        Mark this object for destruction.
        Override for cleanup logic.
        """
        self._destroyed = True
        # Destroy all children
        for child in self._children.copy():
            child.destroy()

    # ==================== Utility Methods ====================

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, name='{self.name}', pos=({self.x:.1f}, {self.y:.1f}))>"

    def __str__(self) -> str:
        return self.name

