#!/usr/bin/env python3
"""
Test the preset UI
"""

import tkinter as tk
import sys
sys.path.insert(0, 'src')

from print_preset_manager import PrintPresetManager
from print_preset_ui import PresetManagerDialog

# Create root window
root = tk.Tk()
root.withdraw()  # Hide the root window

# Create preset manager
preset_manager = PrintPresetManager()

print("Presets loaded:")
for name in preset_manager.get_preset_names():
    print(f"  - {name}")

# Open dialog
dialog = PresetManagerDialog(root, preset_manager)

root.mainloop()
