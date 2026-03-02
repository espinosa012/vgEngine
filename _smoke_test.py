import sys, os
sys.path.insert(0, 'src')
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
pygame.init()
pygame.display.set_mode((1440, 900))

# ── SelectableList widget standalone ──────────────────────────────────────────
from ui.widgets.selectable_list import SelectableList

lst = SelectableList(x=0, y=0, width=200, height=300, title='Test')
lst.add_item('char_0')
lst.add_item('char_1')
lst.add_item('char_2')
assert lst.item_count == 3, f"Expected 3, got {lst.item_count}"

selected_log = []
lst.on_select(lambda i, l: selected_log.append((i, l)))

lst.select(1)
assert lst.selected_index == 1
assert lst.selected_label == 'char_1'
assert selected_log[-1] == (1, 'char_1')

lst.select(-1)
assert lst.selected_index == -1

lst.remove_item(1)
assert lst.item_count == 2
print("SelectableList widget OK")

# ── CharacterScene integration ─────────────────────────────────────────────────
from game.test_scenes.character_scene import CharacterScene

s = CharacterScene()
s.on_enter()

for _ in range(4):
    s._spawn_character()

assert s._char_list is not None
assert s._char_list.item_count == 4, f"Expected 4 items, got {s._char_list.item_count}"
print(f"List has {s._char_list.item_count} items  OK")

# Select index 2
s._char_list.select(2)
assert s._selected_char is s._characters[2], "Wrong character selected"
assert s._characters[2].shape.selected is True, "shape.selected should be True"
assert s._characters[0].shape.selected is False, "Other chars should not be selected"
print(f"Selection OK: '{s._selected_char.name}' selected, shape.selected=True")

# Deselect (index -1)
s._char_list.select(-1)
assert s._selected_char is None
assert s._characters[2].shape.selected is False
print("Deselect OK")

# Re-select and verify only one is ever selected
s._char_list.select(0)
s._char_list.select(3)
assert s._characters[3].shape.selected is True
assert s._characters[0].shape.selected is False
print("Re-select OK: only char_3 selected")

# Draw
surf = pygame.display.get_surface()
s.draw(surf)
print("draw OK")

s._randomize_obstacles()
s.draw(surf)
print("draw with obstacles OK")

s.on_exit()
pygame.quit()
print("ALL GOOD")

