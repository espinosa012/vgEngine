#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/espinosa025/Documents/virigir/vgEngine')

try:
    import pygame
    pygame.init()
    from src.ui import Label
    l = Label(text='test')
    with open('/tmp/ui_test_result.txt', 'w') as f:
        f.write('SUCCESS: Label created without themes\n')
    print('SUCCESS')
except Exception as e:
    with open('/tmp/ui_test_result.txt', 'w') as f:
        f.write(f'ERROR: {e}\n')
        import traceback
        traceback.print_exc(file=f)
    print(f'ERROR: {e}')
    sys.exit(1)

