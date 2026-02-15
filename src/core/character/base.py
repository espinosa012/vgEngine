from core.base.game_object import GameObject


class BaseCharacter(GameObject):
    """
    Base class for all character entities (player, enemies, NPCs).
    Inherits from GameObject and adds character-specific functionality.
    """

    def __init__(self, x: float = 0, y: float = 0, name: str = None):
        """
        Initialize a character.

        Args:
            x: Initial x position
            y: Initial y position
            name: Optional name for the character
        """
        super().__init__(x, y, name)

        # Character-specific properties
        self.health: float = 100.0
        self.max_health: float = 100.0
        self.speed: float = 100.0  # pixels per second

        # Movement
        self.velocity_x: float = 0.0
        self.velocity_y: float = 0.0

        # State
        self.facing_direction: str = "right"  # "left", "right", "up", "down"
        self.is_moving: bool = False

    def update(self, delta_time: float):
        """
        Update character state.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        # Apply velocity
        if self.velocity_x != 0 or self.velocity_y != 0:
            self.translate(self.velocity_x * delta_time, self.velocity_y * delta_time)
            self.is_moving = True
        else:
            self.is_moving = False

    def render(self, renderer):
        """
        Render the character.
        Override this in subclasses for specific rendering.

        Args:
            renderer: Renderer object to draw with
        """
        pass

    def take_damage(self, amount: float):
        """
        Apply damage to the character.

        Args:
            amount: Damage amount
        """
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.on_death()

    def heal(self, amount: float):
        """
        Heal the character.

        Args:
            amount: Heal amount
        """
        self.health = min(self.max_health, self.health + amount)

    def move(self, direction_x: float, direction_y: float):
        """
        Set movement velocity based on direction.

        Args:
            direction_x: Horizontal direction (-1 to 1)
            direction_y: Vertical direction (-1 to 1)
        """
        self.velocity_x = direction_x * self.speed
        self.velocity_y = direction_y * self.speed

        # Update facing direction
        if direction_x > 0:
            self.facing_direction = "right"
        elif direction_x < 0:
            self.facing_direction = "left"
        elif direction_y > 0:
            self.facing_direction = "down"
        elif direction_y < 0:
            self.facing_direction = "up"

    def stop(self):
        """Stop character movement."""
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.is_moving = False

    def on_death(self):
        """
        Called when character health reaches 0.
        Override for custom death behavior.
        """
        self.destroy()

    @property
    def is_alive(self) -> bool:
        """Check if character is alive."""
        return self.health > 0 and not self.destroyed

