"""
Color class for working with RGB and hexadecimal colors.
"""

from typing import Union, Tuple, List


class Color:
    """
    A class for working with colors in RGB and hexadecimal formats.

    Attributes:
        r: Red component (0-255).
        g: Green component (0-255).
        b: Blue component (0-255).
        a: Alpha component for transparency (0-255), default 255 (opaque).
    """

    def __init__(
        self,
        *args,
        **kwargs
    ):
        """
        Initialize a Color object.

        Args:
            Can be called in multiple ways:
            - Color(r, g, b): RGB values (0-255)
            - Color(r, g, b, a): RGB + Alpha values (0-255)
            - Color("#RRGGBB"): Hexadecimal string
            - Color("#RRGGBBAA"): Hexadecimal string with alpha
            - Color(r=r, g=g, b=b, a=a): Named parameters

        Raises:
            ValueError: If invalid arguments are provided.
        """
        self.r: int = 0
        self.g: int = 0
        self.b: int = 0
        self.a: int = 255

        # Parse arguments
        if len(args) == 1 and isinstance(args[0], str):
            # Hexadecimal string format
            self._parse_hex(args[0])
        elif len(args) == 3:
            # RGB format
            self.r, self.g, self.b = args
            self._validate_components()
        elif len(args) == 4:
            # RGBA format
            self.r, self.g, self.b, self.a = args
            self._validate_components()
        elif kwargs:
            # Named parameters
            self.r = kwargs.get('r', 0)
            self.g = kwargs.get('g', 0)
            self.b = kwargs.get('b', 0)
            self.a = kwargs.get('a', 255)
            self._validate_components()
        elif len(args) == 0:
            # Default: black
            pass
        else:
            raise ValueError(
                "Invalid arguments. Use Color(r, g, b[, a]) or Color('#RRGGBB[AA]')"
            )

    def _parse_hex(self, hex_string: str) -> None:
        """
        Parse a hexadecimal color string.

        Args:
            hex_string: Hex color string (e.g., "#FF0000" or "#FF0000FF").

        Raises:
            ValueError: If the hex string is invalid.
        """
        if not hex_string.startswith('#'):
            raise ValueError("Hexadecimal color must start with '#'")

        hex_string = hex_string[1:]  # Remove '#'

        if len(hex_string) == 6:
            # RGB format
            self.r = int(hex_string[0:2], 16)
            self.g = int(hex_string[2:4], 16)
            self.b = int(hex_string[4:6], 16)
            self.a = 255
        elif len(hex_string) == 8:
            # RGBA format
            self.r = int(hex_string[0:2], 16)
            self.g = int(hex_string[2:4], 16)
            self.b = int(hex_string[4:6], 16)
            self.a = int(hex_string[6:8], 16)
        else:
            raise ValueError(
                "Hexadecimal color must be 6 or 8 characters long (excluding '#')"
            )

    def _validate_components(self) -> None:
        """
        Validate that all color components are in the valid range (0-255).

        Raises:
            ValueError: If any component is out of range.
        """
        for name, value in [('r', self.r), ('g', self.g), ('b', self.b), ('a', self.a)]:
            if not isinstance(value, int) or not 0 <= value <= 255:
                raise ValueError(f"Component '{name}' must be an integer between 0 and 255")

    def to_rgb(self) -> Tuple[int, int, int]:
        """
        Get RGB components as a tuple.

        Returns:
            Tuple of (r, g, b).
        """
        return (self.r, self.g, self.b)

    def to_rgba(self) -> Tuple[int, int, int, int]:
        """
        Get RGBA components as a tuple.

        Returns:
            Tuple of (r, g, b, a).
        """
        return (self.r, self.g, self.b, self.a)

    def to_hex(self, include_alpha: bool = False) -> str:
        """
        Convert color to hexadecimal string.

        Args:
            include_alpha: If True, include alpha channel (default: False).

        Returns:
            Hexadecimal color string (e.g., "#FF0000" or "#FF0000FF").
        """
        if include_alpha:
            return f"#{self.r:02X}{self.g:02X}{self.b:02X}{self.a:02X}"
        else:
            return f"#{self.r:02X}{self.g:02X}{self.b:02X}"

    def to_normalized(self) -> Tuple[float, float, float, float]:
        """
        Get normalized color components (0.0 - 1.0).

        Returns:
            Tuple of (r, g, b, a) with values between 0.0 and 1.0.
        """
        return (
            self.r / 255.0,
            self.g / 255.0,
            self.b / 255.0,
            self.a / 255.0
        )

    def copy(self) -> 'Color':
        """
        Create a copy of this color.

        Returns:
            A new Color instance with the same values.
        """
        return Color(self.r, self.g, self.b, self.a)

    @staticmethod
    def get_color_scale(
        init_color: 'Color',
        final_color: 'Color',
        nsteps: int
    ) -> List['Color']:
        """
        Create a linear color scale between two colors.

        Args:
            init_color: Starting color.
            final_color: Ending color.
            nsteps: Number of steps in the scale (must be >= 2).

        Returns:
            List of Color objects representing the color scale.

        Raises:
            ValueError: If nsteps < 2.
        """
        if nsteps < 2:
            raise ValueError("nsteps must be at least 2")

        colors = []

        for i in range(nsteps):
            # Calculate interpolation factor (0.0 to 1.0)
            t = i / (nsteps - 1)

            # Linear interpolation for each component
            r = int(init_color.r + (final_color.r - init_color.r) * t)
            g = int(init_color.g + (final_color.g - init_color.g) * t)
            b = int(init_color.b + (final_color.b - init_color.b) * t)
            a = int(init_color.a + (final_color.a - init_color.a) * t)

            colors.append(Color(r, g, b, a))

        return colors

    def __repr__(self) -> str:
        """String representation of the color."""
        return f"Color(r={self.r}, g={self.g}, b={self.b}, a={self.a})"

    def __str__(self) -> str:
        """String representation showing hex value."""
        return self.to_hex(include_alpha=self.a != 255)

    def __eq__(self, other: object) -> bool:
        """Check equality with another Color."""
        if not isinstance(other, Color):
            return False
        return (
            self.r == other.r and
            self.g == other.g and
            self.b == other.b and
            self.a == other.a
        )

    def __hash__(self) -> int:
        """Make Color hashable."""
        return hash((self.r, self.g, self.b, self.a))


# Common color constants
class Colors:
    """Common color constants."""
    BLACK = Color(0, 0, 0)
    WHITE = Color(255, 255, 255)
    RED = Color(255, 0, 0)
    GREEN = Color(0, 255, 0)
    BLUE = Color(0, 0, 255)
    YELLOW = Color(255, 255, 0)
    CYAN = Color(0, 255, 255)
    MAGENTA = Color(255, 0, 255)
    TRANSPARENT = Color(0, 0, 0, 0)

