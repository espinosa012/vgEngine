"""
TileMapCell class for representing individual tiles in a tilemap.
"""




class Tile:
    """
    Simple tile cell class.

    Attributes:
        tile_id: The tile index/ID for this cell in tileset.
    """

    def __init__(self, tile_id: int = 0) -> None:
        """
        Initialize a tile cell.

        Args:
            tile_id: The tile index/ID (default: 0).
        """
        self.tile_id = tile_id

    def get_tile_id(self) -> int:
        """Get the tile ID."""
        return self.tile_id

    def set_tile_id(self, tile_id: int) -> None:
        """Set the tile ID."""
        self.tile_id = tile_id

    def __repr__(self) -> str:
        """String representation of the tile cell."""
        return f"TileMapCell(tile_id={self.tile_id})"

