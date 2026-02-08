# vgNoise Viewer

A visual noise generator tool with a graphical interface for experimenting with procedural noise generation. Compatible with Godot's FastNoiseLite parameters.

## Features

- Real-time noise visualization
- Support for Perlin and OpenSimplex noise algorithms
- All Godot FastNoiseLite fractal types (FBM, Ridged, Ping-Pong)
- Dark theme UI with custom stepper controls
- High-performance Numba JIT acceleration

## Architecture

The viewer is built with a modular architecture:

```
vgNoiseViewer/
├── app.py              # Main application class (NoiseViewer)
├── config.py           # Configuration dataclasses and constants
├── theme.py            # ThemeManager for UI styling
├── widgets.py          # Reusable UI components (StepperControl, Card, etc.)
├── noise_factory.py    # NoiseGeneratorFactory and NoiseParameters
├── image_utils.py      # ImageGenerator and NoiseImageRenderer
├── test_app.py         # Comprehensive test suite (67 tests)
└── __init__.py         # Package exports
```

### Key Components

- **NoiseViewer**: Main application class managing UI and coordination
- **ThemeManager**: Handles dark theme styling for ttk widgets
- **NoiseGeneratorFactory**: Factory pattern for creating noise generators
- **NoiseParameters**: Data container for noise generation parameters
- **NoiseImageRenderer**: Converts noise data to displayable images
- **StepperControl**: Custom widget with +/- buttons for numeric input
- **Card**: Styled container widget for parameter groups

## Installation

```bash
pip install -r requirements.txt
```

Note: Tkinter comes pre-installed with Python on most systems.

## Usage

```bash
python app.py
```

## Running Tests

```bash
python -m pytest test_app.py -v
```

## Parameters

### Basic Parameters
- **Seed**: Random seed for reproducible results
- **Noise Type**: PERLIN or SIMPLEX algorithm
- **Frequency**: Base frequency (detail level)
- **Offset X/Y**: Domain offset for panning

### Fractal Parameters
- **Fractal Type**: NONE, FBM, RIDGED, or PING_PONG
- **Octaves**: Number of noise layers (1-9)
- **Lacunarity**: Frequency multiplier per octave
- **Persistence**: Amplitude multiplier per octave
- **Weighted Strength**: Octave weighting based on previous value
- **Ping Pong Strength**: Strength of ping-pong effect

### Image Settings
- **Image Size**: 128, 256, 512, or 1024 pixels

## Requirements

- Python 3.10+
- tkinter
- PIL/Pillow
- numpy
- numba
- vgnoise (parent package)
