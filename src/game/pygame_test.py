#!/usr/bin/env python3
"""
Script básico de prueba de Pygame.

Este script demuestra las funcionalidades básicas de pygame:
- Crear una ventana
- Loop de juego básico
- Manejo de eventos (cerrar ventana, teclas)
- Dibujar formas y colores
- Control de FPS
- Uso de la clase Color de vgNoise
"""

import sys
import pygame

# Importar nuestras clases
from core.color.color import Color
from core.tilemap.tilemap import TileMap
from core.tilemap.tileset import TileSet


# Constantes
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colores usando nuestra clase Color
BLACK = Color(0, 0, 0)
WHITE = Color(255, 255, 255)
RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
YELLOW = Color(255, 255, 0)
CYAN = Color(0, 255, 255)
MAGENTA = Color(255, 0, 255)


class BaseGameApp:
    """Aplicación de prueba básica de Pygame."""

    def __init__(self):
        """Inicializa Pygame y crea la ventana."""
        # Inicializar Pygame
        self.tileset = None
        self.tilemap = None
        pygame.init()

        # Crear ventana
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("TileMap Render Test - vgNoise")

        # Reloj para controlar FPS
        self.clock = pygame.time.Clock()

        # Estado
        self.running = True
        self.frame_count = 0

        # Posición del cuadrado que se mueve
        self.square_x = 100
        self.square_y = 100
        self.square_speed = 5

        # Crear tilemap de prueba con tileset grayscale
        self.setup_tilemap()

        print("✓ Pygame inicializado correctamente")
        print(f"✓ Ventana creada: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    def setup_tilemap(self):
        """Configura el tilemap de prueba con tileset grayscale."""
        # Generar tileset grayscale de 32 colores
        print("Generando tileset grayscale de 32 colores...")
        self.tileset = TileSet.generate_grayscale_tileset(
            nsteps=32,
            tile_width=32,
            tile_height=32,
            columns=8,
            output_path="grayscale_tileset_32.png"
        )
        print(f"✓ Tileset generado: {self.tileset}")

        # Crear tilemap de 20x15 tiles
        self.tilemap = TileMap(
            width=20,
            height=15,
            tile_width=32,
            tile_height=32,
            num_layers=1
        )

        # Registrar tileset en el tilemap
        self.tilemap.register_tileset(0, self.tileset)

        # Llenar el tilemap con un patrón de prueba
        for y in range(self.tilemap.height):
            for x in range(self.tilemap.width):
                # Crear un patrón interesante usando los tiles
                # Patrón de tablero de ajedrez con gradientes
                if (x + y) % 2 == 0:
                    tile_id = (x + y) % 32
                else:
                    tile_id = (31 - ((x + y) % 32))

                self.tilemap.set_tile(x, y, 0, tile_id, layer=0)

        print(f"✓ Tilemap creado: {self.tilemap.width}x{self.tilemap.height} tiles")

    def render_tilemap(self, camera_x: int = 0, camera_y: int = 0):
        """
        Renderiza el tilemap en la pantalla usando sistema de chunks.

        Args:
            camera_x: Offset X de la cámara en píxeles.
            camera_y: Offset Y de la cámara en píxeles.
        """
        if not self.tilemap or not self.tileset:
            return

        # Calcular qué tiles son visibles
        start_tile_x = max(0, camera_x // self.tilemap.tile_width)
        start_tile_y = max(0, camera_y // self.tilemap.tile_height)
        end_tile_x = min(self.tilemap.width, (camera_x + WINDOW_WIDTH) // self.tilemap.tile_width + 1)
        end_tile_y = min(self.tilemap.height, (camera_y + WINDOW_HEIGHT) // self.tilemap.tile_height + 1)

        # Renderizar cada capa
        for layer_idx in range(self.tilemap.num_layers):
            layer = self.tilemap.layers[layer_idx]

            # Obtener chunks en el área visible (optimización)
            chunks_in_view = self.tilemap.get_chunks_in_area(
                start_tile_x, start_tile_y, end_tile_x, end_tile_y, layer_idx
            )

            # Renderizar solo los tiles visibles
            for tile_y in range(start_tile_y, end_tile_y):
                for tile_x in range(start_tile_x, end_tile_x):
                    cell = layer.get_tile(tile_x, tile_y)
                    if cell and not cell.is_empty:
                        tileset_id = cell.tileset_id
                        tile_id = cell.tile_id

                        # Obtener tileset
                        tileset = self.tilemap.tilesets.get(tileset_id)
                        if tileset and tileset.surface:
                            # Obtener surface del tile
                            tile_surface = tileset.get_tile_surface(tile_id)
                            if tile_surface:
                                # Calcular posición en pantalla
                                screen_x = tile_x * self.tilemap.tile_width - camera_x
                                screen_y = tile_y * self.tilemap.tile_height - camera_y

                                # Dibujar tile
                                self.screen.blit(tile_surface, (screen_x, screen_y))

    def handle_events(self):
        """Maneja eventos de teclado y ratón."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                print("✓ Ventana cerrada por el usuario")

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    print("✓ ESC presionado - cerrando")
                elif event.key == pygame.K_SPACE:
                    print("✓ SPACE presionado")

        # Movimiento continuo con teclas
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.square_x -= self.square_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.square_x += self.square_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.square_y -= self.square_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.square_y += self.square_speed

        # Mantener dentro de la pantalla
        self.square_x = max(0, min(self.square_x, WINDOW_WIDTH - 50))
        self.square_y = max(0, min(self.square_y, WINDOW_HEIGHT - 50))

    def update(self):
        """Actualiza la lógica del juego."""
        self.frame_count += 1

    def draw(self):
        """Dibuja toda la info en la pantalla."""
        # Limpiar pantalla con color negro
        self.screen.fill(BLACK.to_rgb())

        # Renderizar tilemap
        self.render_tilemap(camera_x=0, camera_y=0)

        # Dibujar título
        font_large = pygame.font.Font(None, 48)
        title = font_large.render("TileMap Test", True, WHITE.to_rgb())
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 10))

        # Dibujar info
        font_small = pygame.font.Font(None, 20)
        active_chunks = len(self.tilemap.get_active_chunks(layer=0))
        info_texts = [
            f"TileMap: {self.tilemap.width}x{self.tilemap.height} tiles",
            f"TileSet: {self.tileset.columns}x{self.tileset.rows} (32 colors)",
            f"Chunk size: {self.tilemap.chunk_size}x{self.tilemap.chunk_size}",
            f"Active chunks: {active_chunks}",
            f"FPS: {int(self.clock.get_fps())}",
        ]

        y_offset = WINDOW_HEIGHT - 115
        for text in info_texts:
            surface = font_small.render(text, True, CYAN.to_rgb())
            self.screen.blit(surface, (10, y_offset))
            y_offset += 22

        # Actualizar pantalla
        pygame.display.flip()

    def run(self):
        """Loop principal del juego."""
        print("\n" + "=" * 60)
        print("TILEMAP RENDER TEST - LOOP INICIADO")
        print("=" * 60)
        print("Controles:")
        print("  - ESC o X: Cerrar ventana")
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

        # Cerrar Pygame
        pygame.quit()
        print("\n✓ Pygame cerrado correctamente")

        # Limpiar archivo de tileset temporal
        self._cleanup()

    def _cleanup(self):
        """Limpia archivos temporales."""
        import os
        from pathlib import Path

        if hasattr(self, 'tileset') and self.tileset.image_path:
            tileset_path = Path(self.tileset.image_path)
            if tileset_path.exists():
                try:
                    os.remove(tileset_path)
                    print(f"✓ Archivo temporal eliminado: {tileset_path.name}")
                except:
                    pass

    def __del__(self):
        """Asegura que Pygame se cierre correctamente."""
        try:
            pygame.quit()
        except:
            pass


def main():
    """Función principal."""
    print("=" * 60)
    print("PYGAME TEST - vgNoise Project")
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

