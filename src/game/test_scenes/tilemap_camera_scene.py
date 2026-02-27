"""
Tilemap + Camera test scene.
"""

import pygame
from pathlib import Path

from core.color.color import Color
from core.tilemap.tilemap import TileMap
from core.tilemap.tileset import TileSet
from core.camera.camera import Camera
from .base_scene import BaseScene


class TilemapCameraScene(BaseScene):
    """
    Scene that demonstrates tilemap rendering with camera movement and zoom.
    """

    def __init__(self):
        super().__init__(
            name="Tilemap + Camera (Large Chunks)",
            description="Navigate large tilemap - only camera chunk is rendered"
        )
        self.tilemap = None
        self.tileset = None
        self.camera = None
        self.camera_speed = 20  # Faster movement for large map

        # Colors
        self.bg_color = Color(0, 0, 0)
        self.text_color = Color(0, 255, 255)

        # Chunk tracking
        self.current_chunks = set()  # Set of (chunk_x, chunk_y) tuples being rendered

    def setup(self, screen_width: int, screen_height: int) -> None:
        """Setup large tilemap with chunk system and camera."""
        super().setup(screen_width, screen_height)

        print("Generating grayscale tileset (32 colors)...")
        self.tileset = TileSet.generate_grayscale_tileset(
            nsteps=32,
            tile_size=(8, 8),
            columns=8,
            output_path="grayscale_tileset_32.png"
        )
        print(f"✓ Tileset generated: {self.tileset}")

        # Create LARGE tilemap: 2024x2024 tiles with 256x256 chunks
        print("Creating large tilemap (2024x2024 tiles, 256x256 chunk size)...")
        self.tilemap = TileMap(
            width=512,
            height=512,
            tile_size=(8, 8),
            num_layers=1,
            chunk_size=128
        )

        self.tilemap.add_tileset(0, self.tileset)

        print(f"✓ Tilemap created: {self.tilemap.width}x{self.tilemap.height} tiles")
        print(f"✓ Chunk size: {self.tilemap.chunk_size}x{self.tilemap.chunk_size}")
        print(f"✓ Total possible chunks: {(2024//256)**2} ({2024//256}x{2024//256})")

        # Setup camera
        self.camera = Camera(
            x=0, y=0,
            width=screen_width,
            height=screen_height,
            zoom=1.0
        )

        self.camera.set_bounds_from_tilemap(
            self.tilemap.width,
            self.tilemap.height,
            self.tilemap.tile_width,
            self.tilemap.tile_height
        )

        print(f"✓ Camera: {self.camera}")
        print("✓ Chunks will be generated dynamically as you explore!")

        # Initialize the starting chunk
        self._update_visible_chunks()

    def cleanup(self) -> None:
        """Cleanup tileset file."""
        super().cleanup()

        if self.tileset and self.tileset.image_path:
            tileset_path = Path(self.tileset.image_path)
            if tileset_path.exists():
                try:
                    tileset_path.unlink()
                    print(f"✓ Tileset file deleted: {tileset_path.name}")
                except:
                    pass

    def _get_camera_chunk_position(self) -> tuple:
        """
        Get the chunk coordinates where the camera center is located.

        Returns:
            Tuple of (chunk_x, chunk_y) where the camera center is.
        """
        # Camera center in world coordinates
        center_x = self.camera.x + (self.camera.width / 2) / self.camera.zoom
        center_y = self.camera.y + (self.camera.height / 2) / self.camera.zoom

        # Convert to tile coordinates
        tile_x = int(center_x / self.tilemap.tile_width)
        tile_y = int(center_y / self.tilemap.tile_height)

        # Convert to chunk coordinates
        chunk_x = tile_x // self.tilemap.chunk_size
        chunk_y = tile_y // self.tilemap.chunk_size

        return chunk_x, chunk_y

    def _update_visible_chunks(self):
        """
        Update which chunks should be rendered based on camera position.
        Only renders the chunk where the camera center is located.
        """
        chunk_x, chunk_y = self._get_camera_chunk_position()

        # Only render the chunk where the camera is
        new_chunks = set()

        # Check if chunk is within tilemap bounds
        max_chunk_x = (self.tilemap.width - 1) // self.tilemap.chunk_size
        max_chunk_y = (self.tilemap.height - 1) // self.tilemap.chunk_size

        if 0 <= chunk_x <= max_chunk_x and 0 <= chunk_y <= max_chunk_y:
            new_chunks.add((chunk_x, chunk_y))

            # Generate tiles for this chunk if not already generated
            self._ensure_chunk_generated(chunk_x, chunk_y)

        self.current_chunks = new_chunks

    def _ensure_chunk_generated(self, chunk_x: int, chunk_y: int):
        """
        Ensure a chunk has been generated with tile data.
        Generates a pattern for the chunk if it's empty.

        Args:
            chunk_x: Chunk X coordinate.
            chunk_y: Chunk Y coordinate.
        """
        layer = self.tilemap.layers[0]
        chunk = layer.get_chunk(chunk_x, chunk_y)

        # If chunk doesn't exist, it will be created when we set tiles
        # Check if chunk is empty by sampling a tile
        chunk_start_x = chunk_x * self.tilemap.chunk_size
        chunk_start_y = chunk_y * self.tilemap.chunk_size

        sample_cell = layer.get_tile(chunk_start_x, chunk_start_y)

        # If the sample cell is empty, generate the entire chunk
        if sample_cell and sample_cell.is_empty:
            self._generate_chunk_tiles(chunk_x, chunk_y)
        elif not sample_cell:
            self._generate_chunk_tiles(chunk_x, chunk_y)

    def _generate_chunk_tiles(self, chunk_x: int, chunk_y: int):
        """
        Generate tile pattern for a specific chunk.
        Uses GLOBAL coordinates to ensure pattern continuity across chunks.

        Args:
            chunk_x: Chunk X coordinate.
            chunk_y: Chunk Y coordinate.
        """
        chunk_start_x = chunk_x * self.tilemap.chunk_size
        chunk_start_y = chunk_y * self.tilemap.chunk_size

        chunk_end_x = min(chunk_start_x + self.tilemap.chunk_size, self.tilemap.width)
        chunk_end_y = min(chunk_start_y + self.tilemap.chunk_size, self.tilemap.height)

        # Generate pattern for this chunk using GLOBAL tile coordinates
        # This ensures continuity between chunks
        for y in range(chunk_start_y, chunk_end_y):
            for x in range(chunk_start_x, chunk_end_x):
                # Create pattern based on GLOBAL position (x, y)
                # This makes the pattern continuous across all chunks
                if (x + y) % 2 == 0:
                    tile_id = (x + y) % 32
                else:
                    tile_id = (31 - ((x + y) % 32))

                self.tilemap.set_tile(x, y, tile_id, tileset_id=0, layer=0)

    def handle_events(self, events: list) -> None:
        """Handle events."""
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                # Zoom with mouse wheel
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if event.y > 0:  # Scroll up = zoom in
                    self.camera.zoom_at_point(mouse_x, mouse_y, 1.1)
                elif event.y < 0:  # Scroll down = zoom out
                    self.camera.zoom_at_point(mouse_x, mouse_y, 0.9)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Reset camera
                    self.camera.set_position(0, 0)
                    self.camera.zoom = 1.0
                    print("✓ Camera reset")
                elif event.key == pygame.K_SPACE:
                    print(f"✓ Camera: {self.camera}")

    def handle_keys(self, keys) -> None:
        """Handle continuous key presses."""
        # Camera movement with WASD or arrows
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.camera.move(-self.camera_speed, 0)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.camera.move(self.camera_speed, 0)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.camera.move(0, -self.camera_speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.camera.move(0, self.camera_speed)

        # Zoom with + and -
        if keys[pygame.K_PLUS] or keys[pygame.K_EQUALS]:
            self.camera.zoom_in(1.02)
        if keys[pygame.K_MINUS]:
            self.camera.zoom_out(1.02)

    def update(self, dt: float) -> None:
        """Update camera and visible chunks."""
        if self.camera:
            self.camera.update()
            # Update which chunks should be visible based on camera position
            self._update_visible_chunks()

    def draw(self, screen: pygame.Surface) -> None:
        """Draw tilemap rendering only visible chunks."""
        # Clear screen
        screen.fill(self.bg_color.to_rgb())

        if not self.tilemap or not self.tileset or not self.camera:
            return

        # Render all layers using chunk-based drawing
        for layer_idx in range(self.tilemap.num_layers):
            self.tilemap.draw(screen, self.camera, layer=layer_idx)

    def get_info_text(self) -> list:
        """Get info text with chunk information."""
        if not self.tilemap or not self.camera:
            return super().get_info_text()

        active_chunks = len(self.tilemap.get_active_chunks(layer=0))
        visible_chunks = len(self.current_chunks)
        camera_chunk = self._get_camera_chunk_position()

        return [
            f"Scene: {self.name}",
            f"TileMap: {self.tilemap.width}x{self.tilemap.height} tiles",
            f"Chunk size: {self.tilemap.chunk_size}x{self.tilemap.chunk_size}",
            f"Active chunks: {active_chunks} (generated)",
            f"Visible chunks: {visible_chunks} (rendering)",
            f"Camera chunk: ({camera_chunk[0]}, {camera_chunk[1]})",
            f"Camera pos: ({self.camera.x:.0f}, {self.camera.y:.0f})",
            f"Zoom: {self.camera.zoom:.2f}x",
            "",
            "Controls:",
            "WASD/Arrows: Move camera",
            "Mouse wheel: Zoom",
            "+/- : Zoom in/out",
            "R: Reset camera",
            "1-9: Change scene",
            "ESC: Exit",
        ]

