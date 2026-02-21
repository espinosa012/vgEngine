"""
Base character controller for handling character input and control.
"""

from typing import Optional, TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from ..character import BaseCharacter


class BaseCharacterController(ABC):
    """
    Abstract base class for character controllers.

    Controllers handle input and translate it into character actions.
    Different controller implementations can provide different input methods:
    - Keyboard (arrow keys, WASD)
    - Mouse
    - Gamepad
    - AI-controlled

    Attributes:
        character: The character being controlled
        enabled: Whether the controller is currently active
    """

    def __init__(self, character: Optional['BaseCharacter'] = None):
        """
        Initialize the controller.

        Args:
            character: The character to control (can be set later)
        """
        self._character: Optional['BaseCharacter'] = character
        self._enabled: bool = True

    # ==================== Properties ====================

    @property
    def character(self) -> Optional['BaseCharacter']:
        """Get the controlled character."""
        return self._character

    @character.setter
    def character(self, value: Optional['BaseCharacter']):
        """Set the controlled character."""
        self._character = value

    @property
    def enabled(self) -> bool:
        """Check if the controller is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        """Enable or disable the controller."""
        self._enabled = value

    # ==================== Core Methods ====================

    def attach(self, character: 'BaseCharacter'):
        """
        Attach this controller to a character.

        Args:
            character: The character to control
        """
        self._character = character

    def detach(self):
        """Detach the controller from its character."""
        self._character = None

    @abstractmethod
    def update(self, delta_time: float):
        """
        Update the controller state.

        This method should be called each frame to process input
        and update the character accordingly.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        pass

    def handle_event(self, event) -> bool:
        """
        Handle an input event.

        Override this in subclasses to handle specific events
        (key presses, mouse clicks, etc.)

        Args:
            event: The input event to handle

        Returns:
            True if the event was consumed, False otherwise
        """
        return False

