"""
MapCell class for representing individual tilemap cells.
"""

from typing import Optional, Tuple


class MapCell:
    """
    Represents a single cell in a tilemap.

    Attributes:
        tileset_id: ID of the tileset (None if empty).
        tile_id: ID of the tile within the tileset (None if empty).
    """

    def __init__(self, tileset_id: Optional[int] = None, tile_id: Optional[int] = None) -> None:
        """
        Initialize a map cell.

        Args:
            tileset_id: ID of the tileset (default: None for empty cell).
            tile_id: ID of the tile within the tileset (default: None for empty cell).
        """
        self.tileset_id = tileset_id
        self.tile_id = tile_id

    @property
    def is_empty(self) -> bool:
        """Check if the cell is empty (no tile)."""
        return self.tileset_id is None or self.tile_id is None

    def clear(self) -> None:
        """Clear the cell (remove tile)."""
        self.tileset_id = None
        self.tile_id = None

    def set(self, tileset_id: int, tile_id: int) -> None:
        """
        Set the tile for this cell.

        Args:
            tileset_id: ID of the tileset.
            tile_id: ID of the tile within the tileset.
        """
        self.tileset_id = tileset_id
        self.tile_id = tile_id

    def get_tile_data(self) -> Optional[Tuple[int, int]]:
        """
        Get the tile data as a tuple.

        Returns:
            Tuple of (tileset_id, tile_id) or None if empty.
        """
        if not self.is_empty:
            return self.tileset_id, self.tile_id
        return None

    def __repr__(self) -> str:
        """String representation of the cell."""
        if self.is_empty:
            return "MapCell(empty)"
        return f"MapCell(tileset_id={self.tileset_id}, tile_id={self.tile_id})"

    def __eq__(self, other) -> bool:
        """Check equality with another MapCell."""
        if not isinstance(other, MapCell):
            return False
        return self.tileset_id == other.tileset_id and self.tile_id == other.tile_id

