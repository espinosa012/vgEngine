"""
UI Framework Demo - Complete example showcasing all components.

This demo demonstrates:
- All widget types (Label, Button, Checkbox, Slider, TextInput, etc.)
- Layout containers (VBox, HBox, Grid)
- Event handling
- UIManager usage
- Custom colors
"""

import pygame
import sys

# Add src to path
sys.path.insert(0, '/Users/espinosa025/Documents/virigir/vgEngine')

from src.ui import (
    UIManager,
    Label,
    Button,
    Panel,
    Checkbox,
    Slider,
    TextInput,
    VBox,
    HBox,
    Grid
)


class UIDemo:
    """UI Framework demonstration."""

    def __init__(self):
        pygame.init()

        # Screen setup
        self.screen_width = 1024
        self.screen_height = 768
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("vgEngine UI Framework Demo")

        # Clock
        self.clock = pygame.time.Clock()
        self.running = True

        # UI Manager
        self.ui = UIManager(self.screen_width, self.screen_height)

        # Setup UI
        self._create_ui()

    def _create_ui(self):
        """Create the demo UI."""

        # Main container
        main_panel = Panel(
            x=20, y=20,
            width=self.screen_width - 40,
            height=self.screen_height - 40,
            bg_color=(40, 40, 40),
            border_width=2,
            border_radius=8,
            padding=20
        )
        self.ui.add(main_panel)

        # Title
        title = Label(
            x=0, y=0,
            text="vgEngine UI Framework Demo",
            font_size=28,
            bold=True
        )
        main_panel.add_child(title)

        # Demo sections in a grid
        grid = Grid(
            x=0, y=50,
            width=main_panel.content_width,
            height=main_panel.content_height - 50,
            columns=3,
            spacing_x=20,
            spacing_y=20,
            padding=0
        )
        main_panel.add_child(grid)

        # Section 1: Buttons and Labels
        section1 = self._create_buttons_section()
        grid.add_child(section1)

        # Section 2: Inputs
        section2 = self._create_inputs_section()
        grid.add_child(section2)

        # Section 3: Sliders and Checkboxes
        section3 = self._create_controls_section()
        grid.add_child(section3)

        # Section 4: VBox example
        section4 = self._create_vbox_section()
        grid.add_child(section4)

        # Section 5: HBox example
        section5 = self._create_hbox_section()
        grid.add_child(section5)

        # Section 6: Color examples
        section6 = self._create_color_section()
        grid.add_child(section6)

    def _create_buttons_section(self) -> Panel:
        """Create buttons demo section."""
        panel = Panel(
            width=250, height=200,
            bg_color=(50, 50, 50),
            border_width=1,
            border_radius=4,
            padding=10
        )

        vbox = VBox(spacing=10, align='stretch')
        panel.add_child(vbox)

        vbox.add_child(Label(text="Buttons", font_size=18, bold=True))

        btn1 = Button(
            text="Click Me!",
            height=36
        ).on_click(lambda btn: print("Button 1 clicked!"))
        vbox.add_child(btn1)

        btn2 = Button(
            text="Disabled",
            height=36
        )
        btn2.enabled = False
        vbox.add_child(btn2)

        btn3 = Button(
            text="Success",
            height=36,
            bg_color=(76, 175, 80)
        ).on_click(lambda btn: print("Success!"))
        vbox.add_child(btn3)

        return panel

    def _create_inputs_section(self) -> Panel:
        """Create text inputs demo section."""
        panel = Panel(
            width=250, height=200,
            bg_color=(50, 50, 50),
            border_width=1,
            border_radius=4,
            padding=10
        )

        vbox = VBox(spacing=10, align='stretch')
        panel.add_child(vbox)

        vbox.add_child(Label(text="Text Inputs", font_size=18, bold=True))

        input1 = TextInput(
            placeholder="Enter your name...",
            height=32
        ).on_change(lambda ti: print(f"Name: {ti.text}"))
        vbox.add_child(input1)

        input2 = TextInput(
            text="Default value",
            height=32
        ).on_submit(lambda ti: print(f"Submitted: {ti.text}"))
        vbox.add_child(input2)

        input3 = TextInput(
            placeholder="Max 10 chars",
            max_length=10,
            height=32
        )
        vbox.add_child(input3)

        return panel

    def _create_controls_section(self) -> Panel:
        """Create sliders and checkboxes section."""
        panel = Panel(
            width=250, height=200,
            bg_color=(50, 50, 50),
            border_width=1,
            border_radius=4,
            padding=10
        )

        vbox = VBox(spacing=10, align='stretch')
        panel.add_child(vbox)

        vbox.add_child(Label(text="Controls", font_size=18, bold=True))

        # Slider
        slider = Slider(
            height=30,
            min_value=0,
            max_value=100,
            value=50,
            show_value=True
        ).on_change(lambda s: print(f"Slider: {s.value}"))
        vbox.add_child(slider)

        # Checkboxes
        cb1 = Checkbox(
            text="Option 1",
            checked=True
        ).on_change(lambda cb: print(f"Option 1: {cb.checked}"))
        vbox.add_child(cb1)

        cb2 = Checkbox(
            text="Option 2"
        ).on_change(lambda cb: print(f"Option 2: {cb.checked}"))
        vbox.add_child(cb2)

        cb3 = Checkbox(
            text="Disabled",
            checked=False
        )
        cb3.enabled = False
        vbox.add_child(cb3)

        return panel

    def _create_vbox_section(self) -> Panel:
        """Create VBox layout demo."""
        panel = Panel(
            width=250, height=200,
            bg_color=(50, 50, 50),
            border_width=1,
            border_radius=4,
            padding=10
        )

        vbox = VBox(spacing=8, align='center')
        panel.add_child(vbox)

        vbox.add_child(Label(text="VBox Layout", font_size=18, bold=True))
        vbox.add_child(Label(text="Centered items", color=(180, 180, 180)))

        for i in range(1, 4):
            btn = Button(
                text=f"Item {i}",
                width=150,
                height=30
            )
            vbox.add_child(btn)

        return panel

    def _create_hbox_section(self) -> Panel:
        """Create HBox layout demo."""
        panel = Panel(
            width=250, height=200,
            bg_color=(50, 50, 50),
            border_width=1,
            border_radius=4,
            padding=10
        )

        # Title
        title = Label(text="HBox Layout", font_size=18, bold=True)
        title.x = 0
        title.y = 0
        panel.add_child(title)

        # HBox container
        hbox = HBox(
            y=40,
            spacing=8,
            align='center',
            height=40
        )
        panel.add_child(hbox)

        for i in range(1, 4):
            btn = Button(
                text=f"B{i}",
                width=60,
                height=32
            )
            hbox.add_child(btn)

        # Another HBox
        hbox2 = HBox(
            y=100,
            spacing=5,
            align='center',
            height=30
        )
        panel.add_child(hbox2)

        colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255)]
        for color in colors:
            btn = Button(
                text="●",
                width=40,
                height=28,
                bg_color=color
            )
            hbox2.add_child(btn)

        return panel

    def _create_color_section(self) -> Panel:
        """Create color examples section."""
        panel = Panel(
            width=250, height=200,
            bg_color=(50, 50, 50),
            border_width=1,
            border_radius=4,
            padding=10
        )

        vbox = VBox(spacing=10, align='stretch')
        panel.add_child(vbox)

        vbox.add_child(Label(text="Color Examples", font_size=18, bold=True))

        # Colored buttons
        btn_red = Button(
            text="Red Button",
            height=32,
            bg_color=(220, 60, 60),
            hover_color=(255, 80, 80)
        ).on_click(lambda btn: print("Red!"))
        vbox.add_child(btn_red)

        btn_green = Button(
            text="Green Button",
            height=32,
            bg_color=(76, 175, 80),
            hover_color=(100, 200, 100)
        ).on_click(lambda btn: print("Green!"))
        vbox.add_child(btn_green)

        btn_purple = Button(
            text="Purple Button",
            height=32,
            bg_color=(156, 39, 176),
            hover_color=(186, 69, 206)
        ).on_click(lambda btn: print("Purple!"))
        vbox.add_child(btn_purple)

        return panel

    def run(self):
        """Main game loop."""
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(60) / 1000.0

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

                # UI event handling
                self.ui.handle_event(event)

            # Update
            self.ui.update(dt)

            # Draw
            self.screen.fill((20, 20, 20))
            self.ui.draw(self.screen)

            # FPS counter
            fps = int(self.clock.get_fps())
            font = pygame.font.Font(None, 24)
            fps_text = font.render(f"FPS: {fps}", True, (100, 255, 100))
            self.screen.blit(fps_text, (10, 10))

            pygame.display.flip()

        pygame.quit()


if __name__ == '__main__':
    demo = UIDemo()
    demo.run()

