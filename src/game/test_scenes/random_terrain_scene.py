"""
Random Terrain Tilemap Scene - Test scene showing a large tilemap with random terrain tiles.

This scene demonstrates:
- Generation of terrain tileset with 6 terrain types
- Large tilemap (256x256) with random terrain tiles
- Camera controls for navigation
- Tile ID display on hover
"""

import pygame
import random
from typing import Optional

from src.core.tilemap.tilemap import TileMap
from src.core.tilemap.tileset import TileSet
from src.core.camera.camera import Camera
from .base_scene import BaseScene


class RandomTerrainScene(BaseScene):
    """Test scene with a large random terrain tilemap."""

    def __init__(self):
        """Initialize the random terrain scene."""
        super().__init__(
            name="Random Terrain Scene",
            description="256x256 tilemap with random terrain tiles"
        )

        self.running = True  # Control de loop principal
        self.tilemap: Optional[TileMap] = None
        self.tileset: Optional[TileSet] = None
        self.camera: Optional[Camera] = None

        # Map dimensions
        self.map_width = 256
        self.map_height = 256
        self.tile_size = 32

        # Camera movement
        self.camera_speed = 500  # pixels per second

        # Mouse interaction
        self.show_hover_info = True
        self.hovered_tile: Optional[tuple] = None

        # Terrain type names
        self.terrain_names = {
            0: "Sand",
            1: "Dirt",
            2: "Grass",
            3: "Mountain",
            4: "Snow",
            5: "Water",
        }

    def on_enter(self):
        """Called when entering the scene."""
        print("Entering Random Terrain Scene")
        print(f"Generating {self.map_width}x{self.map_height} tilemap...")

        # Generate terrain tileset
        self.tileset = TileSet.generate_terrain_tileset(
            tile_size=(self.tile_size, self.tile_size),
            columns=6,
            output_path="terrain_tileset_temp.png"
        )
        print(f"Terrain tileset generated: {self.tileset}")

        # Create tilemap
        self.tilemap = TileMap(
            width=self.map_width,
            height=self.map_height,
            tile_size=(self.tile_size, self.tile_size)
        )
        self.tilemap.tileset = self.tileset

        # Fill with random terrain tiles
        # Distribution: water (5%), sand (15%), dirt (15%), grass (40%), mountain (15%), snow (10%)
        terrain_weights = [15, 15, 40, 15, 10, 5]  # Corresponds to terrain IDs 0-5
        terrain_pool = []
        for terrain_id, weight in enumerate(terrain_weights):
            terrain_pool.extend([terrain_id] * weight)

        for y in range(self.map_height):
            for x in range(self.map_width):
                tile_id = random.choice(terrain_pool)
                self.tilemap.set_tile(x, y, tile_id)

        print(f"Tilemap filled with random terrain tiles")

        # Initialize camera
        screen = pygame.display.get_surface()
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        # Camera position will be in world coordinates
        # Start at center of the map
        center_x = (self.map_width * self.tile_size) // 2 - screen_width // 2
        center_y = (self.map_height * self.tile_size) // 2 - screen_height // 2

        self.camera = Camera(
            x=center_x,
            y=center_y,
            width=screen_width,
            height=screen_height,
            zoom=1.0
        )

        # Set bounds for camera (can't go outside the map)
        self.camera.set_bounds(
            min_x=0,
            max_x=self.map_width * self.tile_size - screen_width,
            min_y=0,
            max_y=self.map_height * self.tile_size - screen_height
        )

        print("Camera initialized and centered")
        print("\nControls:")
        print("  Arrow keys or WASD - Move camera")
        print("  Mouse hover - Show tile information")
        print("  ESC - Exit")

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False

        elif event.type == pygame.MOUSEMOTION:
            # Update hovered tile
            if self.camera and self.tilemap:
                # Convert screen coords to world coords
                world_x, world_y = self.camera.screen_to_world(event.pos[0], event.pos[1])

                # Convert world coords to tile coords
                tile_x = int(world_x // self.tile_size)
                tile_y = int(world_y // self.tile_size)

                # Check if within bounds
                if 0 <= tile_x < self.map_width and 0 <= tile_y < self.map_height:
                    self.hovered_tile = (tile_x, tile_y)
                else:
                    self.hovered_tile = None

    def update(self, dt: float) -> None:
        """Update scene state."""
        if not self.camera:
            return

        # Camera movement with arrow keys or WASD
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.camera_speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.camera_speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.camera_speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.camera_speed * dt

        # Move camera
        if dx != 0 or dy != 0:
            self.camera.move(dx, dy)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the scene."""
        # Clear screen
        screen.fill((20, 20, 30))

        if not self.tilemap or not self.camera or not self.tilemap.tileset:
            return

        # Calculate visible area in tiles
        start_x = max(0, int(self.camera.x // self.tile_size))
        start_y = max(0, int(self.camera.y // self.tile_size))
        end_x = min(self.map_width, int((self.camera.x + self.camera.width) // self.tile_size) + 1)
        end_y = min(self.map_height, int((self.camera.y + self.camera.height) // self.tile_size) + 1)

        # Render visible tiles
        tileset = self.tilemap.tileset
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                # Get MapCell
                cell = self.tilemap.get_tile(x, y)
                if cell and not cell.is_empty:
                    # Get tile from tileset using tile_id
                    tile_surface = tileset.get_tile_surface(cell.tile_id)
                    if tile_surface:
                        # Calculate screen position
                        screen_x = x * self.tile_size - int(self.camera.x)
                        screen_y = y * self.tile_size - int(self.camera.y)
                        screen.blit(tile_surface, (screen_x, screen_y))

        # Draw UI overlay
        self._draw_ui(screen)

    def _draw_ui(self, screen: pygame.Surface) -> None:
        """Draw UI elements."""
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 20)

        # Camera position
        cam_text = f"Camera: ({int(self.camera.x)}, {int(self.camera.y)})"
        cam_surf = small_font.render(cam_text, True, (200, 200, 200))
        screen.blit(cam_surf, (10, 10))

        # Map info
        map_text = f"Map: {self.map_width}x{self.map_height} tiles"
        map_surf = small_font.render(map_text, True, (200, 200, 200))
        screen.blit(map_surf, (10, 35))

        # Hovered tile info
        if self.hovered_tile and self.show_hover_info:
            tile_x, tile_y = self.hovered_tile
            cell = self.tilemap.get_tile(tile_x, tile_y)

            if cell and not cell.is_empty:
                tile_id = cell.tile_id
                terrain_name = self.terrain_names.get(tile_id, "Unknown")

                # Draw info box at mouse position
                mouse_pos = pygame.mouse.get_pos()
                info_text = f"Tile: ({tile_x}, {tile_y}) | ID: {tile_id} | {terrain_name}"
                info_surf = font.render(info_text, True, (255, 255, 255))

                # Draw background
                padding = 8
                info_rect = info_surf.get_rect()
                info_rect.topleft = (mouse_pos[0] + 20, mouse_pos[1] - 10)

                bg_rect = info_rect.inflate(padding * 2, padding * 2)
                pygame.draw.rect(screen, (40, 40, 50, 200), bg_rect)
                pygame.draw.rect(screen, (100, 100, 120), bg_rect, 2)

                # Draw text
                screen.blit(info_surf, info_rect)

        # Controls hint
        hint_text = "Arrow keys/WASD: Move | ESC: Exit"
        hint_surf = small_font.render(hint_text, True, (150, 150, 150))
        hint_rect = hint_surf.get_rect()
        hint_rect.bottomleft = (10, screen.get_height() - 10)
        screen.blit(hint_surf, hint_rect)

    def on_exit(self):
        """Called when exiting the scene."""
        print("Exiting Random Terrain Scene")

        # Cleanup
        self.tilemap = None
        self.tileset = None
        self.camera = None

