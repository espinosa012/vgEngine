"""
Enumerations for vgNoise library.

Enum values match FastNoiseLite exactly so that integer values from
config.json map to the correct noise algorithms.
"""

from enum import Enum


class NoiseType(Enum):
    """Supported noise algorithms (matches FastNoiseLite enum ordering)."""
    OPEN_SIMPLEX_2 = 0   # FastNoiseLite: NoiseType_OpenSimplex2
    OPEN_SIMPLEX_2S = 1  # FastNoiseLite: NoiseType_OpenSimplex2S
    CELLULAR = 2         # FastNoiseLite: NoiseType_Cellular
    PERLIN = 3           # FastNoiseLite: NoiseType_Perlin
    VALUE_CUBIC = 4      # FastNoiseLite: NoiseType_ValueCubic
    VALUE = 5            # FastNoiseLite: NoiseType_Value


class FractalType(Enum):
    """Fractal combination types compatible with FastNoiseLite."""
    NONE = 0        # Single octave, no fractal
    FBM = 1         # Fractal Brownian Motion
    RIDGED = 2      # Ridged multifractal
    PING_PONG = 3   # Ping-pong / terraced


class CellularDistanceFunction(Enum):
    """Distance functions for cellular/Worley noise."""
    EUCLIDEAN = 0
    EUCLIDEAN_SQUARED = 1
    MANHATTAN = 2
    HYBRID = 3


class CellularReturnType(Enum):
    """Return value types for cellular noise."""
    CELL_VALUE = 0
    DISTANCE = 1
    DISTANCE_2 = 2
    DISTANCE_2_ADD = 3
    DISTANCE_2_SUB = 4
    DISTANCE_2_MUL = 5
    DISTANCE_2_DIV = 6


class DomainWarpType(Enum):
    """Domain warp types compatible with FastNoiseLite."""
    OPEN_SIMPLEX_2 = 0
    OPEN_SIMPLEX_2_REDUCED = 1
    BASIC_GRID = 2


class DomainWarpFractalType(Enum):
    """Fractal types for domain warp."""
    NONE = 0        # Single iteration
    PROGRESSIVE = 1  # Progressive (warp accumulates each octave)
    INDEPENDENT = 2  # Independent (each octave warps original coords)