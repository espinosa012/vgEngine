"""
Character package for game entities.
BaseCharacter has been consolidated into core.character.
"""

from core.character import BaseCharacter
from .character import GameCharacter

__all__ = [
    'BaseCharacter',
    'GameCharacter',
]

