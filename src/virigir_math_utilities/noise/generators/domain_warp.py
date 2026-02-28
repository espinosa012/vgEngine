"""
Domain Warp implementation with Numba JIT acceleration.

This module implements domain warping compatible with Godot's FastNoiseLite.
Domain warping distorts the input coordinates before sampling noise,
creating more organic and natural-looking patterns.
"""

from typing import Tuple, Optional
import numpy as np
from numba import njit, prange
from numpy.typing import NDArray

from virigir_math_utilities.noise.core import DomainWarpFractalType, DomainWarpType

# ============================================================================
# Constants
# ============================================================================

# Rotation matrix constants for 2D domain warp (similar to Godot)
ROTATE_2D_COS = 0.6  # cos(53.13°) approximately
ROTATE_2D_SIN = 0.8  # sin(53.13°) approximately

# Simplex gradients for domain warp (scaled for amplitude)
SIMPLEX_GRADIENTS_2D = np.array([
    [1.0, 0.0], [-1.0, 0.0], [0.0, 1.0], [0.0, -1.0],
    [0.707107, 0.707107], [-0.707107, 0.707107],
    [0.707107, -0.707107], [-0.707107, -0.707107],
], dtype=np.float64)


# ============================================================================
# JIT Kernels - Simplex Domain Warp
# ============================================================================

@njit(fastmath=True, cache=True)
def _simplex_warp_single(
    x: float,
    y: float,
    perm: NDArray[np.int32],
    amplitude: float
) -> Tuple[float, float]:
    """
    Compute simplex-based domain warp offset for a single point.

    Args:
        x: X coordinate
        y: Y coordinate
        perm: Permutation table
        amplitude: Warp amplitude

    Returns:
        Tuple of (warp_x, warp_y) offsets
    """
    # Skew input space to determine which simplex cell we're in
    F2 = 0.5 * (np.sqrt(3.0) - 1.0)
    G2 = (3.0 - np.sqrt(3.0)) / 6.0

    s = (x + y) * F2
    i = int(np.floor(x + s))
    j = int(np.floor(y + s))

    t = (i + j) * G2
    X0 = i - t
    Y0 = j - t
    x0 = x - X0
    y0 = y - Y0

    # Determine which simplex
    if x0 > y0:
        i1, j1 = 1, 0
    else:
        i1, j1 = 0, 1

    x1 = x0 - i1 + G2
    y1 = y0 - j1 + G2
    x2 = x0 - 1.0 + 2.0 * G2
    y2 = y0 - 1.0 + 2.0 * G2

    # Hash coordinates
    ii = i & 255
    jj = j & 255

    gi0 = perm[ii + perm[jj]] & 7
    gi1 = perm[ii + i1 + perm[jj + j1]] & 7
    gi2 = perm[ii + 1 + perm[jj + 1]] & 7

    # Calculate contributions
    warp_x = 0.0
    warp_y = 0.0

    t0 = 0.5 - x0 * x0 - y0 * y0
    if t0 > 0:
        t0 *= t0
        t02 = t0 * t0
        gx = SIMPLEX_GRADIENTS_2D[gi0, 0]
        gy = SIMPLEX_GRADIENTS_2D[gi0, 1]
        warp_x += t02 * gx
        warp_y += t02 * gy

    t1 = 0.5 - x1 * x1 - y1 * y1
    if t1 > 0:
        t1 *= t1
        t12 = t1 * t1
        gx = SIMPLEX_GRADIENTS_2D[gi1, 0]
        gy = SIMPLEX_GRADIENTS_2D[gi1, 1]
        warp_x += t12 * gx
        warp_y += t12 * gy

    t2 = 0.5 - x2 * x2 - y2 * y2
    if t2 > 0:
        t2 *= t2
        t22 = t2 * t2
        gx = SIMPLEX_GRADIENTS_2D[gi2, 0]
        gy = SIMPLEX_GRADIENTS_2D[gi2, 1]
        warp_x += t22 * gx
        warp_y += t22 * gy

    # Scale by amplitude
    scale = 38.283687591552734375 * amplitude
    return warp_x * scale, warp_y * scale


@njit(fastmath=True, cache=True)
def _basic_grid_warp_single(
    x: float,
    y: float,
    perm: NDArray[np.int32],
    amplitude: float
) -> Tuple[float, float]:
    """
    Compute basic grid-based domain warp offset for a single point.
    Uses value noise gradient estimation.

    Args:
        x: X coordinate
        y: Y coordinate
        perm: Permutation table
        amplitude: Warp amplitude

    Returns:
        Tuple of (warp_x, warp_y) offsets
    """
    floor_x = int(np.floor(x))
    floor_y = int(np.floor(y))

    xf = x - floor_x
    yf = y - floor_y

    ix = floor_x & 255
    iy = floor_y & 255
    ix1 = (ix + 1) & 255
    iy1 = (iy + 1) & 255

    # Fade curves
    u = xf * xf * xf * (xf * (xf * 6.0 - 15.0) + 10.0)
    v = yf * yf * yf * (yf * (yf * 6.0 - 15.0) + 10.0)

    # Hash to get pseudo-random gradients
    h00 = perm[ix + perm[iy]]
    h10 = perm[ix1 + perm[iy]]
    h01 = perm[ix + perm[iy1]]
    h11 = perm[ix1 + perm[iy1]]

    # Convert hash to gradient vectors (simple approach)
    def hash_to_grad(h):
        gx = ((h & 15) / 7.5) - 1.0
        gy = (((h >> 4) & 15) / 7.5) - 1.0
        return gx, gy

    gx00, gy00 = hash_to_grad(h00)
    gx10, gy10 = hash_to_grad(h10)
    gx01, gy01 = hash_to_grad(h01)
    gx11, gy11 = hash_to_grad(h11)

    # Bilinear interpolation of gradients
    gx0 = gx00 + u * (gx10 - gx00)
    gx1 = gx01 + u * (gx11 - gx01)
    warp_x = (gx0 + v * (gx1 - gx0)) * amplitude

    gy0 = gy00 + u * (gy10 - gy00)
    gy1 = gy01 + u * (gy11 - gy01)
    warp_y = (gy0 + v * (gy1 - gy0)) * amplitude

    return warp_x, warp_y


# ============================================================================
# JIT Kernels - Vectorized Domain Warp (No Fractal)
# ============================================================================

@njit(parallel=True, fastmath=True, cache=True)
def domain_warp_simplex_2d(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    perm: NDArray[np.int32],
    frequency: float,
    amplitude: float
) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Apply simplex domain warp to coordinate arrays (no fractal).

    Args:
        x: Array of X coordinates
        y: Array of Y coordinates
        perm: Permutation table
        frequency: Warp frequency
        amplitude: Warp amplitude

    Returns:
        Tuple of (warped_x, warped_y) arrays
    """
    n = len(x)
    out_x = np.empty(n, dtype=np.float64)
    out_y = np.empty(n, dtype=np.float64)

    for i in prange(n):
        xs = x[i] * frequency
        ys = y[i] * frequency

        wx, wy = _simplex_warp_single(xs, ys, perm, amplitude)

        out_x[i] = x[i] + wx
        out_y[i] = y[i] + wy

    return out_x, out_y


@njit(parallel=True, fastmath=True, cache=True)
def domain_warp_basic_grid_2d(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    perm: NDArray[np.int32],
    frequency: float,
    amplitude: float
) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Apply basic grid domain warp to coordinate arrays (no fractal).

    Args:
        x: Array of X coordinates
        y: Array of Y coordinates
        perm: Permutation table
        frequency: Warp frequency
        amplitude: Warp amplitude

    Returns:
        Tuple of (warped_x, warped_y) arrays
    """
    n = len(x)
    out_x = np.empty(n, dtype=np.float64)
    out_y = np.empty(n, dtype=np.float64)

    for i in prange(n):
        xs = x[i] * frequency
        ys = y[i] * frequency

        wx, wy = _basic_grid_warp_single(xs, ys, perm, amplitude)

        out_x[i] = x[i] + wx
        out_y[i] = y[i] + wy

    return out_x, out_y


# ============================================================================
# JIT Kernels - Fractal Domain Warp (Progressive)
# ============================================================================

@njit(parallel=True, fastmath=True, cache=True)
def domain_warp_simplex_fractal_progressive_2d(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    perm: NDArray[np.int32],
    frequency: float,
    amplitude: float,
    octaves: int,
    lacunarity: float,
    gain: float
) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Apply simplex domain warp with progressive fractal.
    Each octave warps the already-warped coordinates from the previous octave.

    Args:
        x: Array of X coordinates
        y: Array of Y coordinates
        perm: Permutation table
        frequency: Base warp frequency
        amplitude: Base warp amplitude
        octaves: Number of fractal octaves
        lacunarity: Frequency multiplier per octave
        gain: Amplitude multiplier per octave

    Returns:
        Tuple of (warped_x, warped_y) arrays
    """
    n = len(x)
    out_x = x.copy()
    out_y = y.copy()

    for i in prange(n):
        wx = out_x[i]
        wy = out_y[i]

        freq = frequency
        amp = amplitude

        for _ in range(octaves):
            xs = wx * freq
            ys = wy * freq

            dx, dy = _simplex_warp_single(xs, ys, perm, amp)

            # Apply warp with rotation for variety
            wx += dx * ROTATE_2D_COS - dy * ROTATE_2D_SIN
            wy += dx * ROTATE_2D_SIN + dy * ROTATE_2D_COS

            freq *= lacunarity
            amp *= gain

        out_x[i] = wx
        out_y[i] = wy

    return out_x, out_y


@njit(parallel=True, fastmath=True, cache=True)
def domain_warp_basic_grid_fractal_progressive_2d(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    perm: NDArray[np.int32],
    frequency: float,
    amplitude: float,
    octaves: int,
    lacunarity: float,
    gain: float
) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Apply basic grid domain warp with progressive fractal.
    """
    n = len(x)
    out_x = x.copy()
    out_y = y.copy()

    for i in prange(n):
        wx = out_x[i]
        wy = out_y[i]

        freq = frequency
        amp = amplitude

        for _ in range(octaves):
            xs = wx * freq
            ys = wy * freq

            dx, dy = _basic_grid_warp_single(xs, ys, perm, amp)

            wx += dx * ROTATE_2D_COS - dy * ROTATE_2D_SIN
            wy += dx * ROTATE_2D_SIN + dy * ROTATE_2D_COS

            freq *= lacunarity
            amp *= gain

        out_x[i] = wx
        out_y[i] = wy

    return out_x, out_y


# ============================================================================
# JIT Kernels - Fractal Domain Warp (Independent)
# ============================================================================

@njit(parallel=True, fastmath=True, cache=True)
def domain_warp_simplex_fractal_independent_2d(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    perm: NDArray[np.int32],
    frequency: float,
    amplitude: float,
    octaves: int,
    lacunarity: float,
    gain: float
) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Apply simplex domain warp with independent fractal.
    Each octave samples from the original coordinates, summing offsets.

    Args:
        x: Array of X coordinates
        y: Array of Y coordinates
        perm: Permutation table
        frequency: Base warp frequency
        amplitude: Base warp amplitude
        octaves: Number of fractal octaves
        lacunarity: Frequency multiplier per octave
        gain: Amplitude multiplier per octave

    Returns:
        Tuple of (warped_x, warped_y) arrays
    """
    n = len(x)
    out_x = np.empty(n, dtype=np.float64)
    out_y = np.empty(n, dtype=np.float64)

    for i in prange(n):
        total_dx = 0.0
        total_dy = 0.0

        freq = frequency
        amp = amplitude

        for _ in range(octaves):
            xs = x[i] * freq
            ys = y[i] * freq

            dx, dy = _simplex_warp_single(xs, ys, perm, amp)

            total_dx += dx
            total_dy += dy

            freq *= lacunarity
            amp *= gain

        out_x[i] = x[i] + total_dx
        out_y[i] = y[i] + total_dy

    return out_x, out_y


@njit(parallel=True, fastmath=True, cache=True)
def domain_warp_basic_grid_fractal_independent_2d(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    perm: NDArray[np.int32],
    frequency: float,
    amplitude: float,
    octaves: int,
    lacunarity: float,
    gain: float
) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Apply basic grid domain warp with independent fractal.
    """
    n = len(x)
    out_x = np.empty(n, dtype=np.float64)
    out_y = np.empty(n, dtype=np.float64)

    for i in prange(n):
        total_dx = 0.0
        total_dy = 0.0

        freq = frequency
        amp = amplitude

        for _ in range(octaves):
            xs = x[i] * freq
            ys = y[i] * freq

            dx, dy = _basic_grid_warp_single(xs, ys, perm, amp)

            total_dx += dx
            total_dy += dy

            freq *= lacunarity
            amp *= gain

        out_x[i] = x[i] + total_dx
        out_y[i] = y[i] + total_dy

    return out_x, out_y


# ============================================================================
# DomainWarp2D Class
# ============================================================================

class DomainWarp2D:
    """
    2D Domain Warp generator compatible with Godot FastNoiseLite.

    This class handles domain warping of coordinates before they are
    used for noise sampling, creating more organic and natural patterns.

    Attributes:
        enabled: Whether domain warp is active.
        warp_type: Type of warp algorithm (SIMPLEX, SIMPLEX_REDUCED, BASIC_GRID).
        amplitude: Strength of the warp effect.
        frequency: Frequency of the warp noise.
        fractal_type: Fractal mode (NONE, PROGRESSIVE, INDEPENDENT).
        fractal_octaves: Number of fractal octaves.
        fractal_lacunarity: Frequency multiplier per octave.
        fractal_gain: Amplitude multiplier per octave.
    """

    PERM_SIZE = 256

    def __init__(
        self,
        enabled: bool = False,
        warp_type: DomainWarpType = DomainWarpType.SIMPLEX,
        amplitude: float = 30.0,
        frequency: float = 0.05,
        fractal_type: DomainWarpFractalType = DomainWarpFractalType.NONE,
        fractal_octaves: int = 5,
        fractal_lacunarity: float = 2.0,
        fractal_gain: float = 0.5,
        seed: Optional[int] = None
    ) -> None:
        """
        Initialize the domain warp generator.

        Args:
            enabled: Whether domain warp is active.
            warp_type: Type of warp algorithm.
            amplitude: Strength of the warp effect.
            frequency: Frequency of the warp noise.
            fractal_type: Fractal mode for the warp.
            fractal_octaves: Number of fractal octaves.
            fractal_lacunarity: Frequency multiplier per octave.
            fractal_gain: Amplitude multiplier per octave.
            seed: Random seed for reproducibility.
        """
        self.enabled = enabled
        self.warp_type = warp_type
        self.amplitude = amplitude
        self.frequency = frequency
        self.fractal_type = fractal_type
        self.fractal_octaves = max(1, min(fractal_octaves, 9))
        self.fractal_lacunarity = fractal_lacunarity
        self.fractal_gain = fractal_gain

        # Initialize permutation table
        self._seed = seed
        self._rng = np.random.default_rng(seed)
        self._init_permutation_table()

    def _init_permutation_table(self) -> None:
        """Initialize the permutation table for hashing coordinates."""
        perm = np.arange(self.PERM_SIZE, dtype=np.int32)
        self._rng.shuffle(perm)
        self._permutation = np.concatenate([perm, perm]).astype(np.int32)

    @property
    def seed(self) -> Optional[int]:
        """Get the seed."""
        return self._seed

    @seed.setter
    def seed(self, value: Optional[int]) -> None:
        """Set the seed and reinitialize permutation table."""
        self._seed = value
        self._rng = np.random.default_rng(value)
        self._init_permutation_table()

    def warp_coordinates(
        self,
        x: NDArray[np.float64],
        y: NDArray[np.float64]
    ) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
        """
        Apply domain warp to coordinate arrays.

        Args:
            x: Array of X coordinates (will be flattened).
            y: Array of Y coordinates (will be flattened).

        Returns:
            Tuple of (warped_x, warped_y) arrays with same shape as input.
        """
        if not self.enabled:
            return x, y

        original_shape = x.shape
        x_flat = x.ravel().astype(np.float64)
        y_flat = y.ravel().astype(np.float64)

        # Select warp function based on type and fractal mode
        if self.fractal_type == DomainWarpFractalType.NONE:
            warped_x, warped_y = self._warp_no_fractal(x_flat, y_flat)
        elif self.fractal_type == DomainWarpFractalType.PROGRESSIVE:
            warped_x, warped_y = self._warp_fractal_progressive(x_flat, y_flat)
        else:  # INDEPENDENT
            warped_x, warped_y = self._warp_fractal_independent(x_flat, y_flat)

        return warped_x.reshape(original_shape), warped_y.reshape(original_shape)

    def _warp_no_fractal(
        self,
        x: NDArray[np.float64],
        y: NDArray[np.float64]
    ) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
        """Apply single-octave domain warp."""
        if self.warp_type == DomainWarpType.BASIC_GRID:
            return domain_warp_basic_grid_2d(
                x, y, self._permutation, self.frequency, self.amplitude
            )
        else:  # SIMPLEX or SIMPLEX_REDUCED
            return domain_warp_simplex_2d(
                x, y, self._permutation, self.frequency, self.amplitude
            )

    def _warp_fractal_progressive(
        self,
        x: NDArray[np.float64],
        y: NDArray[np.float64]
    ) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
        """Apply progressive fractal domain warp."""
        if self.warp_type == DomainWarpType.BASIC_GRID:
            return domain_warp_basic_grid_fractal_progressive_2d(
                x, y, self._permutation,
                self.frequency, self.amplitude,
                self.fractal_octaves, self.fractal_lacunarity, self.fractal_gain
            )
        else:  # SIMPLEX or SIMPLEX_REDUCED
            return domain_warp_simplex_fractal_progressive_2d(
                x, y, self._permutation,
                self.frequency, self.amplitude,
                self.fractal_octaves, self.fractal_lacunarity, self.fractal_gain
            )

    def _warp_fractal_independent(
        self,
        x: NDArray[np.float64],
        y: NDArray[np.float64]
    ) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
        """Apply independent fractal domain warp."""
        if self.warp_type == DomainWarpType.BASIC_GRID:
            return domain_warp_basic_grid_fractal_independent_2d(
                x, y, self._permutation,
                self.frequency, self.amplitude,
                self.fractal_octaves, self.fractal_lacunarity, self.fractal_gain
            )
        else:  # SIMPLEX or SIMPLEX_REDUCED
            return domain_warp_simplex_fractal_independent_2d(
                x, y, self._permutation,
                self.frequency, self.amplitude,
                self.fractal_octaves, self.fractal_lacunarity, self.fractal_gain
            )

    def warp_single(self, x: float, y: float) -> Tuple[float, float]:
        """
        Apply domain warp to a single point.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Tuple of (warped_x, warped_y)
        """
        if not self.enabled:
            return x, y

        x_arr = np.array([x], dtype=np.float64)
        y_arr = np.array([y], dtype=np.float64)

        warped_x, warped_y = self.warp_coordinates(x_arr, y_arr)

        return float(warped_x[0]), float(warped_y[0])

    def to_dict(self) -> dict:
        """Convert domain warp configuration to a dictionary."""
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
        """
        Create a DomainWarp2D from a dictionary.

        Args:
            data: Dictionary with domain warp configuration.
            seed: Optional seed override.

        Returns:
            A new DomainWarp2D instance.
        """
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

