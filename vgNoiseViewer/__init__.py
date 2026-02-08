"""
vgNoise Viewer - A visual noise generator tool.

This package provides a graphical interface to visualize and experiment
with different noise generation parameters compatible with Godot's FastNoiseLite.
"""

try:
    from .app import NoiseViewer, main
    from .config import ThemeColors, WindowConfig, ParameterConfig
    from .theme import ThemeManager
    from .noise_factory import NoiseGeneratorFactory, NoiseParameters
    from .image_utils import ImageGenerator, NoiseImageRenderer
    from .widgets import StepperControl, LabeledCombobox, LabeledSpinbox, Card, ScrollableFrame
except ImportError:
    # Direct execution
    pass

__all__ = [
    # Main application
    "NoiseViewer",
    "main",
    # Configuration
    "ThemeColors",
    "WindowConfig",
    "ParameterConfig",
    # Theme
    "ThemeManager",
    # Noise
    "NoiseGeneratorFactory",
    "NoiseParameters",
    # Image
    "ImageGenerator",
    "NoiseImageRenderer",
    # Widgets
    "StepperControl",
    "LabeledCombobox",
    "LabeledSpinbox",
    "Card",
    "ScrollableFrame",
]
