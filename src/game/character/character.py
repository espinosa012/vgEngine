from typing import Optional, Tuple, Union

from core.character.base import BaseCharacter
from core.character.controller import CharacterController, PlayerController
from core.character.shape import CharacterShape
from core.item.inventory import Inventory

GridPos = Tuple[int, int]


class GameCharacter(BaseCharacter):
    """
    Personaje concreto para uso en el juego.

    Hereda toda la lógica de BaseCharacter (movimiento en grid,
    pathfinding, salud, shape) y sirve como punto de extensión
    para añadir comportamiento específico del juego.

    Por defecto se crea con un ``CharacterController`` asignado.
    Para convertirlo en el personaje del jugador basta con:

        character.set_player_controller()

    o pasar ``is_player=True`` al constructor.
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
        is_player: bool = False,
        inventory: Optional[Inventory] = None,
        interact_range: float = 64.0,
        grid_mode: bool = False,
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

        if is_player:
            self.controller: Union[CharacterController, PlayerController] = PlayerController(
                character=self,
                inventory=inventory,
                interact_range=interact_range,
                grid_mode=grid_mode,
            )
        else:
            self.controller = CharacterController(
                character=self,
                inventory=inventory,
                interact_range=interact_range,
                grid_mode=grid_mode,
            )

    # ------------------------------------------------------------------
    # Helpers para cambiar el tipo de controller en caliente
    # ------------------------------------------------------------------

    def set_player_controller(
        self,
        interact_range: Optional[float] = None,
        grid_mode: Optional[bool] = None,
    ) -> PlayerController:
        """
        Sustituye el controller actual por un ``PlayerController``.

        Conserva el inventario y los slots de equipo existentes.

        Returns
        -------
        PlayerController
            El nuevo controller asignado.
        """
        prev = self.controller
        self.controller = PlayerController(
            character=self,
            inventory=prev.inventory if prev else None,
            interact_range=interact_range if interact_range is not None
                           else (prev.interact_range if prev else 64.0),
            grid_mode=grid_mode if grid_mode is not None
                      else (prev.grid_mode if prev else False),
        )
        return self.controller

    def set_ai_controller(
        self,
        interact_range: Optional[float] = None,
        grid_mode: Optional[bool] = None,
    ) -> CharacterController:
        """
        Sustituye el controller actual por un ``CharacterController`` base
        (para uso por IA o scripts).

        Conserva el inventario y los slots de equipo existentes.

        Returns
        -------
        CharacterController
            El nuevo controller asignado.
        """
        prev = self.controller
        self.controller = CharacterController(
            character=self,
            inventory=prev.inventory if prev else None,
            interact_range=interact_range if interact_range is not None
                           else (prev.interact_range if prev else 64.0),
            grid_mode=grid_mode if grid_mode is not None
                      else (prev.grid_mode if prev else False),
        )
        return self.controller

