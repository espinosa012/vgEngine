"""
Core game framework module.
Provides base classes for building games with Python.
"""

from core.base.game_object import GameObject
from .character.base import BaseCharacter

__all__ = [
    'GameObject',
    'BaseCharacter',
]

