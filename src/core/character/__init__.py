"""
Character package for core game entities.
"""

from .base import BaseCharacter
from .renderer import CharacterRenderer
from .shape import CharacterShape, RectShape

__all__ = [
    'BaseCharacter',
    'CharacterRenderer',
    'CharacterShape',
    'RectShape',
]

