"""
2D Noise Generator implementation with support for multiple noise types.
"""

import json
from pathlib import Path
from typing import Optional, Tuple, Sequence, Dict, Any, Union
import numpy as np
from numpy.typing import NDArray

from . import DomainWarp2D
from ..core import NoiseGenerator, FractalType, NoiseType, CellularDistanceFunction, CellularReturnType, DomainWarpType, \
    DomainWarpFractalType

# JSON file extension for noise configurations
NOISE_JSON_EXTENSION = ".noise.json"


class NoiseGenerator2D(NoiseGenerator):
    """
    2D Noise Generator facade supporting multiple noise algorithms.

    This class provides a unified interface to generate 2D noise using
    different algorithms (Perlin, Simplex, etc.). It delegates the actual
    noise generation to specialized implementations.

    Supports loading/saving noise configurations to JSON files.

    Attributes:
        seed: Random seed for reproducible noise generation.
        noise_type: The type of noise algorithm to use.
        _generator: The underlying noise generator instance.
        _config: Current noise configuration dictionary.
    """

    # Default configuration values
    DEFAULT_CONFIG: Dict[str, Any] = {
        "noise_type": NoiseType.PERLIN.name,
        "seed": 0,
        "frequency": 0.01,
        "offset_x": 0.0,
        "offset_y": 0.0,
        "fractal_type": FractalType.FBM.name,
        "octaves": 5,
        "lacunarity": 2.0,
        "persistence": 0.5,
        "weighted_strength": 0.0,
        "ping_pong_strength": 2.0,
        # Cellular-specific
        "cellular_distance_function": CellularDistanceFunction.EUCLIDEAN_SQUARED.name,
        "cellular_return_type": CellularReturnType.DISTANCE.name,
        "cellular_jitter": 1.0,
        # Domain warp
        "domain_warp_enabled": 0,
        "domain_warp_type": DomainWarpType.SIMPLEX.value,
        "domain_warp_amplitude": 30.0,
        "domain_warp_frequency": 0.05,
        "domain_warp_fractal_type": DomainWarpFractalType.NONE.value,
        "domain_warp_fractal_octaves": 5,
        "domain_warp_fractal_lacunarity": 2.0,
        "domain_warp_fractal_gain": 0.5,
    }

    def __init__(
        self,
        seed: Optional[int] = None,
        noise_type: NoiseType = NoiseType.PERLIN,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the 2D noise generator.

        Args:
            seed: Optional random seed for reproducibility.
            noise_type: The type of noise algorithm to use (default: PERLIN).
            config: Optional dictionary with noise configuration (from JSON).
                   If provided, seed and noise_type parameters are ignored.

        Raises:
            NotImplementedError: If the requested noise type is not yet implemented.
        """
        # If config is provided, use it to initialize
        if config is not None:
            self._config = {**self.DEFAULT_CONFIG, **config}
            seed = self._config.get("seed", 0)
            noise_type = NoiseType[self._config.get("noise_type", "PERLIN")]
        else:
            self._config = {
                **self.DEFAULT_CONFIG,
                "seed": seed if seed is not None else 0,
                "noise_type": noise_type.name,
            }

        super().__init__(seed)
        self._noise_type = noise_type
        self._generator = self._create_generator_from_config(self._config)
        self._domain_warp = self._create_domain_warp_from_config(self._config)

    def _create_domain_warp_from_config(self, config: Dict[str, Any]) -> DomainWarp2D:
        """
        Create the domain warp generator based on the configuration.

        Args:
            config: Dictionary with noise configuration.

        Returns:
            A DomainWarp2D instance.
        """
        return DomainWarp2D.from_dict(config, seed=config.get("seed", 0))

    def _create_generator_from_config(self, config: Dict[str, Any]) -> NoiseGenerator:
        """
        Create the appropriate noise generator based on the configuration.

        Args:
            config: Dictionary with noise configuration.

        Returns:
            A noise generator instance.

        Raises:
            NotImplementedError: If the requested noise type is not yet implemented.
        """
        noise_type = NoiseType[config.get("noise_type", "PERLIN")]

        # Common parameters
        common_params = {
            "seed": config.get("seed"),
            "frequency": config.get("frequency", 0.01),
            "offset": (config.get("offset_x", 0.0), config.get("offset_y", 0.0)),
            "fractal_type": FractalType[config.get("fractal_type", "FBM")],
            "octaves": config.get("octaves", 5),
            "lacunarity": config.get("lacunarity", 2.0),
            "persistence": config.get("persistence", 0.5),
            "weighted_strength": config.get("weighted_strength", 0.0),
            "ping_pong_strength": config.get("ping_pong_strength", 2.0),
        }

        if noise_type == NoiseType.PERLIN:
            from .perlin2d import PerlinNoise2D
            return PerlinNoise2D(**common_params)

        elif noise_type == NoiseType.SIMPLEX:
            from .opensimplex2d import OpenSimplexNoise2D
            return OpenSimplexNoise2D(**common_params)

        elif noise_type == NoiseType.SIMPLEX_SMOOTH:
            from .simplexsmooth2d import SimplexSmoothNoise2D
            return SimplexSmoothNoise2D(**common_params)

        elif noise_type == NoiseType.CELLULAR:
            from .cellular2d import CellularNoise2D
            cellular_params = {
                **common_params,
                "distance_function": CellularDistanceFunction[
                    config.get("cellular_distance_function", "EUCLIDEAN_SQUARED")
                ],
                "return_type": CellularReturnType[
                    config.get("cellular_return_type", "DISTANCE")
                ],
                "jitter": config.get("cellular_jitter", 1.0),
            }
            return CellularNoise2D(**cellular_params)

        elif noise_type == NoiseType.VALUE_CUBIC:
            from .valuecubic2d import ValueCubicNoise2D
            return ValueCubicNoise2D(**common_params)

        elif noise_type == NoiseType.VALUE:
            from .value2d import ValueNoise2D
            return ValueNoise2D(**common_params)

        else:
            raise NotImplementedError(
                f"Noise type {noise_type.name} is not yet implemented. "
                f"Currently supported: PERLIN, SIMPLEX, SIMPLEX_SMOOTH, CELLULAR, VALUE_CUBIC, VALUE"
            )

    def _create_generator(
        self,
        noise_type: NoiseType,
        seed: Optional[int]
    ) -> NoiseGenerator:
        """
        Create the appropriate noise generator based on the noise type.
        Legacy method for backward compatibility.
        """
        config = {**self._config, "noise_type": noise_type.name, "seed": seed}
        return self._create_generator_from_config(config)

    @property
    def config(self) -> Dict[str, Any]:
        """Get the current noise configuration as a dictionary."""
        return self._config.copy()

    @config.setter
    def config(self, value: Dict[str, Any]) -> None:
        """Set the noise configuration and recreate the generator."""
        self._config = {**self.DEFAULT_CONFIG, **value}
        self._noise_type = NoiseType[self._config.get("noise_type", "PERLIN")]
        self.seed = self._config.get("seed", 0)
        self._generator = self._create_generator_from_config(self._config)
        self._domain_warp = self._create_domain_warp_from_config(self._config)

    @property
    def noise_type(self) -> NoiseType:
        """Get the current noise type."""
        return self._noise_type

    @noise_type.setter
    def noise_type(self, value: NoiseType) -> None:
        """Set the noise type and recreate the underlying generator."""
        if value != self._noise_type:
            self._noise_type = value
            self._config["noise_type"] = value.name
            self._generator = self._create_generator_from_config(self._config)

    @property
    def dimensions(self) -> int:
        """Return the number of dimensions (2 for this generator)."""
        return 2

    @property
    def generator(self) -> NoiseGenerator:
        """Get the underlying noise generator instance."""
        return self._generator

    @property
    def domain_warp(self) -> DomainWarp2D:
        """Get the domain warp generator instance."""
        return self._domain_warp

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the noise configuration to a dictionary for JSON serialization.

        Returns:
            Dictionary with all noise parameters. Enum values are stored as integers.
        """
        # Get enum values as integers
        noise_type_str = self._config.get("noise_type", "PERLIN")
        fractal_type_str = self._config.get("fractal_type", "FBM")
        dist_func_str = self._config.get("cellular_distance_function", "EUCLIDEAN_SQUARED")
        return_type_str = self._config.get("cellular_return_type", "DISTANCE")

        result = {
            "version": "1.0",
            "noise_type": NoiseType[noise_type_str].value,
            "seed": self._config.get("seed", 0),
            "frequency": self._config.get("frequency", 0.01),
            "offset_x": self._config.get("offset_x", 0.0),
            "offset_y": self._config.get("offset_y", 0.0),
            "fractal_type": FractalType[fractal_type_str].value,
            "octaves": self._config.get("octaves", 5),
            "lacunarity": self._config.get("lacunarity", 2.0),
            "persistence": self._config.get("persistence", 0.5),
            "weighted_strength": self._config.get("weighted_strength", 0.0),
            "ping_pong_strength": self._config.get("ping_pong_strength", 2.0),
            # Cellular-specific
            "cellular_distance_function": CellularDistanceFunction[dist_func_str].value,
            "cellular_return_type": CellularReturnType[return_type_str].value,
            "cellular_jitter": self._config.get("cellular_jitter", 1.0),
        }

        # Add domain warp fields
        result.update(self._domain_warp.to_dict())

        return result

    @staticmethod
    def _enum_value_to_name(enum_class, value) -> str:
        """
        Convert an enum value (int or str) to its name.

        Args:
            enum_class: The enum class to use.
            value: Either an integer value or a string name.

        Returns:
            The name of the enum member.
        """
        if isinstance(value, int):
            # Convert integer to enum name
            for member in enum_class:
                if member.value == value:
                    return member.name
            # Fallback to first member if not found
            return list(enum_class)[0].name
        else:
            # Already a string, return as-is
            return str(value)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NoiseGenerator2D":
        """
        Create a NoiseGenerator2D from a dictionary.

        Args:
            data: Dictionary with noise configuration. Enum values can be
                  either integers or strings.

        Returns:
            A new NoiseGenerator2D instance.
        """
        # Convert integer enum values to string names for internal config
        converted_config = data.copy()

        if "noise_type" in converted_config:
            converted_config["noise_type"] = cls._enum_value_to_name(
                NoiseType, converted_config["noise_type"]
            )

        if "fractal_type" in converted_config:
            converted_config["fractal_type"] = cls._enum_value_to_name(
                FractalType, converted_config["fractal_type"]
            )

        if "cellular_distance_function" in converted_config:
            converted_config["cellular_distance_function"] = cls._enum_value_to_name(
                CellularDistanceFunction, converted_config["cellular_distance_function"]
            )

        if "cellular_return_type" in converted_config:
            converted_config["cellular_return_type"] = cls._enum_value_to_name(
                CellularReturnType, converted_config["cellular_return_type"]
            )

        return cls(config=converted_config)

    @classmethod
    def all_from_config_json(
        cls, filepath: Union[str, Path]
    ) -> Dict[str, "NoiseGenerator2D"]:
        """
        Load all noise generators defined in a config.json file.

        The JSON file is expected to have a ``"noise"`` key containing a
        mapping of noise names to their noise parameter dictionaries.

        Args:
            filepath: Path to the config.json file.

        Returns:
            A dictionary mapping noise names to NoiseGenerator2D instances.

        Example::

            generators = NoiseGenerator2D.all_from_config_json(
                "configs/config.json"
            )
            base_elevation = generators["base_elevation"]
            continentality = generators["continentality"]
        """
        filepath = Path(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        noise_section = data.get("noise", {})
        generators: Dict[str, "NoiseGenerator2D"] = {}
        for name, noise_data in noise_section.items():
            generators[name] = cls.from_dict(noise_data)

        return generators

    def save_to_json(self, filepath: Union[str, Path]) -> None:
        """
        Save the noise configuration to a JSON file.

        Args:
            filepath: Path to the output file. If it doesn't end with
                     '.noise.json', the extension will be added.
        """
        filepath = Path(filepath)

        # Ensure proper extension
        if not str(filepath).endswith(NOISE_JSON_EXTENSION):
            filepath = Path(str(filepath) + NOISE_JSON_EXTENSION)

        # Create parent directories if needed
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Write JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_json(cls, filepath: Union[str, Path]) -> "NoiseGenerator2D":
        """
        Load a noise configuration from a JSON file.

        Args:
            filepath: Path to the JSON file.

        Returns:
            A new NoiseGenerator2D instance with the loaded configuration.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            json.JSONDecodeError: If the file is not valid JSON.
            KeyError: If required fields are missing.
        """
        filepath = Path(filepath)

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return cls.from_dict(data)

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

        # Apply domain warp if enabled
        if self._domain_warp.enabled:
            warped_x, warped_y = self._domain_warp.warp_single(position[0], position[1])
            position = (warped_x, warped_y)

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
        # Apply domain warp if enabled
        if self._domain_warp.enabled:
            x, y = self._domain_warp.warp_coordinates(x, y)

        if hasattr(self._generator, 'get_values_vectorized'):
            return self._generator.get_values_vectorized(x, y)
        else:
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

        # Create coordinate arrays
        x_coords = np.linspace(region[0][0], region[0][1], region[0][2])
        y_coords = np.linspace(region[1][0], region[1][1], region[1][2])

        xx, yy = np.meshgrid(x_coords, y_coords, indexing='ij')
        shape = xx.shape

        # Apply domain warp if enabled
        if self._domain_warp.enabled:
            warped_x, warped_y = self._domain_warp.warp_coordinates(xx, yy)
            x_flat = warped_x.ravel().astype(np.float64)
            y_flat = warped_y.ravel().astype(np.float64)
        else:
            x_flat = xx.ravel().astype(np.float64)
            y_flat = yy.ravel().astype(np.float64)

        # Generate noise using the underlying generator's vectorized method if available
        if hasattr(self._generator, 'get_values_vectorized'):
            result = self._generator.get_values_vectorized(x_flat, y_flat)
        else:
            result = np.empty(x_flat.shape, dtype=np.float64)
            for i in range(len(x_flat)):
                result[i] = self._generator.get_value_at((x_flat[i], y_flat[i]))

        return result.reshape(shape)

