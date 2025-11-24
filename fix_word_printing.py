#!/usr/bin/env python3
"""
Fix Win32com Cache Issue - Clears corrupted cache
"""

import shutil
import os
from pathlib import Path

print("=" * 80)
print("FIXING WIN32COM CACHE FOR WORD PRINTING")
print("=" * 80)
print()

try:
    # Find the win32com cache directory
    import win32com
    import tempfile

    # Get the temp directory where win32com stores its cache
    temp_dir = tempfile.gettempdir()
    gen_py_dir = Path(temp_dir) / "gen_py"

    print(f"Looking for win32com cache at: {gen_py_dir}")

    if gen_py_dir.exists():
        print(f"Found cache directory!")
        print(f"Deleting: {gen_py_dir}")
        shutil.rmtree(gen_py_dir)
        print("✓ Cache cleared!")
    else:
        print("Cache directory not found (that's okay, might be somewhere else)")

    # Alternative location - user's local app data
    import win32api
    local_appdata = os.environ.get('LOCALAPPDATA')
    if local_appdata:
        gen_py_dir2 = Path(local_appdata) / "Temp" / "gen_py"
        if gen_py_dir2.exists():
            print(f"\nFound alternate cache at: {gen_py_dir2}")
            print(f"Deleting: {gen_py_dir2}")
            shutil.rmtree(gen_py_dir2)
            print("✓ Alternate cache cleared!")

    print()
    print("=" * 80)
    print("DONE!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Try printing again")
    print("2. Folder labels should now work")
    print()

except Exception as e:
    print(f"Error: {e}")
    print()
    print("Alternative fix:")
    print("1. Close Python/app completely")
    print("2. Delete folder: C:\\Users\\YourName\\AppData\\Local\\Temp\\gen_py")
    print("3. Restart the app")
    print()

input("Press Enter to close...")
