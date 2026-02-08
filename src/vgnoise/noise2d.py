"""
2D Noise Generator implementation with support for multiple noise types.
"""

from typing import Optional, Tuple, Sequence
import numpy as np
from numpy.typing import NDArray

from .base import NoiseGenerator
from .enums import NoiseType


class NoiseGenerator2D(NoiseGenerator):
    """
    2D Noise Generator facade supporting multiple noise algorithms.

    This class provides a unified interface to generate 2D noise using
    different algorithms (Perlin, Simplex, etc.). It delegates the actual
    noise generation to specialized implementations.

    Attributes:
        seed: Random seed for reproducible noise generation.
        noise_type: The type of noise algorithm to use.
        _generator: The underlying noise generator instance.
    """

    def __init__(
        self,
        seed: Optional[int] = None,
        noise_type: NoiseType = NoiseType.PERLIN
    ) -> None:
        """
        Initialize the 2D noise generator.

        Args:
            seed: Optional random seed for reproducibility.
            noise_type: The type of noise algorithm to use (default: PERLIN).

        Raises:
            NotImplementedError: If the requested noise type is not yet implemented.
        """
        super().__init__(seed)
        self._noise_type = noise_type
        self._generator = self._create_generator(noise_type, seed)

    def _create_generator(
        self,
        noise_type: NoiseType,
        seed: Optional[int]
    ) -> NoiseGenerator:
        """
        Create the appropriate noise generator based on the noise type.

        Args:
            noise_type: The type of noise algorithm to use.
            seed: Optional random seed for reproducibility.

        Returns:
            A noise generator instance.

        Raises:
            NotImplementedError: If the requested noise type is not yet implemented.
        """
        if noise_type == NoiseType.PERLIN:
            from .perlin2d import PerlinNoise2D
            return PerlinNoise2D(seed=seed)
        elif noise_type == NoiseType.SIMPLEX:
            from .opensimplex2d import OpenSimplexNoise2D
            return OpenSimplexNoise2D(seed=seed)
        elif noise_type == NoiseType.SIMPLEX_SMOOTH:
            from .opensimplex2d import OpenSimplexNoise2D
            # Smooth simplex uses multiple octaves
            return OpenSimplexNoise2D(octaves=4, persistence=0.5, seed=seed)
        else:
            raise NotImplementedError(
                f"Noise type {noise_type.name} is not yet implemented. "
                f"Currently supported: PERLIN, SIMPLEX, SIMPLEX_SMOOTH"
            )

    @property
    def noise_type(self) -> NoiseType:
        """Get the current noise type."""
        return self._noise_type

    @noise_type.setter
    def noise_type(self, value: NoiseType) -> None:
        """
        Set the noise type and recreate the underlying generator.

        Args:
            value: The new noise type to use.
        """
        if value != self._noise_type:
            self._noise_type = value
            self._generator = self._create_generator(value, self.seed)

    @property
    def dimensions(self) -> int:
        """Return the number of dimensions (2 for this generator)."""
        return 2

    @property
    def generator(self) -> NoiseGenerator:
        """Get the underlying noise generator instance."""
        return self._generator

    def get_value_at(self, position: Tuple[float, ...]) -> np.float64:
        """
        Get the noise value at a specific 2D position.

        Args:
            position: A tuple (x, y) containing the 2D coordinates.

        Returns:
            A noise value normalized to the range [0, 1].

        Raises:
            ValueError: If the position doesn't have exactly 2 elements.
        """
        if len(position) != 2:
            raise ValueError(f"Position must have 2 elements, got {len(position)}")
        return self._generator.get_value_at(position)

    def get_values_vectorized(
        self,
        x: NDArray[np.float64],
        y: NDArray[np.float64]
    ) -> NDArray[np.float64]:
        """
        Vectorized noise computation for arrays of coordinates.

        Args:
            x: Array of X coordinates.
            y: Array of Y coordinates.

        Returns:
            Array of noise values normalized to [0, 1].
        """
        # Check if the underlying generator supports vectorized computation
        if hasattr(self._generator, 'get_values_vectorized'):
            return self._generator.get_values_vectorized(x, y)
        else:
            # Fallback to non-vectorized computation
            result = np.empty(x.shape, dtype=np.float64)
            for i in range(len(x.flat)):
                result.flat[i] = self._generator.get_value_at((x.flat[i], y.flat[i]))
            return result

    def generate_region(
        self,
        region: Sequence[Tuple[float, float, int]]
    ) -> NDArray[np.float64]:
        """
        Generate noise values over a defined region (optimized).

        Args:
            region: A sequence defining the region to generate. Each element is a tuple
                    of (start, end, num_points) for each dimension.

        Returns:
            A NumPy array of noise values normalized to the range [0, 1].
        """
        if len(region) != self.dimensions:
            raise ValueError(
                f"Region must have {self.dimensions} dimensions, got {len(region)}"
            )

        # Delegate to the underlying generator if it has an optimized implementation
        if hasattr(self._generator, 'generate_region'):
            return self._generator.generate_region(region)

        # Fallback implementation
        x_coords = np.linspace(region[0][0], region[0][1], region[0][2])
        y_coords = np.linspace(region[1][0], region[1][1], region[1][2])

        xx, yy = np.meshgrid(x_coords, y_coords, indexing='ij')
        shape = xx.shape
        x_flat = xx.flatten().astype(np.float64)
        y_flat = yy.flatten().astype(np.float64)

        result = self.get_values_vectorized(x_flat, y_flat)

        return result.reshape(shape)

