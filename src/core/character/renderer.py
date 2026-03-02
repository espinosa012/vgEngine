"""
CharacterRenderer — centraliza el renderizado de BaseCharacter.

Separa la lógica visual del modelo de datos del personaje.
El renderer es quien asigna y posee el shape del personaje; de esta
forma el mismo personaje puede renderizarse de maneras distintas sin
modificar BaseCharacter en absoluto.

Uso básico
----------
    renderer = CharacterRenderer(character)
    renderer.draw(surface)

Con shape personalizado
-----------------------
    from core.character.shape import RectShape
    from core.color.color import Colors

    renderer = CharacterRenderer(
        character,
        shape=RectShape(24, 32, color=Colors.RED, border_width=1),
    )
    renderer.draw(surface)

Con cámara/offset
-----------------
    renderer.draw(surface, offset_x=camera.x, offset_y=camera.y)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import pygame

from core.character.shape import CharacterShape, RectShape
from core.color.color import Colors

if TYPE_CHECKING:
    from core.character.base import BaseCharacter


class CharacterRenderer:
    """
    Responsable de dibujar un BaseCharacter en una pygame.Surface.

    El renderer es el propietario lógico del CharacterShape del personaje.
    Al crear el renderer se asigna automáticamente el shape al campo
    ``character.shape`` para que el propio personaje también pueda usarlo
    para cálculos de colisión / posicionamiento en grid.

    Attributes:
        character:   El personaje que se renderiza.
        shape:       Forma visual asignada al personaje.
        show_health: Si True, dibuja una barra de salud sobre el personaje.
        health_bar_height: Altura en píxeles de la barra de salud.
        health_bar_offset: Separación vertical entre personaje y barra.
    """

    # Defaults para la barra de salud
    _HEALTH_BG_COLOR = (60, 60, 60, 200)
    _HEALTH_FG_COLOR = (220, 60, 60, 255)
    _HEALTH_BAR_HEIGHT = 4
    _HEALTH_BAR_OFFSET = 3

    def __init__(
        self,
        character: "BaseCharacter",
        shape: Optional[CharacterShape] = None,
        show_health: bool = False,
        health_bar_height: int = _HEALTH_BAR_HEIGHT,
        health_bar_offset: int = _HEALTH_BAR_OFFSET,
    ) -> None:
        """
        Inicializa el renderer y asigna el shape al personaje.

        Args:
            character:         Instancia de BaseCharacter a renderizar.
            shape:             Shape visual. Si es None se usa un RectShape
                               blanco de 32×32 píxeles.
            show_health:       Mostrar barra de salud (defecto: False).
            health_bar_height: Altura de la barra de salud en píxeles.
            health_bar_offset: Espacio entre el personaje y la barra.
        """
        self.character = character

        # Asignar shape — el renderer es quien toma esta decisión
        self.shape: CharacterShape = shape or RectShape(
            width=32,
            height=32,
            color=Colors.WHITE,
            border_width=1,
        )
        # Propagar el shape al personaje para que lo use en sus cálculos
        character.shape = self.shape

        self.show_health = show_health
        self.health_bar_height = health_bar_height
        self.health_bar_offset = health_bar_offset

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def draw(
        self,
        surface: pygame.Surface,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
    ) -> None:
        """
        Dibuja el personaje en *surface* aplicando el offset de cámara.

        Args:
            surface:  Superficie pygame sobre la que dibujar.
            offset_x: Desplazamiento horizontal (típicamente camera.x).
            offset_y: Desplazamiento vertical (típicamente camera.y).
        """
        draw_x = self.character.x - offset_x
        draw_y = self.character.y - offset_y

        self.shape.draw(surface, draw_x, draw_y)

        if self.show_health:
            self._draw_health_bar(surface, draw_x, draw_y)

    def draw_at_cell(
        self,
        surface: pygame.Surface,
        tile_x: int,
        tile_y: int,
        tile_w: int,
        tile_h: int,
        floor_gap: int = 2,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
    ) -> None:
        """
        Dibuja el personaje centrado en la parte inferior de una celda del
        tilemap.

        Útil cuando la cámara trabaja en espacio mundo y el tilemap ya está
        desplazado por el offset de cámara.

        Args:
            surface:   Superficie pygame destino.
            tile_x:    Columna de la celda en unidades de tile.
            tile_y:    Fila de la celda en unidades de tile.
            tile_w:    Ancho de un tile en píxeles.
            tile_h:    Alto de un tile en píxeles.
            floor_gap: Píxeles de margen entre los pies y el suelo del tile.
            offset_x:  Desplazamiento horizontal de cámara.
            offset_y:  Desplazamiento vertical de cámara.
        """
        cell_px = tile_x * tile_w - offset_x
        cell_py = tile_y * tile_h - offset_y

        draw_x = cell_px + (tile_w - self.shape.width) // 2
        draw_y = cell_py + tile_h - self.shape.height - floor_gap

        self.shape.draw(surface, draw_x, draw_y)

        if self.show_health:
            self._draw_health_bar(surface, draw_x, draw_y)

    def set_shape(self, shape: CharacterShape) -> None:
        """
        Reemplaza el shape en tiempo de ejecución y lo propaga al personaje.

        Args:
            shape: Nuevo shape visual.
        """
        self.shape = shape
        self.character.shape = shape

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _draw_health_bar(
        self,
        surface: pygame.Surface,
        draw_x: float,
        draw_y: float,
    ) -> None:
        """Dibuja una barra de salud sobre el personaje."""
        bar_w = self.shape.width
        bar_h = self.health_bar_height
        bar_x = int(draw_x)
        bar_y = int(draw_y) - bar_h - self.health_bar_offset

        # Fondo
        bg_rect = pygame.Rect(bar_x, bar_y, bar_w, bar_h)
        bg_surf = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
        bg_surf.fill(self._HEALTH_BG_COLOR)
        surface.blit(bg_surf, bg_rect)

        # Barra de vida actual
        hp_pct = self.character.health_percentage
        hp_w = max(0, int(bar_w * hp_pct))
        if hp_w > 0:
            fg_surf = pygame.Surface((hp_w, bar_h), pygame.SRCALPHA)
            fg_surf.fill(self._HEALTH_FG_COLOR)
            surface.blit(fg_surf, (bar_x, bar_y))

    def __repr__(self) -> str:
        return (
            f"CharacterRenderer("
            f"character={self.character.name!r}, "
            f"shape={self.shape!r}, "
            f"show_health={self.show_health})"
        )

