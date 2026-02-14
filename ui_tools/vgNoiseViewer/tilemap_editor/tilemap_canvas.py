"""
Canvas for displaying and editing tilemaps.
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict
from PIL import Image, ImageTk, ImageDraw
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))
from tilemap import VGTileMap, TileSet
class TilemapCanvas(ttk.Frame):
    """Canvas for displaying and editing a tilemap."""
    def __init__(self, parent, **kwargs):
        """
        Initialize the tilemap canvas.
        Args:
            parent: Parent widget.
        """
        super().__init__(parent, **kwargs)
        self.tilemap: Optional[VGTileMap] = None
        self.tileset_images: Dict[int, Image.Image] = {}  # tileset_id -> Image
        self.tilesets: Dict[int, TileSet] = {}  # tileset_id -> TileSet
        self.current_tile_id: Optional[int] = None
        self.current_tileset_id: Optional[int] = None
        self.rendered_image: Optional[Image.Image] = None
        self._setup_ui()
    def _setup_ui(self):
        """Setup the UI components."""
        # Add scrollbars
        v_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        # Create canvas
        self.canvas = tk.Canvas(
            self,
            bg="#2d2d2d",
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set,
            highlightthickness=0
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.config(command=self.canvas.yview)
        h_scroll.config(command=self.canvas.xview)
        # Bind mouse events
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
    def set_tilemap(self, tilemap: VGTileMap):
        """Set the tilemap to display."""
        self.tilemap = tilemap
        self.render()
    def register_tileset(self, tileset_id: int, tileset: TileSet, image: Image.Image):
        """Register a tileset for rendering."""
        self.tilesets[tileset_id] = tileset
        self.tileset_images[tileset_id] = image
    def set_current_tile(self, tileset_id: int, tile_id: int):
        """Set the current tile for painting."""
        self.current_tileset_id = tileset_id
        self.current_tile_id = tile_id
    def render(self):
        """Render the tilemap to the canvas."""
        if not self.tilemap:
            return
        # Create image
        width = self.tilemap.width * self.tilemap.tile_width
        height = self.tilemap.height * self.tilemap.tile_height
        self.rendered_image = Image.new('RGB', (width, height), color=(45, 45, 45))
        # Render each tile
        for y in range(self.tilemap.height):
            for x in range(self.tilemap.width):
                tile = self.tilemap.get_tile(x, y)
                if tile and tile.tile_id >= 0:
                    self._draw_tile(x, y, tile.tile_id)
        # Draw grid
        self._draw_grid()
        # Update canvas
        self.photo = ImageTk.PhotoImage(self.rendered_image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.config(scrollregion=(0, 0, width, height))
    def _draw_tile(self, map_x: int, map_y: int, tile_id: int):
        """Draw a single tile on the rendered image."""
        if not self.rendered_image:
            return
        # Find tileset that contains this tile_id
        # For now, use the first tileset (simplified)
        if not self.tileset_images:
            return
        tileset_id = list(self.tilesets.keys())[0]
        tileset = self.tilesets[tileset_id]
        tileset_image = self.tileset_images[tileset_id]
        # Get tile rect from tileset
        rect = tileset.get_tile_rect(tile_id)
        if not rect:
            return
        src_x, src_y, src_w, src_h = rect
        # Extract tile from tileset
        tile_img = tileset_image.crop((src_x, src_y, src_x + src_w, src_y + src_h))
        # Resize if needed
        if (src_w != self.tilemap.tile_width or src_h != self.tilemap.tile_height):
            tile_img = tile_img.resize(
                (self.tilemap.tile_width, self.tilemap.tile_height),
                Image.Resampling.NEAREST
            )
        # Paste on rendered image
        dst_x = map_x * self.tilemap.tile_width
        dst_y = map_y * self.tilemap.tile_height
        self.rendered_image.paste(tile_img, (dst_x, dst_y))
    def _draw_grid(self):
        """Draw grid lines on the rendered image."""
        if not self.rendered_image:
            return
        draw = ImageDraw.Draw(self.rendered_image)
        width = self.tilemap.width * self.tilemap.tile_width
        height = self.tilemap.height * self.tilemap.tile_height
        # Vertical lines
        for x in range(self.tilemap.width + 1):
            px = x * self.tilemap.tile_width
            draw.line([(px, 0), (px, height)], fill=(68, 68, 68), width=1)
        # Horizontal lines
        for y in range(self.tilemap.height + 1):
            py = y * self.tilemap.tile_height
            draw.line([(0, py), (width, py)], fill=(68, 68, 68), width=1)
    def _on_click(self, event):
        """Handle mouse click."""
        self._paint_tile(event)
    def _on_drag(self, event):
        """Handle mouse drag."""
        self._paint_tile(event)
    def _paint_tile(self, event):
        """Paint a tile at the mouse position."""
        if not self.tilemap or self.current_tile_id is None:
            return
        # Get canvas coordinates
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        # Convert to tile coordinates
        tile_x = int(x // self.tilemap.tile_width)
        tile_y = int(y // self.tilemap.tile_height)
        # Paint tile
        if 0 <= tile_x < self.tilemap.width and 0 <= tile_y < self.tilemap.height:
            self.tilemap.set_tile(tile_x, tile_y, self.current_tile_id)
            # Re-render just this tile
            self._draw_tile(tile_x, tile_y, self.current_tile_id)
            # Update display
            self.photo = ImageTk.PhotoImage(self.rendered_image)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
