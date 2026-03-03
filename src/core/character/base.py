from typing import Optional, Tuple, TYPE_CHECKING
import pygame

from core.base.game_object import GameObject
from core.character.movement_component import MovementComponent
from core.character.shape import CharacterShape, RectShape
from core.color.color import Colors

if TYPE_CHECKING:
    from core.character.controller import CharacterController

GridPos = Tuple[int, int]


class BaseCharacter(GameObject):
    """
    Base class for all character entities (player, enemies, NPCs).
    Inherits from GameObject and adds character-specific functionality.

    Grid-based movement is handled via a MovementComponent that uses A*
    pathfinding. Subclasses should override _cell_is_walkable() to define
    their own walkability rules; the world reference is passed in so that
    the character can query it without coupling to the tilemap directly.

    Visual representation is handled by a CharacterShape instance that
    draws the character using pygame primitives. Replace self.shape at
    any time to change the character's appearance.
    """

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        name: str = None,
        world=None,
        grid_pos: GridPos = (0, 0),
        move_speed: float = 4.0,
        shape: Optional[CharacterShape] = None,
        tile_w: int = 16,
        tile_h: int = 16,
    ):
        """
        Initialize a character.

        Args:
            x:          Initial pixel x position.
            y:          Initial pixel y position.
            name:       Optional name for the character.
            world:      VGWorld instance used for walkability queries.
            grid_pos:   Initial position in grid (cell) coordinates.
            move_speed: Grid-based movement speed in cells per second.
            shape:      Visual representation built from pygame primitives.
                        Defaults to a 32×32 white RectShape if None.
        """
        super().__init__(x, y, name)

        # Character-specific properties
        self.health: float = 100.0
        self.max_health: float = 100.0
        self.speed: float = 100.0  # pixels per second (free movement)

        # Free movement velocity (legacy / non-grid movement)
        self.velocity_x: float = 0.0
        self.velocity_y: float = 0.0

        # State
        self.facing_direction: str = "right"  # "left", "right", "up", "down"
        self.is_moving: bool = False

        # ------------------------------------------------------------------
        # Grid-based movement
        # ------------------------------------------------------------------
        self.world = world
        self.grid_x: int = grid_pos[0]
        self.grid_y: int = grid_pos[1]
        self.tile_w: int = tile_w
        self.tile_h: int = tile_h

        self._movement: Optional[MovementComponent] = None
        if world is not None:
            self._movement = MovementComponent(
                is_walkable_fn=self._cell_is_walkable,
                move_speed=move_speed,
                tile_w=tile_w,
                tile_h=tile_h,
            )
            self._movement.set_cell(grid_pos)

        # ------------------------------------------------------------------
        # Visual shape
        # ------------------------------------------------------------------
        # Holds the primitive-based visual of this character.
        # Replace or mutate self.shape at any time to change appearance.
        self.shape: CharacterShape = shape if shape is not None else RectShape(
            width=32,
            height=32,
            color=Colors.WHITE,
            border_width=1,
        )

        # ------------------------------------------------------------------
        # Controller (opcional)
        # ------------------------------------------------------------------
        # Asigna un CharacterController (o subclase) para que el personaje
        # se actualice automáticamente en cada frame.
        # Un personaje sin controller sigue funcionando con normalidad;
        # simplemente no tiene comportamiento propio.
        self.controller: Optional["CharacterController"] = None

    # ------------------------------------------------------------------
    # Grid position
    # ------------------------------------------------------------------

    @property
    def grid_position(self) -> GridPos:
        """Current position in grid (cell) coordinates."""
        return self.grid_x, self.grid_y

    @property
    def health_percentage(self) -> float:
        """Get health as a percentage (0.0 to 1.0)."""
        if self.max_health <= 0:
            return 0.0
        return self.health / self.max_health

    def set_velocity(self, vx: float, vy: float) -> None:
        """
        Set the character's velocity directly.

        Args:
            vx: Horizontal velocity in pixels per second.
            vy: Vertical velocity in pixels per second.
        """
        self.velocity_x = vx
        self.velocity_y = vy

    # ------------------------------------------------------------------
    # Walkability — override in subclasses
    # ------------------------------------------------------------------

    def _cell_is_walkable(self, pos: GridPos) -> bool:
        """
        Decide whether the character can walk on the given cell.

        Delegates to world.is_walkable by default. Override in subclasses
        to add character-specific restrictions (e.g. blocking water, lava…).

        Args:
            pos: (x, y) grid position to test.

        Returns:
            True if the cell is passable for this character.
        """
        if self.world is None:
            return True
        return self.world.is_walkable(pos[0], pos[1])

    # ------------------------------------------------------------------
    # Grid-based movement API
    # ------------------------------------------------------------------

    def move_to(self, destination: GridPos) -> bool:
        """
        Request grid-based movement to destination using A* pathfinding.

        Args:
            destination: Target (x, y) grid position.

        Returns:
            True if a valid path was found and movement has started.
        """
        if self._movement is None:
            return False
        return self._movement.request_move_to(self.grid_position, destination)

    def move_to_cell(
        self,
        destination: GridPos,
        is_walkable_fn,
        move_speed: float = 4.0,
    ) -> bool:
        """
        Move to *destination* using a caller-supplied walkability function.

        Creates a temporary MovementComponent if none exists (i.e. no world
        was provided at construction time), using the scene's obstacle set
        directly.

        Args:
            destination:    Target (tile_x, tile_y) grid position.
            is_walkable_fn: Callable[(tile_x, tile_y)] → bool.
            move_speed:     Cells per second (default 4).

        Returns:
            True if a path was found and movement started.
        """
        if self._movement is None:
            self._movement = MovementComponent(
                is_walkable_fn=is_walkable_fn,
                move_speed=move_speed,
                tile_w=self.tile_w,
                tile_h=self.tile_h,
            )
            self._movement.set_cell(self.grid_position)
        else:
            # Update the walkability function and speed in-place
            self._movement._is_walkable = is_walkable_fn
            self._movement.move_speed = move_speed

        return self._movement.request_move_to(self.grid_position, destination)

    def get_path_to(self, destination: GridPos) -> list:
        """Return the remaining planned path (including current target cell)."""
        if self._movement is None:
            return []
        return self._movement.remaining_path

    def stop_grid_movement(self) -> None:
        """Interrupt grid-based movement immediately."""
        if self._movement is not None:
            self._movement.stop()

    def on_move(self, new_pos: GridPos) -> None:
        """
        Hook called after each grid step.

        Override in subclasses to trigger animations, sounds, etc.

        Args:
            new_pos: The new (x, y) grid position after the step.
        """
        pass

    def _on_step(self, new_pos: GridPos) -> None:
        """Internal callback wired to MovementComponent.update()."""
        self.grid_x, self.grid_y = new_pos
        self.on_move(new_pos)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, delta_time: float):
        """
        Update character state.

        Args:
            delta_time: Time elapsed since last frame in seconds.
        """
        # Free (pixel-space) movement
        if self.velocity_x != 0 or self.velocity_y != 0:
            self.translate(self.velocity_x * delta_time, self.velocity_y * delta_time)
            self.is_moving = True
        else:
            self.is_moving = False

        # Grid-based movement
        if self._movement is not None:
            self._movement.update(delta_time, on_step=self._on_step)
            if self._movement.is_moving:
                self.is_moving = True
            # Sync world position from smooth interpolation
            # Offset so the character is bottom-centred on its cell
            self.x = (self._movement.pixel_x
                      + (self.tile_w - self.shape.width) / 2)
            self.y = (self._movement.pixel_y
                      + self.tile_h - self.shape.height - 2)

        # Controller tick (IA, lógica de jugador, etc.)
        if self.controller is not None:
            self.controller.tick(delta_time)

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self, surface: "pygame.Surface") -> None:
        """
        Draw the character on a pygame surface.

        Delegates to self.shape.draw(), which renders the character using
        pygame primitives. Override in subclasses for additional elements
        (health bars, name tags, debug info…).

        Args:
            surface: The pygame.Surface to draw onto.
        """
        self.shape.draw(surface, self.x, self.y)

    def render_to_tilemap(
        self,
        surface: "pygame.Surface",
        tile_x: int,
        tile_y: int,
        tile_w: int,
        tile_h: int,
        floor_gap: int = 2,
    ) -> None:
        """
        Draw the character centred at the bottom of a tilemap cell.

        The character is horizontally centred inside the cell and sits just
        above the cell's bottom edge, leaving *floor_gap* pixels of space
        between the character's feet and the tile floor.

        Args:
            surface:    Target pygame.Surface (the tilemap viewport surface).
            tile_x:     Column index of the target cell in tile units.
            tile_y:     Row index of the target cell in tile units.
            tile_w:     Width of a single tile in pixels.
            tile_h:     Height of a single tile in pixels.
            floor_gap:  Pixels of separation between the character bottom and
                        the cell floor (default: 2).
        """
        # Top-left pixel of the target cell
        cell_px = tile_x * tile_w
        cell_py = tile_y * tile_h

        # Horizontal centre; vertical aligned to the bottom with the gap
        draw_x = cell_px + (tile_w - self.shape.width) // 2
        draw_y = cell_py + tile_h - self.shape.height - floor_gap

        self.shape.draw(surface, draw_x, draw_y)

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def take_damage(self, amount: float):
        """
        Apply damage to the character.

        Args:
            amount: Damage amount.
        """
        self.health = max(0.0, self.health - amount)
        if self.health <= 0:
            self.on_death()

    def heal(self, amount: float):
        """
        Heal the character.

        Args:
            amount: Heal amount.
        """
        self.health = min(self.max_health, self.health + amount)

    # ------------------------------------------------------------------
    # Free movement
    # ------------------------------------------------------------------

    def move(self, direction_x: float, direction_y: float):
        """
        Set movement velocity based on direction.

        Args:
            direction_x: Horizontal direction (-1 to 1).
            direction_y: Vertical direction (-1 to 1).
        """
        self.velocity_x = direction_x * self.speed
        self.velocity_y = direction_y * self.speed

        if direction_x > 0:
            self.facing_direction = "right"
        elif direction_x < 0:
            self.facing_direction = "left"
        elif direction_y > 0:
            self.facing_direction = "down"
        elif direction_y < 0:
            self.facing_direction = "up"

    def stop(self):
        """Stop free movement."""
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.is_moving = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_death(self):
        """
        Called when character health reaches 0.
        Override for custom death behavior.
        """
        self.destroy()

    @property
    def is_alive(self) -> bool:
        """Check if character is alive."""
        return self.health > 0 and not self.destroyed

