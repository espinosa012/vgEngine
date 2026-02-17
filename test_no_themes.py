#!/usr/bin/env python3
"""Test que el framework funciona sin themes."""

import pygame
import sys

sys.path.insert(0, '/Users/espinosa025/Documents/virigir/vgEngine')

from src.ui import (
    UIManager, Button, Label, VBox, HBox, Grid,
    Panel, Checkbox, Slider, TextInput, ImageWidget,
    Container, ScrollView
)

def main():
    pygame.init()

    print("Testing UI Framework without themes...")
    print("="*60)

    # Test UIManager
    ui = UIManager(800, 600)
    print("✅ UIManager created")

    # Test all widgets
    try:
        label = Label(text='Test Label', font_size=16, color=(255, 255, 255))
        print("✅ Label")

        button = Button(text='Test Button', bg_color=(66, 135, 245))
        print("✅ Button")

        panel = Panel(bg_color=(50, 50, 50), padding=10)
        print("✅ Panel")

        checkbox = Checkbox(text='Test Checkbox')
        print("✅ Checkbox")

        slider = Slider(min_value=0, max_value=100, value=50)
        print("✅ Slider")

        text_input = TextInput(placeholder='Type here...')
        print("✅ TextInput")

        image_widget = ImageWidget(width=100, height=100)
        print("✅ ImageWidget")

        # Test containers
        vbox = VBox(spacing=10)
        print("✅ VBox")

        hbox = HBox(spacing=10)
        print("✅ HBox")

        grid = Grid(columns=3, spacing_x=5, spacing_y=5)
        print("✅ Grid")

        container = Container(padding=10)
        print("✅ Container")

        scroll_view = ScrollView(width=200, height=200)
        print("✅ ScrollView")

        # Test adding children
        vbox.add_child(label)
        vbox.add_child(button)
        panel.add_child(vbox)
        ui.add(panel)
        print("✅ Hierarchy created")

        # Test properties
        assert panel.content_width == panel.width - (panel.padding * 2)
        print("✅ Panel.content_width works")

        assert panel.content_height == panel.height - (panel.padding * 2)
        print("✅ Panel.content_height works")

        print("="*60)
        print("🎉 ALL TESTS PASSED!")
        print("✨ Framework works perfectly without themes")

        pygame.quit()
        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        return 1

if __name__ == '__main__':
    sys.exit(main())

