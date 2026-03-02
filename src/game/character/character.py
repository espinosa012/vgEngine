from typing import Optional, Tuple

from core.character.base import BaseCharacter
from core.character.shape import CharacterShape

GridPos = Tuple[int, int]


class GameCharacter(BaseCharacter):
    """
    Personaje concreto para uso en el juego.

    Hereda toda la lógica de BaseCharacter (movimiento en grid,
    pathfinding, salud, shape) y sirve como punto de extensión
    para añadir comportamiento específico del juego.
    """

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        name: Optional[str] = None,
        world=None,
        grid_pos: GridPos = (0, 0),
        move_speed: float = 4.0,
        shape: Optional[CharacterShape] = None,
        tile_w: int = 16,
        tile_h: int = 16,
    ) -> None:
        super().__init__(
            x=x,
            y=y,
            name=name,
            world=world,
            grid_pos=grid_pos,
            move_speed=move_speed,
            shape=shape,
            tile_w=tile_w,
            tile_h=tile_h,
        )

