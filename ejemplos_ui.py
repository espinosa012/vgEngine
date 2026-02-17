"""
Ejemplos rápidos del framework UI de vgEngine.

Este archivo contiene ejemplos simples y directos para empezar
a usar el framework rápidamente.
"""

import pygame
import sys

sys.path.insert(0, '/Users/espinosa025/Documents/virigir/vgEngine')

from src.ui import (
    UIManager, Button, Label, Panel, VBox, HBox,
    Checkbox, Slider, TextInput, Grid
)


def ejemplo_1_basico():
    """Ejemplo 1: Ventana básica con un botón."""
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Ejemplo 1: Básico")
    clock = pygame.time.Clock()

    # Crear UI
    ui = UIManager(400, 300)

    button = Button(
        x=150, y=130,
        width=100, height=40,
        text="¡Haz clic!"
    ).on_click(lambda btn: print("¡Botón presionado!"))

    ui.add(button)

    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
               (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            ui.handle_event(event)

        ui.update(clock.tick(60) / 1000.0)

        screen.fill((30, 30, 30))
        ui.draw(screen)
        pygame.display.flip()

    pygame.quit()


def ejemplo_2_menu():
    """Ejemplo 2: Menú vertical con VBox."""
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    pygame.display.set_caption("Ejemplo 2: Menú VBox")
    clock = pygame.time.Clock()

    ui = UIManager(400, 400)

    # Crear menú con VBox
    menu = VBox(x=100, y=50, spacing=15, align='center')

    menu.add_child(Label(text="MENÚ PRINCIPAL", font_size=28, bold=True))
    menu.add_child(Button(text="Nueva Partida", width=200, height=40))
    menu.add_child(Button(text="Cargar Partida", width=200, height=40))
    menu.add_child(Button(text="Opciones", width=200, height=40))
    menu.add_child(Button(text="Salir", width=200, height=40).on_click(
        lambda btn: print("Salir presionado")
    ))

    ui.add(menu)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
               (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            ui.handle_event(event)

        ui.update(clock.tick(60) / 1000.0)

        screen.fill((30, 30, 30))
        ui.draw(screen)
        pygame.display.flip()

    pygame.quit()


def ejemplo_3_panel_con_inputs():
    """Ejemplo 3: Panel con inputs de texto y controles."""
    pygame.init()
    screen = pygame.display.set_mode((500, 400))
    pygame.display.set_caption("Ejemplo 3: Panel con Inputs")
    clock = pygame.time.Clock()

    ui = UIManager(500, 400)

    # Panel de formulario
    panel = Panel(
        x=50, y=50,
        width=400, height=300,
        bg_color=(50, 50, 50),
        border_width=2,
        border_radius=8,
        padding=20
    )
    ui.add(panel)

    # Contenido del panel
    vbox = VBox(spacing=15, align='stretch')
    panel.add_child(vbox)

    vbox.add_child(Label(text="Configuración de Usuario", font_size=20, bold=True))

    # Nombre
    vbox.add_child(Label(text="Nombre:", color=(200, 200, 200)))
    name_input = TextInput(
        placeholder="Ingresa tu nombre...",
        height=32
    ).on_change(lambda ti: print(f"Nombre: {ti.text}"))
    vbox.add_child(name_input)

    # Email
    vbox.add_child(Label(text="Email:", color=(200, 200, 200)))
    email_input = TextInput(
        placeholder="correo@ejemplo.com",
        height=32
    )
    vbox.add_child(email_input)

    # Checkboxes
    vbox.add_child(Checkbox(text="Recibir notificaciones", checked=True))
    vbox.add_child(Checkbox(text="Modo oscuro", checked=True))

    # Botón guardar
    save_btn = Button(
        text="Guardar",
        height=36,
        bg_color=(76, 175, 80)
    ).on_click(lambda btn: print("Guardado!"))
    vbox.add_child(save_btn)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
               (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            ui.handle_event(event)

        ui.update(clock.tick(60) / 1000.0)

        screen.fill((30, 30, 30))
        ui.draw(screen)
        pygame.display.flip()

    pygame.quit()


def ejemplo_4_sliders():
    """Ejemplo 4: Panel de ajustes con sliders."""
    pygame.init()
    screen = pygame.display.set_mode((500, 400))
    pygame.display.set_caption("Ejemplo 4: Sliders")
    clock = pygame.time.Clock()

    ui = UIManager(500, 400)

    panel = Panel(
        x=50, y=50,
        width=400, height=300,
        bg_color=(50, 50, 50),
        border_width=2,
        border_radius=8,
        padding=20
    )
    ui.add(panel)

    vbox = VBox(spacing=20, align='stretch')
    panel.add_child(vbox)

    vbox.add_child(Label(text="Ajustes de Audio", font_size=22, bold=True))

    # Volumen Master
    vbox.add_child(Label(text="Volumen Master", color=(200, 200, 200)))
    master_slider = Slider(
        height=30,
        min_value=0,
        max_value=100,
        value=75,
        show_value=True
    ).on_change(lambda s: print(f"Master: {s.value}"))
    vbox.add_child(master_slider)

    # Volumen Música
    vbox.add_child(Label(text="Volumen Música", color=(200, 200, 200)))
    music_slider = Slider(
        height=30,
        min_value=0,
        max_value=100,
        value=60,
        show_value=True
    ).on_change(lambda s: print(f"Música: {s.value}"))
    vbox.add_child(music_slider)

    # Volumen Efectos
    vbox.add_child(Label(text="Volumen Efectos", color=(200, 200, 200)))
    sfx_slider = Slider(
        height=30,
        min_value=0,
        max_value=100,
        value=80,
        show_value=True
    ).on_change(lambda s: print(f"Efectos: {s.value}"))
    vbox.add_child(sfx_slider)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
               (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            ui.handle_event(event)

        ui.update(clock.tick(60) / 1000.0)

        screen.fill((30, 30, 30))
        ui.draw(screen)
        pygame.display.flip()

    pygame.quit()


def ejemplo_5_grid():
    """Ejemplo 5: Grid de botones."""
    pygame.init()
    screen = pygame.display.set_mode((600, 500))
    pygame.display.set_caption("Ejemplo 5: Grid Layout")
    clock = pygame.time.Clock()

    ui = UIManager(600, 500)

    panel = Panel(
        x=50, y=50,
        width=500, height=400,
        bg_color=(50, 50, 50),
        border_width=2,
        border_radius=8,
        padding=20
    )
    ui.add(panel)

    # Título
    title = Label(text="Selecciona un nivel", font_size=24, bold=True)
    title.x = 150
    title.y = 10
    panel.add_child(title)

    # Grid de niveles
    grid = Grid(
        x=0, y=60,
        width=460, height=300,
        columns=4,
        rows=3,
        spacing_x=10,
        spacing_y=10
    )
    panel.add_child(grid)

    for i in range(12):
        btn = Button(
            text=f"Nivel {i+1}",
            width=100,
            height=80
        ).on_click(lambda b, level=i+1: print(f"Nivel {level} seleccionado"))
        grid.add_child(btn)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
               (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            ui.handle_event(event)

        ui.update(clock.tick(60) / 1000.0)

        screen.fill((30, 30, 30))
        ui.draw(screen)
        pygame.display.flip()

    pygame.quit()


def ejemplo_6_toolbar():
    """Ejemplo 6: Toolbar horizontal con HBox."""
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("Ejemplo 6: Toolbar")
    clock = pygame.time.Clock()

    ui = UIManager(600, 400)

    # Toolbar superior
    toolbar = Panel(
        x=0, y=0,
        width=600, height=60,
        bg_color=(40, 40, 40),
        border_width=1,
        padding=10
    )
    ui.add(toolbar)

    # Botones del toolbar
    hbox = HBox(spacing=10, align='center', height=40)
    toolbar.add_child(hbox)

    buttons = [
        ("Nuevo", (76, 175, 80)),
        ("Abrir", (33, 150, 243)),
        ("Guardar", (255, 193, 7)),
        ("Deshacer", (100, 100, 100)),
        ("Rehacer", (100, 100, 100)),
    ]

    for text, color in buttons:
        btn = Button(
            text=text,
            width=90,
            height=36,
            bg_color=color
        ).on_click(lambda b, t=text: print(f"{t} presionado"))
        hbox.add_child(btn)

    # Área de contenido
    content = Label(
        x=250, y=200,
        text="Área de contenido",
        font_size=24,
        color=(150, 150, 150)
    )
    ui.add(content)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
               (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            ui.handle_event(event)

        ui.update(clock.tick(60) / 1000.0)

        screen.fill((30, 30, 30))
        ui.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    print("=== Ejemplos del Framework UI ===")
    print("1. Básico - Botón simple")
    print("2. Menú - VBox layout")
    print("3. Panel con Inputs")
    print("4. Sliders de audio")
    print("5. Grid de niveles")
    print("6. Toolbar horizontal")
    print("\nSelecciona un ejemplo (1-6) o 0 para salir:")

    try:
        choice = input("> ")

        if choice == '1':
            ejemplo_1_basico()
        elif choice == '2':
            ejemplo_2_menu()
        elif choice == '3':
            ejemplo_3_panel_con_inputs()
        elif choice == '4':
            ejemplo_4_sliders()
        elif choice == '5':
            ejemplo_5_grid()
        elif choice == '6':
            ejemplo_6_toolbar()
        elif choice == '0':
            print("¡Hasta luego!")
        else:
            print("Opción inválida")
    except KeyboardInterrupt:
        print("\n¡Hasta luego!")

