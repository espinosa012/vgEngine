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
        self.terrain_names = {i: f"Gray {i}" for i in range(32)}

    def on_enter(self):
        """Called when entering the scene."""
        print("Entering Random Terrain Scene")
        print(f"Generating {self.map_width}x{self.map_height} tilemap...")

        # Generate grayscale tileset: 32 steps, white (tile 0) to black (tile 31)
        self.tileset = TileSet.generate_grayscale_tileset(
            nsteps=32,
            tile_size=(self.tile_size, self.tile_size),
            columns=32,
            output_path="grayscale_tileset_temp.png",
            white_to_black=True
        )
        print(f"Grayscale tileset generated: {self.tileset}")

        # Create tilemap
        self.tilemap = TileMap(
            width=self.map_width,
            height=self.map_height,
            tile_size=(self.tile_size, self.tile_size)
        )
        self.tilemap.tileset = self.tileset

        # Fill with random grayscale tiles (uniform distribution across 32 values)
        for y in range(self.map_height):
            for x in range(self.map_width):
                tile_id = random.randint(0, 31)
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
            elif event.key == pygame.K_r:
                if self.camera:
                    self.camera.zoom = 1.0

        elif event.type == pygame.MOUSEWHEEL:
            if self.camera:
                scroll = event.y if event.y != 0 else event.x
                if scroll > 0:
                    self.camera.zoom *= 1.1
                elif scroll < 0:
                    self.camera.zoom /= 1.1

        elif event.type == pygame.MOUSEMOTION:
            if self.camera and self.tilemap:
                world_x, world_y = self.camera.screen_to_world(event.pos[0], event.pos[1])
                tile_x = int(world_x // self.tile_size)
                tile_y = int(world_y // self.tile_size)
                if 0 <= tile_x < self.map_width and 0 <= tile_y < self.map_height:
                    self.hovered_tile = (tile_x, tile_y)
                else:
                    self.hovered_tile = None

    def update(self, dt: float) -> None:
        """Update scene state."""
        if not self.camera:
            return

        keys = pygame.key.get_pressed()

        # Continuous zoom with Q/E held down — camera position stays fixed
        zoom_speed = 1.5
        if keys[pygame.K_e]:
            self.camera.zoom *= zoom_speed ** dt
        elif keys[pygame.K_q]:
            self.camera.zoom /= zoom_speed ** dt

        # Update camera bounds to account for current zoom level
        visible_w = self.camera.width / self.camera.zoom
        visible_h = self.camera.height / self.camera.zoom
        world_w = self.map_width * self.tile_size
        world_h = self.map_height * self.tile_size
        self.camera.set_bounds(
            min_x=0,
            max_x=max(0.0, world_w - visible_w),
            min_y=0,
            max_y=max(0.0, world_h - visible_h),
        )

        # Camera movement (speed adjusted by zoom so world-space movement is constant)
        dx = 0
        dy = 0

        speed = self.camera_speed / self.camera.zoom

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += speed * dt

        if dx != 0 or dy != 0:
            self.camera.move(dx, dy)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the scene."""
        screen.fill((20, 20, 30))

        if not self.tilemap or not self.camera:
            return

        self.tilemap.draw(screen, self.camera)

        self._draw_ui(screen)

    def _draw_ui(self, screen: pygame.Surface) -> None:
        """Draw UI elements."""
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 20)

        # Camera position + zoom
        cam_text = f"Camera: ({int(self.camera.x)}, {int(self.camera.y)})  Zoom: {self.camera.zoom:.2f}x"
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
                mouse_pos = pygame.mouse.get_pos()
                info_text = f"Tile: ({tile_x}, {tile_y}) | ID: {tile_id} | {terrain_name}"
                info_surf = font.render(info_text, True, (255, 255, 255))
                padding = 8
                info_rect = info_surf.get_rect()
                info_rect.topleft = (mouse_pos[0] + 20, mouse_pos[1] - 10)
                bg_rect = info_rect.inflate(padding * 2, padding * 2)
                pygame.draw.rect(screen, (40, 40, 50, 200), bg_rect)
                pygame.draw.rect(screen, (100, 100, 120), bg_rect, 2)
                screen.blit(info_surf, info_rect)

        # Controls hint
        hint_text = "WASD/Arrows: Move | Q/E or Scroll: Zoom | R: Reset zoom | ESC: Exit"
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

