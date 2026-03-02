"""
MovementComponent: handles grid-based movement and pathfinding for characters.
"""

from typing import Callable, List, Optional, Tuple

from virigir_math_utilities.pathfinding import astar_grid_2d, Manhattan, PathResult

GridPos = Tuple[int, int]


class MovementComponent:
    """
    Handles grid-based movement for a character using A* pathfinding.

    Smooth interpolation
    --------------------
    Between on_step() callbacks the component exposes a sub-cell pixel
    position via ``pixel_x`` / ``pixel_y``.  The caller is responsible for
    supplying the tile size so the component can convert grid → pixel coords.

    Attributes:
        move_speed: Steps (cells) per second.
        tile_w, tile_h: Pixel size of one cell (needed for smooth position).
    """

    def __init__(
        self,
        is_walkable_fn: Callable[[GridPos], bool],
        move_speed: float = 4.0,
        tile_w: int = 16,
        tile_h: int = 16,
    ) -> None:
        self._is_walkable = is_walkable_fn
        self.move_speed = move_speed
        self.tile_w = tile_w
        self.tile_h = tile_h

        self._path: List[GridPos] = []
        self._is_moving: bool = False

        # Smooth interpolation state
        self._from_cell: Optional[GridPos] = None   # cell we are leaving
        self._to_cell:   Optional[GridPos] = None   # cell we are heading to
        self._t: float = 0.0                         # 0..1 progress between cells

        # Pixel position (updated every frame)
        self.pixel_x: float = 0.0
        self.pixel_y: float = 0.0

    # ------------------------------------------------------------------
    # Pathfinding
    # ------------------------------------------------------------------

    def request_move_to(self, origin: GridPos, destination: GridPos) -> bool:
        """
        Calculate an A* path from origin to destination and begin movement.

        Returns True if a valid path was found and movement has started.
        """
        result: PathResult = astar_grid_2d(
            start=origin,
            goal=destination,
            is_walkable_fn=self._is_walkable,
            heuristic=Manhattan(),
        )

        if not result.found:
            return False

        # Drop the origin cell — character is already there.
        self._path = list(result.path[1:])
        if self._path:
            self._from_cell = origin
            self._to_cell   = self._path.pop(0)   # pop so the loop doesn't double-count it
            self._t = 0.0
            self._is_moving = True
            self._update_pixel()
        return self._is_moving

    # ------------------------------------------------------------------
    # Update  (call every frame)
    # ------------------------------------------------------------------

    def update(
        self,
        delta_time: float,
        on_step: Callable[[GridPos], None],
    ) -> None:
        """
        Advance smooth movement along the cached path.

        ``on_step`` is called with the new grid position each time the
        character completes a full cell transition.
        """
        if not self._is_moving or self._to_cell is None:
            return

        self._t += delta_time * self.move_speed   # move_speed cells/sec

        # Process all completed cell transitions, including the final one
        while self._t >= 1.0:
            self._t -= 1.0
            arrived = self._to_cell
            self._from_cell = arrived
            on_step(arrived)              # notify caller (updates grid_x/y)

            if self._path:
                # Advance to next cell
                self._to_cell = self._path.pop(0)
            else:
                # Reached the end — snap to destination
                self._to_cell = None
                self._t = 0.0
                self._is_moving = False
                self._update_pixel()
                return

        self._update_pixel()

    def _update_pixel(self) -> None:
        """Recompute pixel_x/pixel_y from the current interpolation state."""
        if self._from_cell is None:
            return
        fx = self._from_cell[0] * self.tile_w
        fy = self._from_cell[1] * self.tile_h
        if self._to_cell is not None and self._is_moving:
            tx = self._to_cell[0] * self.tile_w
            ty = self._to_cell[1] * self.tile_h
            self.pixel_x = fx + (tx - fx) * min(self._t, 1.0)
            self.pixel_y = fy + (ty - fy) * min(self._t, 1.0)
        else:
            self.pixel_x = float(fx)
            self.pixel_y = float(fy)

    # ------------------------------------------------------------------
    # Initialise pixel position from a known cell (call once at spawn)
    # ------------------------------------------------------------------

    def set_cell(self, cell: GridPos) -> None:
        """Teleport (no animation) to *cell* and update pixel position."""
        self._from_cell = cell
        self._to_cell   = None
        self._t = 0.0
        self._is_moving = False
        self._path.clear()
        self._update_pixel()

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    @property
    def is_moving(self) -> bool:
        return self._is_moving

    @property
    def remaining_path(self) -> List[GridPos]:
        """Full pending path including the current target cell."""
        result = []
        if self._to_cell is not None:
            result.append(self._to_cell)
        result.extend(self._path)
        return result

    def stop(self) -> None:
        """Interrupt movement immediately, discarding the current path."""
        self._path.clear()
        self._is_moving = False
        self._t = 0.0
        if self._from_cell:
            self._to_cell = None
            self._update_pixel()
