"""
Test scenes package.

Contains example scenes for testing different features.
"""

from .base_scene import BaseScene
from .noise_editor_scene import NoiseEditorScene
from .tilemap_camera_scene import TilemapCameraScene
from .random_terrain_scene import RandomTerrainScene
from .character_test_scene import CharacterTestScene
from .matrix_viewer_scene import MatrixViewerScene
from .world_editor_scene import WorldEditorScene

# Registry of all available scenes
AVAILABLE_SCENES = [
    TilemapCameraScene,
    RandomTerrainScene,
    CharacterTestScene,
    MatrixViewerScene,
]


def get_scene_by_index(index: int) -> BaseScene:
    """
    Get a scene by its index.

    Args:
        index: Scene index (0-based).

    Returns:
        Scene instance or None if invalid index.
    """
    if 0 <= index < len(AVAILABLE_SCENES):
        return AVAILABLE_SCENES[index]()
    return None


def get_scene_list() -> list:
    """
    Get list of available scene names.

    Returns:
        List of scene names.
    """
    scenes = []
    for scene_class in AVAILABLE_SCENES:
        scene = scene_class()
        scenes.append(f"{scene.name}: {scene.description}")
    return scenes


__all__ = [
    "BaseScene",
    "TilemapCameraScene",
    "RandomTerrainScene",
    "CharacterTestScene",
    "MatrixViewerScene",
    "NoiseEditorScene",
    "WorldEditorScene",
    "AVAILABLE_SCENES",
    "get_scene_by_index",
    "get_scene_list",
]

