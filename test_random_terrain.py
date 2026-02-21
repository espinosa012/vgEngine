#!/usr/bin/env python3
"""
Quick test for the Random Terrain Scene.

This script directly runs the random terrain scene without going through the menu.
"""

import sys
import pygame

# Add src to path
sys.path.insert(0, '/Users/espinosa025/Documents/virigir/vgEngine')

from src.game.test_scenes.random_terrain_scene import RandomTerrainScene


def main():
    """Run the random terrain scene test."""
    # Initialize pygame
    pygame.init()

    # Create window
    screen_width = 1024
    screen_height = 768
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Random Terrain Scene Test - vgEngine")

    # Clock for framerate
    clock = pygame.time.Clock()

    # Create and enter scene
    scene = RandomTerrainScene()
    scene.on_enter()

    # Main game loop
    while scene.running:
        # Calculate delta time
        dt = clock.tick(60) / 1000.0

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                scene.running = False
            scene.handle_event(event)

        # Update
        scene.update(dt)

        # Draw
        scene.draw(screen)

        # Show FPS
        fps = int(clock.get_fps())
        font = pygame.font.Font(None, 20)
        fps_text = font.render(f"FPS: {fps}", True, (100, 255, 100))
        screen.blit(fps_text, (screen_width - 80, 10))

        # Update display
        pygame.display.flip()

    # Exit
    scene.on_exit()
    pygame.quit()
    print("\nTest completed!")


if __name__ == '__main__':
    main()

