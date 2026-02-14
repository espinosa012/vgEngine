"""
TileSet class for managing tile collections for tilemaps.
"""

from typing import Optional, Tuple
from pathlib import Path

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class TileSet:
    """
    Simple tileset class for managing tile collections.

    Attributes:
        tile_width: Width of each tile in pixels.
        tile_height: Height of each tile in pixels.
        columns: Number of columns in the tileset.
        rows: Number of rows in the tileset.
        image_path: Path to the tileset image file.
    """

    def __init__(self, tile_width: int = 32, tile_height: int = 32) -> None:
        """
        Initialize a tileset.

        Args:
            tile_width: Width of each tile in pixels (default: 32).
            tile_height: Height of each tile in pixels (default: 32).
        """
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.columns = 0
        self.rows = 0
        self.image_path: Optional[str] = None

    def set_grid_size(self, columns: int, rows: int) -> None:
        """
        Set the grid size of the tileset.

        Args:
            columns: Number of columns.
            rows: Number of rows.
        """
        self.columns = columns
        self.rows = rows

    def load_from_image(self, image_path: str) -> None:
        """
        Load tileset from a PNG image file and calculate grid automatically.

        Args:
            image_path: Path to the PNG image file.

        Raises:
            ImportError: If PIL/Pillow is not installed.
            FileNotFoundError: If the image file does not exist.
            ValueError: If the image dimensions are not divisible by tile size.
        """
        if not HAS_PIL:
            raise ImportError("PIL/Pillow is required to load images. Install with: pip install Pillow")

        # Resolve and validate path
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Load image and get dimensions
        with Image.open(path) as img:
            image_width, image_height = img.size

        # Calculate grid size
        if image_width % self.tile_width != 0:
            raise ValueError(
                f"Image width ({image_width}) is not divisible by tile_width ({self.tile_width})"
            )
        if image_height % self.tile_height != 0:
            raise ValueError(
                f"Image height ({image_height}) is not divisible by tile_height ({self.tile_height})"
            )

        self.columns = image_width // self.tile_width
        self.rows = image_height // self.tile_height
        self.image_path = str(path.resolve())

    def get_tile_rect(self, tile_id: int) -> Optional[Tuple[int, int, int, int]]:
        """
        Get the rectangle (x, y, width, height) for a tile in the tileset image.

        Args:
            tile_id: The tile ID.

        Returns:
            Tuple of (x, y, width, height) or None if tile_id is invalid.
        """
        if self.columns == 0 or tile_id < 0:
            return None

        col = tile_id % self.columns
        row = tile_id // self.columns

        x = col * self.tile_width
        y = row * self.tile_height

        return x, y, self.tile_width, self.tile_height

    def __repr__(self) -> str:
        """String representation of the tileset."""
        return f"TileSet(tile_size={self.tile_width}x{self.tile_height}, grid={self.columns}x{self.rows})"

