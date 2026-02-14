#!/usr/bin/env python3
"""
Launch the Tilemap Editor application.
"""
import sys
from pathlib import Path
# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))
import tkinter as tk
from tilemap_editor.app import TilemapEditor
def main():
    """Main entry point."""
    root = tk.Tk()
    app = TilemapEditor(root)
    root.mainloop()
if __name__ == "__main__":
    main()
