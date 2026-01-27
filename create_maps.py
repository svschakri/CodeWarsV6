"""
Map creation utility - creates starter maps for PyTanks
Run this to generate default map files in the maps/ folder
"""

import numpy as np
import os

def create_default_map():
    """Create a simple default map"""
    GRID_H, GRID_W = 30, 40
    collision_map = np.ones((GRID_H, GRID_W), dtype=np.int32)
    
    # Ground
    collision_map[-1, :] = 0
    
    # Platforms
    collision_map[20, 5:15] = 0
    collision_map[15, 25:35] = 0
    collision_map[10, 10:20] = 0
    
    return collision_map

def create_minimilitia_style_map():
    """Create a Mini Militia inspired map with symmetrical layout"""
    GRID_H, GRID_W = 30, 40
    collision_map = np.ones((GRID_H, GRID_W), dtype=np.int32)
    
    # Ground floor
    collision_map[-1, :] = 0
    
    # Left bunker
    collision_map[25:29, 2:6] = 0  # walls
    collision_map[24, 2:6] = 0  # roof
    
    # Right bunker (symmetrical)
    collision_map[25:29, 34:38] = 0
    collision_map[24, 34:38] = 0
    
    # Center tower
    collision_map[15:29, 19:21] = 0  # vertical wall
    collision_map[14, 17:23] = 0  # top platform
    
    # Mid-level platforms (left and right)
    collision_map[20, 8:14] = 0
    collision_map[20, 26:32] = 0
    
    # Upper platforms
    collision_map[10, 5:12] = 0
    collision_map[10, 28:35] = 0
    
    # Top center platform
    collision_map[5, 16:24] = 0
    
    # Side walls for boundaries
    collision_map[0:29, 0] = 0  # left wall
    collision_map[0:29, 39] = 0  # right wall
    
    return collision_map

def create_arena_map():
    """Create an arena-style map"""
    GRID_H, GRID_W = 30, 40
    collision_map = np.ones((GRID_H, GRID_W), dtype=np.int32)
    
    # Ground
    collision_map[-1, :] = 0
    
    # Outer walls (arena)
    collision_map[:, 0] = 0  # left
    collision_map[:, -1] = 0  # right
    collision_map[0, :] = 0  # top
    
    # Center elevated platform
    collision_map[18, 15:25] = 0
    
    # Corner platforms
    collision_map[10, 3:8] = 0  # top-left
    collision_map[10, 32:37] = 0  # top-right
    collision_map[23, 3:8] = 0  # bottom-left
    collision_map[23, 32:37] = 0  # bottom-right
    
    # Center obstacles
    collision_map[15:17, 12] = 0
    collision_map[15:17, 27] = 0
    
    return collision_map

def create_open_map():
    """Create a simple open map with minimal obstacles"""
    GRID_H, GRID_W = 30, 40
    collision_map = np.ones((GRID_H, GRID_W), dtype=np.int32)
    
    # Ground only
    collision_map[-1, :] = 0
    
    # Few scattered platforms
    collision_map[22, 10:15] = 0
    collision_map[22, 25:30] = 0
    collision_map[15, 18:22] = 0
    
    return collision_map


if __name__ == "__main__":
    # Create maps directory if it doesn't exist
    if not os.path.exists("maps"):
        os.makedirs("maps")
    
    # Create and save maps
    maps = {
        "default": create_default_map(),
        "minimilitia": create_minimilitia_style_map(),
        "arena": create_arena_map(),
        "open": create_open_map()
    }
    
    for name, collision_map in maps.items():
        filepath = os.path.join("maps", f"{name}.npy")
        np.save(filepath, collision_map)
        print(f"Created: {filepath}")
    
    print("\nMaps created successfully!")
    print("Available maps:", ", ".join(maps.keys()))
    print("\nTo use a map, edit server.py line with self.load_map('map_name')")
    print("Or use map_editor.py to create custom maps")
