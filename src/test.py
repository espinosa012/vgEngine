"""
Test script for generating and visualizing 2D noise as a grayscale PNG image.
"""

import time
import numpy as np
from PIL import Image

from vgnoise import NoiseGenerator2D, PerlinNoise2D, OpenSimplexNoise2D


def generate_noise_image(
    width: int = 256,
    height: int = 256,
    scale: float = 1.0,
    seed: int | None = None,
    output_path: str = "noise.png"
) -> None:
    """
    Generate a 2D noise image and save it as a grayscale PNG.

    Light values represent low noise values (close to 0).
    Dark values represent high noise values (close to 1).

    Args:
        width: Width of the output image in pixels.
        height: Height of the output image in pixels.
        scale: Scale factor for the noise coordinates.
        seed: Optional random seed for reproducibility.
        output_path: Path to save the output PNG file.
    """
    # Create the noise generator
    noise = NoiseGenerator2D(seed=seed)

    # Generate the noise region
    # Region format: [(start_x, end_x, num_points_x), (start_y, end_y, num_points_y)]
    region = [
        (0.0, scale, width),
        (0.0, scale, height)
    ]
    noise_data = noise.generate_region(region)

    # Invert values: low noise = light (255), high noise = dark (0)
    inverted_data = 1.0 - noise_data

    # Convert to 8-bit grayscale (0-255)
    image_data = (inverted_data * 255).astype(np.uint8)

    # Create and save the image
    image = Image.fromarray(image_data, mode='L')
    image.save(output_path)

    print(f"Noise image saved to: {output_path}")
    print(f"Image size: {width}x{height}")
    print(f"Noise scale: {scale}")
    if seed is not None:
        print(f"Seed: {seed}")


def generate_perlin_noise_image(
    width: int = 256,
    height: int = 256,
    frequency: float = 1.0,
    amplitude: float = 1.0,
    octaves: int = 4,
    persistence: float = 0.5,
    seed: int | None = None,
    output_path: str = "perlin_noise.png"
) -> None:
    """
    Generate a 2D Perlin noise image with octaves and save it as a grayscale PNG.

    Light values represent low noise values (close to 0).
    Dark values represent high noise values (close to 1).

    Args:
        width: Width of the output image in pixels.
        height: Height of the output image in pixels.
        frequency: Base frequency of the noise.
        amplitude: Base amplitude of the noise.
        octaves: Number of noise layers to combine.
        persistence: Amplitude multiplier for each successive octave.
        seed: Optional random seed for reproducibility.
        output_path: Path to save the output PNG file.
    """
    # Create the Perlin noise generator
    noise = PerlinNoise2D(
        frequency=frequency,
        amplitude=amplitude,
        octaves=octaves,
        persistence=persistence,
        seed=seed
    )

    # Generate the noise region
    region = [
        (0.0, 10.0, width),
        (0.0, 10.0, height)
    ]

    start_time = time.perf_counter()
    noise_data = noise.generate_region(region)
    elapsed_time = time.perf_counter() - start_time

    # Invert values: low noise = light (255), high noise = dark (0)
    inverted_data = 1.0 - noise_data

    # Convert to 8-bit grayscale (0-255)
    image_data = (inverted_data * 255).astype(np.uint8)

    # Create and save the image
    image = Image.fromarray(image_data, mode='L')
    image.save(output_path)

    print(f"Perlin noise image saved to: {output_path}")
    print(f"Image size: {width}x{height} ({width * height:,} pixels)")
    print(f"Generation time: {elapsed_time:.4f}s ({width * height / elapsed_time:,.0f} pixels/sec)")
    print(f"Frequency: {frequency}, Amplitude: {amplitude}")
    print(f"Octaves: {octaves}, Persistence: {persistence}")
    if seed is not None:
        print(f"Seed: {seed}")


def generate_opensimplex_noise_image(
    width: int = 256,
    height: int = 256,
    lacunarity: float = 2.0,
    octaves: int = 4,
    frequency: float = 1.0,
    persistence: float = 0.5,
    seed: int | None = None,
    output_path: str = "opensimplex_noise.png"
) -> None:
    """
    Generate a 2D OpenSimplex noise image with octaves and save it as a grayscale PNG.

    Light values represent low noise values (close to 0).
    Dark values represent high noise values (close to 1).

    Args:
        width: Width of the output image in pixels.
        height: Height of the output image in pixels.
        lacunarity: Frequency multiplier between octaves.
        octaves: Number of noise layers to combine (1-9).
        frequency: Base frequency of the noise. Higher values = more detail.
        persistence: Contribution factor for each successive octave.
        seed: Optional random seed for reproducibility.
        output_path: Path to save the output PNG file.
    """
    # Create the OpenSimplex noise generator
    noise = OpenSimplexNoise2D(
        lacunarity=lacunarity,
        octaves=octaves,
        frequency=frequency,
        persistence=persistence,
        seed=seed
    )

    # Generate the noise region
    region = [
        (0.0, 10.0, width),
        (0.0, 10.0, height)
    ]

    start_time = time.perf_counter()
    noise_data = noise.generate_region(region)
    elapsed_time = time.perf_counter() - start_time

    # Invert values: low noise = light (255), high noise = dark (0)
    inverted_data = 1.0 - noise_data

    # Convert to 8-bit grayscale (0-255)
    image_data = (inverted_data * 255).astype(np.uint8)

    # Create and save the image
    image = Image.fromarray(image_data, mode='L')
    image.save(output_path)

    print(f"OpenSimplex noise image saved to: {output_path}")
    print(f"Image size: {width}x{height} ({width * height:,} pixels)")
    print(f"Generation time: {elapsed_time:.4f}s ({width * height / elapsed_time:,.0f} pixels/sec)")
    print(f"Lacunarity: {lacunarity}, Frequency: {frequency}")
    print(f"Octaves: {octaves}, Persistence: {persistence}")
    if seed is not None:
        print(f"Seed: {seed}")


if __name__ == "__main__":

    # Definir combinaciones de parámetros a probar
    opensimplex_cases = [
        # Variaciones de octavas
        {"lacunarity": 2.0, "octaves": 1, "frequency": 1.0, "persistence": 0.5, "name": "oct_1"},
        {"lacunarity": 2.0, "octaves": 4, "frequency": 1.0, "persistence": 0.5, "name": "oct_4"},
        {"lacunarity": 2.0, "octaves": 6, "frequency": 1.0, "persistence": 0.5, "name": "oct_6"},

        # Variaciones de frequency
        {"lacunarity": 2.0, "octaves": 4, "frequency": 0.5, "persistence": 0.5, "name": "freq_0.5"},
        {"lacunarity": 2.0, "octaves": 4, "frequency": 2.0, "persistence": 0.5, "name": "freq_2.0"},

        # Variaciones de lacunarity
        {"lacunarity": 1.5, "octaves": 4, "frequency": 1.0, "persistence": 0.5, "name": "lac_1.5"},
        {"lacunarity": 3.0, "octaves": 4, "frequency": 1.0, "persistence": 0.5, "name": "lac_3.0"},

        # Variaciones de persistence
        {"lacunarity": 2.0, "octaves": 6, "frequency": 1.0, "persistence": 0.3, "name": "pers_0.3"},
        {"lacunarity": 2.0, "octaves": 6, "frequency": 1.0, "persistence": 0.7, "name": "pers_0.7"},

        # Combinaciones interesantes
        {"lacunarity": 2.0, "octaves": 6, "frequency": 2.0, "persistence": 0.6, "name": "terrain_like"},
        {"lacunarity": 2.5, "octaves": 3, "frequency": 0.5, "persistence": 0.3, "name": "smooth_clouds"},
    ]

    for params in opensimplex_cases:
        generate_opensimplex_noise_image(
            width=256,
            height=256,
            lacunarity=params["lacunarity"],
            octaves=params["octaves"],
            frequency=params["frequency"],
            persistence=params["persistence"],
            seed=42,
            output_path=f"opensimplex_{params['name']}.png"
        )
        print()

