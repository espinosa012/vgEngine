#!/usr/bin/env python3
"""
Script básico de prueba de Pygame con tilemap grande y sistema de chunks.

Este script demuestra:
- Tilemap grande de 2024x2024 tiles
- Sistema de chunks de 256x256 tiles
- Renderizado eficiente basado en chunks visibles
- Cámara con movimiento y zoom
"""

import sys
from pathlib import Path

# Agregar el directorio src al path para imports
src_dir = Path(__file__).parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import pygame

# Importar escena
from test_scenes.random_terrain_scene import RandomTerrainScene


# Constantes
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60


class BaseGameApp:
    """Aplicación de prueba de Pygame con tilemap grande y chunks."""

    def __init__(self):
        """Inicializa Pygame y crea la ventana."""
        # Inicializar Pygame
        pygame.init()

        # Crear ventana
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Random Terrain Map (256x256) - vgEngine")

        # Reloj para controlar FPS
        self.clock = pygame.time.Clock()

        # Estado
        self.running = True
        self.frame_count = 0

        # Crear y configurar la escena
        self.scene = RandomTerrainScene()
        self.scene.on_enter()

        print("✓ Pygame inicializado correctamente")
        print(f"✓ Ventana creada: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        print(f"✓ Escena cargada: RandomTerrainScene")

    def handle_events(self):
        """Maneja eventos de teclado y ratón."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.scene.running = False
                print("✓ Ventana cerrada por el usuario")

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    self.scene.running = False
                    print("✓ ESC presionado - cerrando")

            # Pasar eventos a la escena
            self.scene.handle_event(event)

    def update(self):
        """Actualiza la lógica del juego."""
        self.frame_count += 1

        # Calcular delta time
        dt = self.clock.get_time() / 1000.0

        # Actualizar escena
        self.scene.update(dt)

    def draw(self):
        """Dibuja la escena en la pantalla."""
        # Limpiar pantalla y dibujar escena
        self.scene.draw(self.screen)

        # Dibujar FPS
        font = pygame.font.Font(None, 20)
        fps_text = font.render(f"FPS: {int(self.clock.get_fps())}", True, (100, 255, 100))
        self.screen.blit(fps_text, (WINDOW_WIDTH - 80, 10))

        # Actualizar pantalla
        pygame.display.flip()

    def run(self):
        """Loop principal del juego."""
        print("\n" + "=" * 60)
        print("RANDOM TERRAIN MAP TEST")
        print("=" * 60)
        print("Map size: 256x256 tiles")
        print("Tile size: 32x32 pixels")
        print("Terrain types: Sand, Dirt, Grass, Mountain, Snow, Water")
        print()
        print("Controles:")
        print("  - WASD o Flechas: Mover cámara")
        print("  - Mouse hover: Ver información del tile")
        print("  - ESC: Cerrar ventana")
        print("=" * 60 + "\n")

        while self.running:
            # Manejar eventos
            self.handle_events()

            # Actualizar lógica
            self.update()

            # Dibujar
            self.draw()

            # Controlar FPS
            self.clock.tick(FPS)

        # Cleanup de la escena
        self.scene.on_exit()

        # Cerrar Pygame
        pygame.quit()
        print("\n✓ Pygame cerrado correctamente")

    def __del__(self):
        """Asegura que Pygame se cierre correctamente."""
        try:
            pygame.quit()
        except:
            pass


def main():
    """Función principal."""
    print("=" * 60)
    print("PYGAME TEST - Random Terrain Map - vgEngine")
    print("=" * 60)
    print(f"Pygame version: {pygame.version.ver}")
    print(f"SDL version: {'.'.join(map(str, pygame.get_sdl_version()))}")
    print("=" * 60)
    print()

    try:
        # Crear y ejecutar la aplicación
        app = BaseGameApp()
        app.run()

        print("\n" + "=" * 60)
        print("✓ TEST COMPLETADO EXITOSAMENTE")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

