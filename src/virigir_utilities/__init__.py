"""
vgMath - A math library for Python.

Package structure:
    - core: Base classes and enumerations
    - generators: Noise generation algorithms
    - matrix: Matrix data structures
    - utils: Utility functions
"""

# Core
from vgmath.noise.core import (
    NoiseGenerator,
    NoiseType,
    FractalType,
    CellularDistanceFunction,
    CellularReturnType,
    DomainWarpType,
)

# Generators
from vgmath.noise.generators import (
    NoiseGenerator2D,
    NOISE_JSON_EXTENSION,
    PerlinNoise2D,
    OpenSimplexNoise2D,
    CellularNoise2D,
    ValueCubicNoise2D,
    ValueNoise2D,
    SimplexSmoothNoise2D,
)

# Matrix
from .matrix import Matrix2D

__all__ = [
    # Core
    "NoiseGenerator",
    "NoiseType",
    "FractalType",
    "CellularDistanceFunction",
    "CellularReturnType",
    "DomainWarpType",
    # Generators
    "NoiseGenerator2D",
    "NOISE_JSON_EXTENSION",
    "PerlinNoise2D",
    "OpenSimplexNoise2D",
    "CellularNoise2D",
    "ValueCubicNoise2D",
    "ValueNoise2D",
    "SimplexSmoothNoise2D",
    # Matrix
    "Matrix2D",
]
