"""
Numba JIT-compiled noise generation kernels.

This module contains optimized noise generation functions using Numba
for maximum performance through JIT compilation and parallelization.
"""

import numpy as np
from numba import njit, prange
from numpy.typing import NDArray


@njit(fastmath=True)
def _fade(t: float) -> float:
    """Smoothstep fade function (quintic)."""
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


@njit(parallel=True, fastmath=True, cache=True)
def perlin_fbm_2d(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    perm: NDArray[np.int32],
    grads: NDArray[np.float64],
    octaves: int,
    lacunarity: float,
    persistence: float,
    fractal_bounding: float
) -> NDArray[np.float64]:
    """
    Generate 2D Perlin FBM noise using parallel JIT compilation.

    Args:
        x: Flattened array of X coordinates (with frequency applied).
        y: Flattened array of Y coordinates (with frequency applied).
        perm: Permutation table (512 elements).
        grads: Gradient vectors (8x2).
        octaves: Number of octaves.
        lacunarity: Frequency multiplier per octave.
        persistence: Amplitude multiplier per octave.
        fractal_bounding: Normalization factor.

    Returns:
        Array of noise values normalized to [0, 1].
    """
    n = len(x)
    result = np.zeros(n, dtype=np.float64)

    for i in prange(n):
        xi = x[i]
        yi = y[i]
        total = 0.0
        amp = 1.0

        for _ in range(octaves):
            # Get integer and fractional parts
            floor_x = np.floor(xi)
            floor_y = np.floor(yi)
            xf = xi - floor_x
            yf = yi - floor_y

            ix = int(floor_x) & 255
            iy = int(floor_y) & 255
            ix1 = (ix + 1) & 255
            iy1 = (iy + 1) & 255

            # Fade curves
            u = xf * xf * xf * (xf * (xf * 6.0 - 15.0) + 10.0)
            v = yf * yf * yf * (yf * (yf * 6.0 - 15.0) + 10.0)

            # Hash coordinates
            h00 = perm[perm[ix] + iy] & 7
            h10 = perm[perm[ix1] + iy] & 7
            h01 = perm[perm[ix] + iy1] & 7
            h11 = perm[perm[ix1] + iy1] & 7

            # Gradient dot products
            n00 = grads[h00, 0] * xf + grads[h00, 1] * yf
            n10 = grads[h10, 0] * (xf - 1.0) + grads[h10, 1] * yf
            n01 = grads[h01, 0] * xf + grads[h01, 1] * (yf - 1.0)
            n11 = grads[h11, 0] * (xf - 1.0) + grads[h11, 1] * (yf - 1.0)

            # Bilinear interpolation
            nx0 = n00 + u * (n10 - n00)
            nx1 = n01 + u * (n11 - n01)
            noise = nx0 + v * (nx1 - nx0)

            total += noise * amp
            amp *= persistence
            xi *= lacunarity
            yi *= lacunarity

        result[i] = total * fractal_bounding * 0.5 + 0.5

    return result


@njit(parallel=True, fastmath=True, cache=True)
def perlin_fbm_2d_weighted(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    perm: NDArray[np.int32],
    grads: NDArray[np.float64],
    octaves: int,
    lacunarity: float,
    persistence: float,
    weighted_strength: float,
    fractal_bounding: float
) -> NDArray[np.float64]:
    """
    Generate 2D Perlin FBM noise with weighted strength.
    """
    n = len(x)
    result = np.zeros(n, dtype=np.float64)

    for i in prange(n):
        xi = x[i]
        yi = y[i]
        total = 0.0
        amp = 1.0

        for _ in range(octaves):
            floor_x = np.floor(xi)
            floor_y = np.floor(yi)
            xf = xi - floor_x
            yf = yi - floor_y

            ix = int(floor_x) & 255
            iy = int(floor_y) & 255
            ix1 = (ix + 1) & 255
            iy1 = (iy + 1) & 255

            u = xf * xf * xf * (xf * (xf * 6.0 - 15.0) + 10.0)
            v = yf * yf * yf * (yf * (yf * 6.0 - 15.0) + 10.0)

            h00 = perm[perm[ix] + iy] & 7
            h10 = perm[perm[ix1] + iy] & 7
            h01 = perm[perm[ix] + iy1] & 7
            h11 = perm[perm[ix1] + iy1] & 7

            n00 = grads[h00, 0] * xf + grads[h00, 1] * yf
            n10 = grads[h10, 0] * (xf - 1.0) + grads[h10, 1] * yf
            n01 = grads[h01, 0] * xf + grads[h01, 1] * (yf - 1.0)
            n11 = grads[h11, 0] * (xf - 1.0) + grads[h11, 1] * (yf - 1.0)

            nx0 = n00 + u * (n10 - n00)
            nx1 = n01 + u * (n11 - n01)
            noise = nx0 + v * (nx1 - nx0)

            total += noise * amp
            # Apply weighted strength
            amp *= (1.0 - weighted_strength + weighted_strength * (noise + 1.0) * 0.5) * persistence
            xi *= lacunarity
            yi *= lacunarity

        result[i] = total * fractal_bounding * 0.5 + 0.5

    return result


@njit(parallel=True, fastmath=True, cache=True)
def perlin_ridged_2d(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    perm: NDArray[np.int32],
    grads: NDArray[np.float64],
    octaves: int,
    lacunarity: float,
    persistence: float,
    weighted_strength: float,
    fractal_bounding: float
) -> NDArray[np.float64]:
    """
    Generate 2D ridged multifractal noise.
    """
    n = len(x)
    result = np.zeros(n, dtype=np.float64)

    for i in prange(n):
        xi = x[i]
        yi = y[i]
        total = 0.0
        amp = 1.0

        for _ in range(octaves):
            floor_x = np.floor(xi)
            floor_y = np.floor(yi)
            xf = xi - floor_x
            yf = yi - floor_y

            ix = int(floor_x) & 255
            iy = int(floor_y) & 255
            ix1 = (ix + 1) & 255
            iy1 = (iy + 1) & 255

            u = xf * xf * xf * (xf * (xf * 6.0 - 15.0) + 10.0)
            v = yf * yf * yf * (yf * (yf * 6.0 - 15.0) + 10.0)

            h00 = perm[perm[ix] + iy] & 7
            h10 = perm[perm[ix1] + iy] & 7
            h01 = perm[perm[ix] + iy1] & 7
            h11 = perm[perm[ix1] + iy1] & 7

            n00 = grads[h00, 0] * xf + grads[h00, 1] * yf
            n10 = grads[h10, 0] * (xf - 1.0) + grads[h10, 1] * yf
            n01 = grads[h01, 0] * xf + grads[h01, 1] * (yf - 1.0)
            n11 = grads[h11, 0] * (xf - 1.0) + grads[h11, 1] * (yf - 1.0)

            nx0 = n00 + u * (n10 - n00)
            nx1 = n01 + u * (n11 - n01)
            noise_raw = nx0 + v * (nx1 - nx0)

            # Ridged: abs and invert
            noise = 1.0 - abs(noise_raw)
            total += noise * amp

            # Apply weighted strength
            if weighted_strength > 0:
                amp *= (1.0 - weighted_strength + weighted_strength * noise) * persistence
            else:
                amp *= persistence

            xi *= lacunarity
            yi *= lacunarity

        result[i] = total * fractal_bounding

    return result


@njit(fastmath=True)
def _ping_pong(t: float) -> float:
    """Ping-pong function for terraced effects."""
    t = t - int(t * 0.5) * 2
    if t < 1.0:
        return t
    return 2.0 - t


@njit(parallel=True, fastmath=True, cache=True)
def perlin_pingpong_2d(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    perm: NDArray[np.int32],
    grads: NDArray[np.float64],
    octaves: int,
    lacunarity: float,
    persistence: float,
    weighted_strength: float,
    ping_pong_strength: float,
    fractal_bounding: float
) -> NDArray[np.float64]:
    """
    Generate 2D ping-pong fractal noise.
    """
    n = len(x)
    result = np.zeros(n, dtype=np.float64)

    for i in prange(n):
        xi = x[i]
        yi = y[i]
        total = 0.0
        amp = 1.0

        for _ in range(octaves):
            floor_x = np.floor(xi)
            floor_y = np.floor(yi)
            xf = xi - floor_x
            yf = yi - floor_y

            ix = int(floor_x) & 255
            iy = int(floor_y) & 255
            ix1 = (ix + 1) & 255
            iy1 = (iy + 1) & 255

            u = xf * xf * xf * (xf * (xf * 6.0 - 15.0) + 10.0)
            v = yf * yf * yf * (yf * (yf * 6.0 - 15.0) + 10.0)

            h00 = perm[perm[ix] + iy] & 7
            h10 = perm[perm[ix1] + iy] & 7
            h01 = perm[perm[ix] + iy1] & 7
            h11 = perm[perm[ix1] + iy1] & 7

            n00 = grads[h00, 0] * xf + grads[h00, 1] * yf
            n10 = grads[h10, 0] * (xf - 1.0) + grads[h10, 1] * yf
            n01 = grads[h01, 0] * xf + grads[h01, 1] * (yf - 1.0)
            n11 = grads[h11, 0] * (xf - 1.0) + grads[h11, 1] * (yf - 1.0)

            nx0 = n00 + u * (n10 - n00)
            nx1 = n01 + u * (n11 - n01)
            noise_raw = nx0 + v * (nx1 - nx0)

            # Ping-pong effect
            pp_val = (noise_raw + 1.0) * ping_pong_strength
            pp_val = pp_val - int(pp_val * 0.5) * 2
            if pp_val >= 1.0:
                pp_val = 2.0 - pp_val
            noise = pp_val

            total += (noise - 0.5) * 2.0 * amp

            # Apply weighted strength
            if weighted_strength > 0:
                amp *= (1.0 - weighted_strength + weighted_strength * noise) * persistence
            else:
                amp *= persistence

            xi *= lacunarity
            yi *= lacunarity

        result[i] = total * fractal_bounding * 0.5 + 0.5

    return result


@njit(parallel=True, fastmath=True, cache=True)
def perlin_single_2d(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    perm: NDArray[np.int32],
    grads: NDArray[np.float64]
) -> NDArray[np.float64]:
    """
    Generate single octave 2D Perlin noise (no fractal).
    """
    n = len(x)
    result = np.zeros(n, dtype=np.float64)

    for i in prange(n):
        xi = x[i]
        yi = y[i]

        floor_x = np.floor(xi)
        floor_y = np.floor(yi)
        xf = xi - floor_x
        yf = yi - floor_y

        ix = int(floor_x) & 255
        iy = int(floor_y) & 255
        ix1 = (ix + 1) & 255
        iy1 = (iy + 1) & 255

        u = xf * xf * xf * (xf * (xf * 6.0 - 15.0) + 10.0)
        v = yf * yf * yf * (yf * (yf * 6.0 - 15.0) + 10.0)

        h00 = perm[perm[ix] + iy] & 7
        h10 = perm[perm[ix1] + iy] & 7
        h01 = perm[perm[ix] + iy1] & 7
        h11 = perm[perm[ix1] + iy1] & 7

        n00 = grads[h00, 0] * xf + grads[h00, 1] * yf
        n10 = grads[h10, 0] * (xf - 1.0) + grads[h10, 1] * yf
        n01 = grads[h01, 0] * xf + grads[h01, 1] * (yf - 1.0)
        n11 = grads[h11, 0] * (xf - 1.0) + grads[h11, 1] * (yf - 1.0)

        nx0 = n00 + u * (n10 - n00)
        nx1 = n01 + u * (n11 - n01)
        noise = nx0 + v * (nx1 - nx0)

        result[i] = (noise + 1.0) * 0.5

    return result


# =============================================================================
# OpenSimplex 2D Kernels
# =============================================================================

# OpenSimplex 2D constants
STRETCH_2D = -0.211324865405187  # (1 / sqrt(2 + 1) - 1) / 2
SQUISH_2D = 0.366025403784439    # (sqrt(2 + 1) - 1) / 2
NORM_2D = 47.0


@njit(fastmath=True, cache=True)
def _opensimplex_extrapolate(
    perm: NDArray[np.int16],
    perm_grad_index: NDArray[np.int16],
    gradients: NDArray[np.float64],
    xsb: int,
    ysb: int,
    dx: float,
    dy: float
) -> float:
    """Calculate gradient contribution for a single point."""
    index = perm_grad_index[(perm[xsb & 255] + ysb) & 255]
    return gradients[index] * dx + gradients[index + 1] * dy


@njit(fastmath=True, cache=True)
def _opensimplex_sample(
    perm: NDArray[np.int16],
    perm_grad_index: NDArray[np.int16],
    gradients: NDArray[np.float64],
    x: float,
    y: float
) -> float:
    """Sample single OpenSimplex 2D noise value."""
    # Skew input
    s = (x + y) * STRETCH_2D
    xs = x + s
    ys = y + s

    # Floor to get base vertex
    xsb = int(np.floor(xs))
    ysb = int(np.floor(ys))

    # Unskew
    t = (xsb + ysb) * SQUISH_2D
    xb = xsb + t
    yb = ysb + t

    # Delta from base
    dx0 = x - xb
    dy0 = y - yb

    value = 0.0

    # Contribution (0, 0)
    attn0 = 2.0 - dx0 * dx0 - dy0 * dy0
    if attn0 > 0:
        attn0 *= attn0
        value += attn0 * attn0 * _opensimplex_extrapolate(
            perm, perm_grad_index, gradients, xsb, ysb, dx0, dy0
        )

    # Contribution (1, 0)
    dx1 = dx0 - 1.0 - SQUISH_2D
    dy1 = dy0 - SQUISH_2D
    attn1 = 2.0 - dx1 * dx1 - dy1 * dy1
    if attn1 > 0:
        attn1 *= attn1
        value += attn1 * attn1 * _opensimplex_extrapolate(
            perm, perm_grad_index, gradients, xsb + 1, ysb, dx1, dy1
        )

    # Contribution (0, 1)
    dx2 = dx0 - SQUISH_2D
    dy2 = dy0 - 1.0 - SQUISH_2D
    attn2 = 2.0 - dx2 * dx2 - dy2 * dy2
    if attn2 > 0:
        attn2 *= attn2
        value += attn2 * attn2 * _opensimplex_extrapolate(
            perm, perm_grad_index, gradients, xsb, ysb + 1, dx2, dy2
        )

    # Contribution (1, 1)
    dx3 = dx0 - 1.0 - 2.0 * SQUISH_2D
    dy3 = dy0 - 1.0 - 2.0 * SQUISH_2D
    attn3 = 2.0 - dx3 * dx3 - dy3 * dy3
    if attn3 > 0:
        attn3 *= attn3
        value += attn3 * attn3 * _opensimplex_extrapolate(
            perm, perm_grad_index, gradients, xsb + 1, ysb + 1, dx3, dy3
        )

    return value / NORM_2D


@njit(parallel=True, fastmath=True, cache=True)
def opensimplex_fbm_2d(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    perm: NDArray[np.int16],
    perm_grad_index: NDArray[np.int16],
    gradients: NDArray[np.float64],
    octaves: int,
    lacunarity: float,
    persistence: float,
    fractal_bounding: float
) -> NDArray[np.float64]:
    """Generate 2D OpenSimplex FBM noise using parallel JIT compilation."""
    n = len(x)
    result = np.zeros(n, dtype=np.float64)

    for i in prange(n):
        xi = x[i]
        yi = y[i]
        total = 0.0
        amp = 1.0

        for _ in range(octaves):
            noise = _opensimplex_sample(perm, perm_grad_index, gradients, xi, yi)
            total += noise * amp
            amp *= persistence
            xi *= lacunarity
            yi *= lacunarity

        result[i] = total * fractal_bounding * 0.5 + 0.5

    return result


@njit(parallel=True, fastmath=True, cache=True)
def opensimplex_fbm_2d_weighted(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    perm: NDArray[np.int16],
    perm_grad_index: NDArray[np.int16],
    gradients: NDArray[np.float64],
    octaves: int,
    lacunarity: float,
    persistence: float,
    weighted_strength: float,
    fractal_bounding: float
) -> NDArray[np.float64]:
    """Generate 2D OpenSimplex FBM noise with weighted strength."""
    n = len(x)
    result = np.zeros(n, dtype=np.float64)

    for i in prange(n):
        xi = x[i]
        yi = y[i]
        total = 0.0
        amp = 1.0

        for _ in range(octaves):
            noise = _opensimplex_sample(perm, perm_grad_index, gradients, xi, yi)
            total += noise * amp
            amp *= (1.0 - weighted_strength + weighted_strength * (noise + 1.0) * 0.5) * persistence
            xi *= lacunarity
            yi *= lacunarity

        result[i] = total * fractal_bounding * 0.5 + 0.5

    return result


@njit(parallel=True, fastmath=True, cache=True)
def opensimplex_ridged_2d(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    perm: NDArray[np.int16],
    perm_grad_index: NDArray[np.int16],
    gradients: NDArray[np.float64],
    octaves: int,
    lacunarity: float,
    persistence: float,
    weighted_strength: float,
    fractal_bounding: float
) -> NDArray[np.float64]:
    """Generate 2D OpenSimplex ridged multifractal noise."""
    n = len(x)
    result = np.zeros(n, dtype=np.float64)

    for i in prange(n):
        xi = x[i]
        yi = y[i]
        total = 0.0
        amp = 1.0

        for _ in range(octaves):
            noise_raw = _opensimplex_sample(perm, perm_grad_index, gradients, xi, yi)
            noise = 1.0 - abs(noise_raw)
            total += noise * amp

            if weighted_strength > 0:
                amp *= (1.0 - weighted_strength + weighted_strength * noise) * persistence
            else:
                amp *= persistence

            xi *= lacunarity
            yi *= lacunarity

        result[i] = total * fractal_bounding

    return result


@njit(parallel=True, fastmath=True, cache=True)
def opensimplex_pingpong_2d(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    perm: NDArray[np.int16],
    perm_grad_index: NDArray[np.int16],
    gradients: NDArray[np.float64],
    octaves: int,
    lacunarity: float,
    persistence: float,
    weighted_strength: float,
    ping_pong_strength: float,
    fractal_bounding: float
) -> NDArray[np.float64]:
    """Generate 2D OpenSimplex ping-pong fractal noise."""
    n = len(x)
    result = np.zeros(n, dtype=np.float64)

    for i in prange(n):
        xi = x[i]
        yi = y[i]
        total = 0.0
        amp = 1.0

        for _ in range(octaves):
            noise_raw = _opensimplex_sample(perm, perm_grad_index, gradients, xi, yi)

            # Ping-pong
            pp_val = (noise_raw + 1.0) * ping_pong_strength
            pp_val = pp_val - int(pp_val * 0.5) * 2
            if pp_val >= 1.0:
                pp_val = 2.0 - pp_val
            noise = pp_val

            total += (noise - 0.5) * 2.0 * amp

            if weighted_strength > 0:
                amp *= (1.0 - weighted_strength + weighted_strength * noise) * persistence
            else:
                amp *= persistence

            xi *= lacunarity
            yi *= lacunarity

        result[i] = total * fractal_bounding * 0.5 + 0.5

    return result


@njit(parallel=True, fastmath=True, cache=True)
def opensimplex_single_2d(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    perm: NDArray[np.int16],
    perm_grad_index: NDArray[np.int16],
    gradients: NDArray[np.float64]
) -> NDArray[np.float64]:
    """Generate single octave 2D OpenSimplex noise (no fractal)."""
    n = len(x)
    result = np.zeros(n, dtype=np.float64)

    for i in prange(n):
        noise = _opensimplex_sample(perm, perm_grad_index, gradients, x[i], y[i])
        result[i] = (noise + 1.0) * 0.5

    return result

