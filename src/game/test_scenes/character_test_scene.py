"""
Character Test Scene - Test scene for BaseCharacter functionality.

This scene demonstrates:
- Creating and controlling a BaseCharacter
- Basic movement with keyboard input
- Character state visualization
"""

import pygame
from typing import Optional

from .base_scene import BaseScene
from src.game.character import BaseCharacter


class CharacterTestScene(BaseScene):
    """Test scene demonstrating BaseCharacter usage."""

    # Character visual settings
    CHARACTER_SIZE = 40
    CHARACTER_COLOR = (66, 135, 245)  # Blue
    CHARACTER_MOVING_COLOR = (100, 200, 100)  # Green when moving

    # UI Colors
    BACKGROUND_COLOR = (30, 30, 40)
    TEXT_COLOR = (220, 220, 220)
    HEALTH_BAR_BG = (60, 60, 60)
    HEALTH_BAR_FG = (220, 60, 60)

    def __init__(self):
        """Initialize the character test scene."""
        super().__init__(
            name="Character Test Scene",
            description="Test scene for BaseCharacter movement and state"
        )

        self.running = True
        self.character: Optional[BaseCharacter] = None
        self.screen_width = 0
        self.screen_height = 0

        # Movement keys state
        self.move_up = False
        self.move_down = False
        self.move_left = False
        self.move_right = False

    def setup(self, screen_width: int, screen_height: int) -> None:
        """
        Setup the scene.

        Args:
            screen_width: Screen width in pixels.
            screen_height: Screen height in pixels.
        """
        super().setup(screen_width, screen_height)

        self.screen_width = screen_width
        self.screen_height = screen_height

        # Create character at center of screen
        self.character = BaseCharacter(
            x=screen_width // 2 - self.CHARACTER_SIZE // 2,
            y=screen_height // 2 - self.CHARACTER_SIZE // 2,
            name="TestCharacter"
        )
        self.character.speed = 200.0

        print(f"✓ Character '{self.character.name}' created at ({self.character.x}, {self.character.y})")

    def cleanup(self) -> None:
        """Cleanup scene resources."""
        super().cleanup()
        self.character = None

    def handle_events(self, events: list) -> None:
        """
        Handle pygame events.

        Args:
            events: List of pygame events.
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                self._handle_key_down(event.key)
            elif event.type == pygame.KEYUP:
                self._handle_key_up(event.key)

    def _handle_key_down(self, key: int) -> None:
        """Handle key press events."""
        if key == pygame.K_UP or key == pygame.K_w:
            self.move_up = True
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.move_down = True
        elif key == pygame.K_LEFT or key == pygame.K_a:
            self.move_left = True
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            self.move_right = True
        elif key == pygame.K_SPACE:
            # Test damage
            if self.character:
                self.character.take_damage(10)
                print(f"Character took damage! Health: {self.character.health}/{self.character.max_health}")
        elif key == pygame.K_h:
            # Test heal
            if self.character:
                self.character.heal(10)
                print(f"Character healed! Health: {self.character.health}/{self.character.max_health}")
        elif key == pygame.K_r:
            # Reset character
            if self.character:
                self.character.health = self.character.max_health
                self.character.set_position(
                    self.screen_width // 2 - self.CHARACTER_SIZE // 2,
                    self.screen_height // 2 - self.CHARACTER_SIZE // 2
                )
                print("Character reset!")

    def _handle_key_up(self, key: int) -> None:
        """Handle key release events."""
        if key == pygame.K_UP or key == pygame.K_w:
            self.move_up = False
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.move_down = False
        elif key == pygame.K_LEFT or key == pygame.K_a:
            self.move_left = False
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            self.move_right = False

    def handle_keys(self, keys) -> None:
        """
        Handle continuous key presses.

        Args:
            keys: pygame.key.get_pressed() result.
        """
        pass  # Using event-based input instead

    def update(self, dt: float) -> None:
        """
        Update scene logic.

        Args:
            dt: Delta time in seconds.
        """
        if not self.character:
            return

        # Calculate movement direction
        dx = 0.0
        dy = 0.0

        if self.move_up:
            dy -= 1.0
        if self.move_down:
            dy += 1.0
        if self.move_left:
            dx -= 1.0
        if self.move_right:
            dx += 1.0

        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.7071  # 1/sqrt(2)
            dy *= 0.7071

        # Set velocity based on direction and speed
        self.character.set_velocity(
            dx * self.character.speed,
            dy * self.character.speed
        )

        # Update character
        self.character.update(dt)

        # Keep character within bounds
        self._clamp_character_position()

    def _clamp_character_position(self) -> None:
        """Keep character within screen bounds."""
        if not self.character:
            return

        # Clamp X position
        if self.character.x < 0:
            self.character.x = 0
        elif self.character.x > self.screen_width - self.CHARACTER_SIZE:
            self.character.x = self.screen_width - self.CHARACTER_SIZE

        # Clamp Y position
        if self.character.y < 0:
            self.character.y = 0
        elif self.character.y > self.screen_height - self.CHARACTER_SIZE:
            self.character.y = self.screen_height - self.CHARACTER_SIZE

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the scene.

        Args:
            screen: Pygame surface to draw on.
        """
        # Clear screen
        screen.fill(self.BACKGROUND_COLOR)

        if not self.character:
            return

        # Draw character (colored square)
        color = self.CHARACTER_MOVING_COLOR if self.character.is_moving else self.CHARACTER_COLOR
        char_rect = pygame.Rect(
            int(self.character.x),
            int(self.character.y),
            self.CHARACTER_SIZE,
            self.CHARACTER_SIZE
        )
        pygame.draw.rect(screen, color, char_rect)

        # Draw direction indicator (small triangle)
        self._draw_direction_indicator(screen, char_rect)

        # Draw health bar
        self._draw_health_bar(screen)

        # Draw info text
        self._draw_info(screen)

    def _draw_direction_indicator(self, screen: pygame.Surface, char_rect: pygame.Rect) -> None:
        """Draw a triangle showing facing direction."""
        if not self.character:
            return

        center_x = char_rect.centerx
        center_y = char_rect.centery
        indicator_size = 8

        # Calculate triangle points based on facing direction
        if self.character.facing_direction == "right":
            points = [
                (center_x + indicator_size, center_y),
                (center_x - indicator_size // 2, center_y - indicator_size // 2),
                (center_x - indicator_size // 2, center_y + indicator_size // 2),
            ]
        elif self.character.facing_direction == "left":
            points = [
                (center_x - indicator_size, center_y),
                (center_x + indicator_size // 2, center_y - indicator_size // 2),
                (center_x + indicator_size // 2, center_y + indicator_size // 2),
            ]
        elif self.character.facing_direction == "up":
            points = [
                (center_x, center_y - indicator_size),
                (center_x - indicator_size // 2, center_y + indicator_size // 2),
                (center_x + indicator_size // 2, center_y + indicator_size // 2),
            ]
        else:  # down
            points = [
                (center_x, center_y + indicator_size),
                (center_x - indicator_size // 2, center_y - indicator_size // 2),
                (center_x + indicator_size // 2, center_y - indicator_size // 2),
            ]

        pygame.draw.polygon(screen, (255, 255, 255), points)

    def _draw_health_bar(self, screen: pygame.Surface) -> None:
        """Draw character health bar at top of screen."""
        if not self.character:
            return

        bar_width = 200
        bar_height = 20
        bar_x = 10
        bar_y = 10

        # Background
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, self.HEALTH_BAR_BG, bg_rect)

        # Health fill
        health_width = int(bar_width * self.character.health_percentage)
        if health_width > 0:
            health_rect = pygame.Rect(bar_x, bar_y, health_width, bar_height)
            pygame.draw.rect(screen, self.HEALTH_BAR_FG, health_rect)

        # Border
        pygame.draw.rect(screen, self.TEXT_COLOR, bg_rect, 2)

        # Health text
        font = pygame.font.Font(None, 20)
        health_text = f"{int(self.character.health)}/{int(self.character.max_health)}"
        text_surface = font.render(health_text, True, self.TEXT_COLOR)
        text_rect = text_surface.get_rect(center=bg_rect.center)
        screen.blit(text_surface, text_rect)

    def _draw_info(self, screen: pygame.Surface) -> None:
        """Draw info text."""
        if not self.character:
            return

        font = pygame.font.Font(None, 24)
        info_lines = [
            f"Position: ({int(self.character.x)}, {int(self.character.y)})",
            f"Facing: {self.character.facing_direction}",
            f"Moving: {self.character.is_moving}",
            f"Speed: {self.character.speed}",
            "",
            "Controls:",
            "WASD/Arrows - Move",
            "SPACE - Take damage",
            "H - Heal",
            "R - Reset",
        ]

        y_offset = 50
        for line in info_lines:
            text_surface = font.render(line, True, self.TEXT_COLOR)
            screen.blit(text_surface, (10, y_offset))
            y_offset += 22

    def get_info_text(self) -> list:
        """
        Get info text to display on screen.

        Returns:
            List of strings to display.
        """
        return [
            f"Scene: {self.name}",
            self.description,
            "Use WASD or Arrow keys to move the character"
        ]

