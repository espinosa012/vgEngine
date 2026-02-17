#!/usr/bin/env python3
"""
Test rápido del demo UI framework.
"""

import pygame
import sys

sys.path.insert(0, '/Users/espinosa025/Documents/virigir/vgEngine')

from src.ui import UIManager, Label, Button, Panel, VBox, Grid

def test_panel_properties():
    """Test que Panel tiene content_width y content_height."""
    pygame.init()

    panel = Panel(
        x=20, y=20,
        width=200,
        height=150,
        padding=10
    )

    assert hasattr(panel, 'content_width'), "Panel debe tener content_width"
    assert hasattr(panel, 'content_height'), "Panel debe tener content_height"

    assert panel.width == 200
    assert panel.height == 150
    assert panel.padding == 10
    assert panel.content_width == 180  # 200 - (10 * 2)
    assert panel.content_height == 130  # 150 - (10 * 2)

    print("✅ Panel tiene content_width y content_height")
    print(f"   width: {panel.width}, content_width: {panel.content_width}")
    print(f"   height: {panel.height}, content_height: {panel.content_height}")

    pygame.quit()
    return True

def test_demo_ui_creation():
    """Test que se puede crear la UI del demo sin errores."""
    pygame.init()

    screen_width = 1024
    screen_height = 768

    ui = UIManager(screen_width, screen_height)

    # Main panel (como en el demo)
    main_panel = Panel(
        x=20, y=20,
        width=screen_width - 40,
        height=screen_height - 40,
        bg_color=(40, 40, 40),
        border_width=2,
        border_radius=8,
        padding=20
    )
    ui.add(main_panel)

    # Title
    title = Label(
        x=0, y=0,
        text="vgEngine UI Framework Demo",
        font_size=28
    )
    main_panel.add_child(title)

    # Grid usando content_width (esto causaba el error)
    try:
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

        print("✅ Grid creado exitosamente usando Panel.content_width")
        print(f"   Grid width: {grid.width} (de Panel.content_width: {main_panel.content_width})")

    except AttributeError as e:
        print(f"❌ Error: {e}")
        pygame.quit()
        return False

    # Crear algunos paneles hijos (como en el demo)
    for i in range(3):
        section_panel = Panel(
            width=250, height=200,
            bg_color=(50, 50, 50),
            border_width=1,
            border_radius=4,
            padding=10
        )

        vbox = VBox(spacing=10, align='stretch')
        section_panel.add_child(vbox)

        vbox.add_child(Label(text=f"Section {i+1}", font_size=18))
        vbox.add_child(Button(text="Test Button", height=36))

        grid.add_child(section_panel)

    print("✅ Secciones del demo creadas exitosamente")

    pygame.quit()
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("Test de corrección: Panel.content_width")
    print("=" * 60)
    print()

    try:
        if test_panel_properties():
            print()
            if test_demo_ui_creation():
                print()
                print("=" * 60)
                print("🎉 ¡TODOS LOS TESTS PASARON!")
                print("=" * 60)
                print()
                print("El demo_ui_framework.py debería funcionar correctamente ahora.")
                print("Ejecuta: python3 demo_ui_framework.py")
                sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error en los tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    sys.exit(1)

