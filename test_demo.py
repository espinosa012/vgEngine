#!/usr/bin/env python3
import sys
import os
os.chdir('/Users/espinosa025/Documents/virigir/vgEngine')
sys.path.insert(0, '/Users/espinosa025/Documents/virigir/vgEngine')

result_file = '/tmp/demo_test_result.txt'

try:
    with open(result_file, 'w') as f:
        f.write("Iniciando test...\n")

        import pygame
        pygame.init()
        f.write("✅ Pygame inicializado\n")

        from src.ui import UIManager, Label, Button, Panel, Grid, VBox, HBox
        f.write("✅ Imports OK\n")

        ui = UIManager(800, 600)
        f.write("✅ UIManager creado\n")

        panel = Panel(x=20, y=20, width=200, height=150, bg_color=(40, 40, 40), padding=20)
        f.write("✅ Panel creado\n")

        label = Label(text='Test', font_size=28, bold=True)
        f.write("✅ Label creado\n")

        grid = Grid(columns=3, spacing_x=20, spacing_y=20)
        f.write("✅ Grid creado\n")

        # Test completo del demo
        from demo_ui_framework import UIDemo
        f.write("✅ Import de UIDemo OK\n")

        demo = UIDemo()
        f.write("✅ UIDemo instanciado correctamente\n")

        pygame.quit()
        f.write("\n🎉 ¡EL DEMO FUNCIONA CORRECTAMENTE!\n")
        f.write("Puedes ejecutar: python3 demo_ui_framework.py\n")

    print("SUCCESS - ver resultado en", result_file)

except Exception as e:
    with open(result_file, 'a') as f:
        f.write(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc(file=f)
    print(f"ERROR: {e}")
    sys.exit(1)

