"""
Domain Warp implementation using FastNoiseLite-compatible JIT kernels.

Domain warping distorts input coordinates before noise sampling, creating
organic and natural-looking patterns. Algorithms match FastNoiseLite exactly.
"""

from typing import Tuple, Optional
import numpy as np
from numpy.typing import NDArray

from virigir_math_utilities.noise.core import DomainWarpFractalType, DomainWarpType
from .kernels import domain_warp_2d_batch, calc_fractal_bounding


class DomainWarp2D:
    """
    2D Domain Warp generator compatible with FastNoiseLite.

    Warps coordinates before noise sampling using one of three warp types:
    - OpenSimplex2 (type 0)
    - OpenSimplex2Reduced (type 1)
    - BasicGrid (type 2)

    And three fractal modes: None, Progressive, Independent.
    """

    def __init__(
        self,
        enabled: bool = False,
        warp_type: DomainWarpType = DomainWarpType.OPEN_SIMPLEX_2,
        amplitude: float = 30.0,
        frequency: float = 0.05,
        fractal_type: DomainWarpFractalType = DomainWarpFractalType.NONE,
        fractal_octaves: int = 5,
        fractal_lacunarity: float = 2.0,
        fractal_gain: float = 0.5,
        seed: Optional[int] = None,
    ) -> None:
        self.enabled = enabled
        self.warp_type = warp_type
        self.amplitude = amplitude
        self.frequency = frequency
        self.fractal_type = fractal_type
        self.fractal_octaves = max(1, min(fractal_octaves, 9))
        self.fractal_lacunarity = fractal_lacunarity
        self.fractal_gain = fractal_gain
        self._seed = seed if seed is not None else 0
        self._fractal_bounding = calc_fractal_bounding(self.fractal_octaves, self.fractal_gain)

    @property
    def seed(self) -> int:
        return self._seed

    @seed.setter
    def seed(self, value: Optional[int]) -> None:
        self._seed = value if value is not None else 0

    def warp_coordinates(
        self,
        x: NDArray[np.float64],
        y: NDArray[np.float64],
    ) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
        """Apply domain warp to coordinate arrays."""
        if not self.enabled:
            return x, y

        original_shape = x.shape
        x_flat = x.ravel().astype(np.float64)
        y_flat = y.ravel().astype(np.float64)

        warped_x, warped_y = domain_warp_2d_batch(
            x_flat, y_flat,
            seed=self._seed,
            warp_type=int(self.warp_type.value),
            amplitude=float(self.amplitude),
            frequency=float(self.frequency),
            fractal_type=int(self.fractal_type.value),
            octaves=int(self.fractal_octaves),
            lacunarity=float(self.fractal_lacunarity),
            gain=float(self.fractal_gain),
            fractal_bounding=float(self._fractal_bounding),
        )

        return warped_x.reshape(original_shape), warped_y.reshape(original_shape)

    def warp_single(self, x: float, y: float) -> Tuple[float, float]:
        """Apply domain warp to a single point."""
        if not self.enabled:
            return x, y
        x_arr = np.array([x], dtype=np.float64)
        y_arr = np.array([y], dtype=np.float64)
        wx, wy = self.warp_coordinates(x_arr, y_arr)
        return float(wx[0]), float(wy[0])

    def to_dict(self) -> dict:
        return {
            "domain_warp_enabled": 1 if self.enabled else 0,
            "domain_warp_type": self.warp_type.value,
            "domain_warp_amplitude": self.amplitude,
            "domain_warp_frequency": self.frequency,
            "domain_warp_fractal_type": self.fractal_type.value,
            "domain_warp_fractal_gain": self.fractal_gain,
            "domain_warp_fractal_lacunarity": self.fractal_lacunarity,
            "domain_warp_fractal_octaves": self.fractal_octaves,
        }

    @classmethod
    def from_dict(cls, data: dict, seed: Optional[int] = None) -> "DomainWarp2D":
        return cls(
            enabled=bool(data.get("domain_warp_enabled", 0)),
            warp_type=DomainWarpType(data.get("domain_warp_type", 0)),
            amplitude=data.get("domain_warp_amplitude", 30.0),
            frequency=data.get("domain_warp_frequency", 0.05),
            fractal_type=DomainWarpFractalType(data.get("domain_warp_fractal_type", 0)),
            fractal_octaves=data.get("domain_warp_fractal_octaves", 5),
            fractal_lacunarity=data.get("domain_warp_fractal_lacunarity", 2.0),
            fractal_gain=data.get("domain_warp_fractal_gain", 0.5),
            seed=seed,
        )