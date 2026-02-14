"""
VGTileMap class for managing tilemaps.
"""

from typing import Tuple


class VGTileMap:
    """
    Simple tilemap class for managing tile grids.

    Attributes:
        width: Width of the tilemap in tiles.
        height: Height of the tilemap in tiles.
        tile_width: Width of each tile in pixels.
        tile_height: Height of each tile in pixels.
        data: 2D list of tile IDs (integers).
    """

    def __init__(
        self,
        width: int,
        height: int,
        tile_width: int = 32,
        tile_height: int = 32
    ) -> None:
        """
        Initialize the tilemap.

        Args:
            width: Width of the tilemap in tiles.
            height: Height of the tilemap in tiles.
            tile_width: Width of each tile in pixels (default: 32).
            tile_height: Height of each tile in pixels (default: 32).
        """
        self.width = width
        self.height = height
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.data = [[0 for _ in range(width)] for _ in range(height)]

    def get_tile_id(self, x: int, y: int) -> int:
        """
        Get the tile ID at the specified position.

        Args:
            x: X coordinate in tile units.
            y: Y coordinate in tile units.

        Returns:
            The tile ID at the position, or -1 if out of bounds.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.data[y][x]
        return -1

    def set_tile(self, x: int, y: int, tile_id: int) -> None:
        """
        Set the tile ID at the specified position.

        Args:
            x: X coordinate in tile units.
            y: Y coordinate in tile units.
            tile_id: The tile ID to set.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.data[y][x] = tile_id

    def get_size(self) -> Tuple[int, int]:
        """
        Get the size of the tilemap in tiles.

        Returns:
            Tuple of (width, height) in tiles.
        """
        return self.width, self.height

    def get_pixel_size(self) -> Tuple[int, int]:
        """
        Get the size of the tilemap in pixels.

        Returns:
            Tuple of (width, height) in pixels.
        """
        return self.width * self.tile_width, self.height * self.tile_height

    def __repr__(self) -> str:
        """String representation of the tilemap."""
        return (f"VGTileMap(width={self.width}, height={self.height}, "
                f"tile_size=({self.tile_width}x{self.tile_height}))")

