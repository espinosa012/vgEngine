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

# Importar nuestra clase Color
from core.color.color import Color


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
        pygame.init()

        # Crear ventana
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pygame Test - vgNoise")

        # Reloj para controlar FPS
        self.clock = pygame.time.Clock()

        # Estado
        self.running = True
        self.frame_count = 0

        # Posición del cuadrado que se mueve
        self.square_x = 100
        self.square_y = 100
        self.square_speed = 5

        print("✓ Pygame inicializado correctamente")
        print(f"✓ Ventana creada: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")

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
        """Dibuja todo en la pantalla."""
        # Limpiar pantalla con color negro
        self.screen.fill(BLACK.to_rgb())

        # Dibujar título
        font_large = pygame.font.Font(None, 48)
        title = font_large.render("Pygame Test", True, WHITE.to_rgb())
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 30))

        # Dibujar instrucciones
        font_small = pygame.font.Font(None, 24)
        instructions = [
            "Controles:",
            "- Flechas o WASD: Mover cuadrado rojo",
            "- SPACE: Mensaje en consola",
            "- ESC: Salir",
        ]

        y_offset = 100
        for text in instructions:
            surface = font_small.render(text, True, CYAN.to_rgb())
            self.screen.blit(surface, (50, y_offset))
            y_offset += 30

        # Dibujar FPS
        fps_text = font_small.render(f"FPS: {int(self.clock.get_fps())}", True, GREEN.to_rgb())
        self.screen.blit(fps_text, (WINDOW_WIDTH - 100, 20))

        # Dibujar frame count
        frame_text = font_small.render(f"Frame: {self.frame_count}", True, GREEN.to_rgb())
        self.screen.blit(frame_text, (WINDOW_WIDTH - 150, 50))

        # Dibujar cuadrado móvil (rojo)
        pygame.draw.rect(self.screen, RED.to_rgb(), (self.square_x, self.square_y, 50, 50))

        # Dibujar borde alrededor del cuadrado
        pygame.draw.rect(self.screen, YELLOW.to_rgb(), (self.square_x, self.square_y, 50, 50), 2)

        # Dibujar formas decorativas
        # Círculo azul
        pygame.draw.circle(self.screen, BLUE.to_rgb(), (WINDOW_WIDTH - 100, WINDOW_HEIGHT - 100), 40)

        # Líneas de colores
        pygame.draw.line(self.screen, RED.to_rgb(), (50, WINDOW_HEIGHT - 50), (250, WINDOW_HEIGHT - 50), 3)
        pygame.draw.line(self.screen, GREEN.to_rgb(), (50, WINDOW_HEIGHT - 40), (250, WINDOW_HEIGHT - 40), 3)
        pygame.draw.line(self.screen, BLUE.to_rgb(), (50, WINDOW_HEIGHT - 30), (250, WINDOW_HEIGHT - 30), 3)

        # Rectángulo con transparencia simulada (borde)
        pygame.draw.rect(self.screen, MAGENTA.to_rgb(), (300, WINDOW_HEIGHT - 120, 100, 80), 2)

        # Actualizar pantalla
        pygame.display.flip()

    def run(self):
        """Loop principal del juego."""
        print("\n" + "=" * 60)
        print("PYGAME TEST - LOOP INICIADO")
        print("=" * 60)
        print("Controles:")
        print("  - Flechas o WASD: Mover cuadrado")
        print("  - SPACE: Mensaje de prueba")
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

