#!/usr/bin/env python3
"""Test rápido de imports y creación de widgets"""
import sys
sys.path.insert(0, '/Users/espinosa025/Documents/virigir/vgEngine')

try:
    import pygame
    pygame.init()

    from src.ui import (
        UIManager, Label, Button, Panel,
        Checkbox, Slider, TextInput, ImageWidget,
        VBox, HBox, Grid, Container, ScrollView
    )

    # Test creación de cada widget
    ui = UIManager(800, 600)
    label = Label(text='Test')
    button = Button(text='Test')
    panel = Panel()
    checkbox = Checkbox(text='Test')
    slider = Slider()
    text_input = TextInput(placeholder='Test')
    image = ImageWidget()
    vbox = VBox()
    hbox = HBox()
    grid = Grid(columns=3)
    container = Container()
    scroll = ScrollView(width=200, height=200)

    print("✅ Todos los widgets creados exitosamente")

    # Test del demo
    from demo_ui_framework import UIDemo
    print("✅ Import del demo OK")

    demo = UIDemo()
    print("✅ Demo instanciado correctamente")

    pygame.quit()
    print("\n🎉 ¡TODO FUNCIONA! El demo está listo para ejecutarse.")
    print("\nEjecuta:")
    print("  python3 demo_ui_framework.py")

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

