#!/usr/bin/env python3
"""
Test exhaustivo de RandomTerrainScene antes de ejecutar pygame_test.py

Este script verifica que:
1. Todos los imports funcionan
2. TileSet se puede generar
3. TileMap se puede crear y llenar
4. Camera funciona correctamente
5. RandomTerrainScene se puede inicializar
6. El renderizado funciona sin errores
"""

import sys
sys.path.insert(0, '/Users/espinosa025/Documents/virigir/vgEngine/src')

print("="*70)
print("TEST EXHAUSTIVO - RandomTerrainScene")
print("="*70)
print()

# Test 1: Imports
print("1. Testing imports...")
try:
    import pygame
    from core.tilemap.tileset import TileSet
    from core.tilemap.tilemap import TileMap
    from core.tilemap.mapcell import MapCell
    from core.camera.camera import Camera
    from game.test_scenes.random_terrain_scene import RandomTerrainScene
    print("   ✅ All imports OK")
except Exception as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# Test 2: TileSet generation
print("\n2. Testing TileSet generation...")
try:
    tileset = TileSet.generate_terrain_tileset(
        tile_size=(32, 32),
        columns=6,
        output_path="/tmp/test_terrain_tileset.png"
    )
    print(f"   ✅ TileSet generated: {tileset}")

    # Verificar que tiene get_tile_surface
    assert hasattr(tileset, 'get_tile_surface'), "TileSet debe tener get_tile_surface"
    print("   ✅ TileSet.get_tile_surface exists")

    # Test getting a tile
    tile_surface = tileset.get_tile_surface(0)
    assert tile_surface is not None, "Should get a surface for tile 0"
    print(f"   ✅ get_tile_surface(0) returns: {tile_surface}")

except Exception as e:
    print(f"   ❌ TileSet error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: TileMap creation
print("\n3. Testing TileMap...")
try:
    tilemap = TileMap(width=256, height=256, tile_size=(32, 32))
    tilemap.tileset = tileset
    print(f"   ✅ TileMap created: {tilemap}")

    # Set some tiles
    tilemap.set_tile(0, 0, tile_id=2, tileset_id=0)
    tilemap.set_tile(5, 5, tile_id=3, tileset_id=0)
    print("   ✅ Tiles set successfully")

    # Get tiles
    cell = tilemap.get_tile(0, 0)
    assert cell is not None, "Cell should exist"
    assert isinstance(cell, MapCell), "Should return MapCell"
    assert cell.tile_id == 2, "Tile ID should be 2"
    print(f"   ✅ get_tile returns MapCell with tile_id={cell.tile_id}")

except Exception as e:
    print(f"   ❌ TileMap error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Camera
print("\n4. Testing Camera...")
try:
    pygame.init()
    camera = Camera(x=0, y=0, width=800, height=600, zoom=1.0)
    print(f"   ✅ Camera created: x={camera.x}, y={camera.y}")

    # Test movement
    camera.move(10, 20)
    assert camera.x == 10, "Camera x should be 10"
    assert camera.y == 20, "Camera y should be 20"
    print(f"   ✅ Camera.move works: ({camera.x}, {camera.y})")

    # Test screen_to_world
    world_x, world_y = camera.screen_to_world(100, 100)
    print(f"   ✅ screen_to_world works: ({world_x}, {world_y})")

    # Test bounds
    camera.set_bounds(min_x=0, max_x=8192, min_y=0, max_y=8192)
    print("   ✅ set_bounds works")

except Exception as e:
    print(f"   ❌ Camera error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: RandomTerrainScene initialization
print("\n5. Testing RandomTerrainScene initialization...")
try:
    # Create a pygame surface
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Test")

    scene = RandomTerrainScene()
    print(f"   ✅ Scene created: {scene.name}")
    print(f"   ✅ Running: {scene.running}")

    # Enter scene
    scene.on_enter()
    print("   ✅ on_enter() completed")

    # Verify scene state
    assert scene.tilemap is not None, "tilemap should be initialized"
    assert scene.camera is not None, "camera should be initialized"
    assert scene.tilemap.tileset is not None, "tileset should be assigned"
    print("   ✅ Scene state verified")

except Exception as e:
    print(f"   ❌ Scene initialization error: {e}")
    import traceback
    traceback.print_exc()
    pygame.quit()
    sys.exit(1)

# Test 6: Rendering
print("\n6. Testing rendering...")
try:
    # Try to draw
    scene.draw(screen)
    print("   ✅ scene.draw() works")

    # Try to update
    scene.update(0.016)  # ~60 FPS
    print("   ✅ scene.update() works")

    # Test event handling
    test_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w)
    scene.handle_event(test_event)
    print("   ✅ scene.handle_event() works")

except Exception as e:
    print(f"   ❌ Rendering error: {e}")
    import traceback
    traceback.print_exc()
    pygame.quit()
    sys.exit(1)

# Test 7: Full render cycle
print("\n7. Testing full render cycle...")
try:
    # Move camera to see different tiles
    scene.camera.move(500, 500)

    # Draw again
    scene.draw(screen)
    pygame.display.flip()
    print("   ✅ Full render cycle works")

    # Cleanup
    scene.on_exit()
    print("   ✅ on_exit() works")

except Exception as e:
    print(f"   ❌ Full cycle error: {e}")
    import traceback
    traceback.print_exc()
    pygame.quit()
    sys.exit(1)

# Final cleanup
pygame.quit()

print()
print("="*70)
print("🎉 TODOS LOS TESTS PASARON!")
print("="*70)
print()
print("El sistema está listo para ejecutar:")
print("  python3 src/game/pygame_test.py")
print()
print("Resumen de verificaciones:")
print("  ✅ Imports correctos")
print("  ✅ TileSet.generate_terrain_tileset()")
print("  ✅ TileSet.get_tile_surface()")
print("  ✅ TileMap con MapCell")
print("  ✅ Camera con movimiento y bounds")
print("  ✅ RandomTerrainScene.on_enter()")
print("  ✅ Renderizado funcional")
print("  ✅ Update y eventos")
print("  ✅ Ciclo completo sin errores")
print()

sys.exit(0)

