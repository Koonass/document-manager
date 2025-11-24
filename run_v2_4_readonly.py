#!/usr/bin/env python3
"""
Document Manager V2.4 - Read-Only Safe Launcher
Handles running from read-only locations (USB drives)
by redirecting data storage to writable location
"""

import sys
import os
from pathlib import Path

# Check if running in read-only mode
READONLY_MODE = os.environ.get('DM_READONLY_MODE') == '1'
DATA_PATH = os.environ.get('DM_DATA_PATH', '')
SETTINGS_PATH = os.environ.get('DM_SETTINGS_PATH', '')

if READONLY_MODE:
    print("=" * 75)
    print("READ-ONLY MODE DETECTED")
    print("=" * 75)
    print()
    print(f"Application running from: {os.path.dirname(__file__)}")
    print(f"Data stored at: {DATA_PATH}")
    print(f"Settings at: {SETTINGS_PATH}")
    print()

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Monkey-patch the settings manager to use custom paths
if READONLY_MODE:
    import json

    class ReadOnlySettingsManager:
        """Settings manager that works with read-only application directory"""

        def __init__(self):
            # Use settings path from environment
            self.settings_file = SETTINGS_PATH

            # Template is still in read-only app directory (that's fine, we only read it)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.template_path = os.path.join(script_dir, "LABEL TEMPLATE", "Contract_Lumber_Label_Template.docx")

            # Default settings with paths pointing to writable DATA location
            self.default_settings = {
                "html_path": os.path.join(DATA_PATH, "BisTrack Exports"),
                "pdf_path": os.path.join(DATA_PATH, "PDFs"),
                "archive_path": os.path.join(DATA_PATH, "Archive"),
                "db_path": os.path.join(DATA_PATH, "document_manager_v2.1.db"),
                "products_file_path": os.path.join(DATA_PATH, "products_master.csv"),
                "bistrack_import_folder": "",
                "printer1_name": "",
                "printer1_color_mode": "Color",
                "printer1_copies": 1,
                "printer1_enabled": True,
                "printer2_name": "",
                "printer2_color_mode": "Color",
                "printer2_copies": 1,
                "printer2_enabled": True,
                "folder_printer_name": "",
                "folder_printer_enabled": True,
                "version": "2.4.0"
            }
            self.settings = self.load_settings()

        def load_settings(self):
            try:
                if Path(self.settings_file).exists():
                    with open(self.settings_file, 'r') as f:
                        loaded_settings = json.load(f)
                        # Remove template_path if it exists
                        if 'template_path' in loaded_settings:
                            del loaded_settings['template_path']

                        # Convert any relative paths to use DATA_PATH
                        for key in ['html_path', 'pdf_path', 'archive_path', 'db_path', 'products_file_path']:
                            if key in loaded_settings:
                                path_value = loaded_settings[key]
                                # If it's a relative path (starts with DATA), make it absolute
                                if path_value and path_value.startswith('DATA'):
                                    relative_part = path_value[5:].lstrip('\\/')  # Remove "DATA\" or "DATA/"
                                    loaded_settings[key] = os.path.join(DATA_PATH, relative_part)

                        return loaded_settings
            except Exception as e:
                print(f"Warning: Could not load settings: {e}")
            return self.default_settings.copy()

        def save_settings(self):
            try:
                # Ensure settings directory exists
                settings_dir = os.path.dirname(self.settings_file)
                os.makedirs(settings_dir, exist_ok=True)

                settings_to_save = self.settings.copy()
                if 'template_path' in settings_to_save:
                    del settings_to_save['template_path']

                with open(self.settings_file, 'w') as f:
                    json.dump(settings_to_save, f, indent=2)
            except Exception as e:
                print(f"Error: Could not save settings: {e}")

        def get(self, key: str):
            if key == "template_path":
                return self.template_path
            return self.settings.get(key, self.default_settings.get(key, ""))

        def set(self, key: str, value):
            if key == "template_path":
                return
            self.settings[key] = value
            self.save_settings()

    # Replace the settings manager in the module before importing main
    import sys
    import types

    # Create a fake module for our patched settings manager
    settings_module = types.ModuleType('settings_manager_patch')
    settings_module.SettingsManagerV24 = ReadOnlySettingsManager
    sys.modules['settings_manager_patch'] = settings_module

    # Monkey-patch the import
    original_import = __builtins__.__import__

    def custom_import(name, *args, **kwargs):
        module = original_import(name, *args, **kwargs)
        # Patch SettingsManagerV24 when main_v2_4 is imported
        if name == 'main_v2_4' and hasattr(module, 'SettingsManagerV24'):
            module.SettingsManagerV24 = ReadOnlySettingsManager
            print("[PATCHED] Using read-only safe settings manager")
        return module

    __builtins__.__import__ = custom_import

try:
    from main_v2_4 import main

    if __name__ == "__main__":
        print("=" * 75)
        print("Document Manager V2.4 - BisTrack CSV Management")
        if READONLY_MODE:
            print("(Read-Only Mode)")
        print("=" * 75)
        print()

        if READONLY_MODE:
            print("⚠️  IMPORTANT: Data Storage Location")
            print(f"   Your database and files are stored at:")
            print(f"   {DATA_PATH}")
            print()
            print(f"   Place HTML files in:")
            print(f"   {os.path.join(DATA_PATH, 'BisTrack Exports')}")
            print()
            print(f"   Find generated PDFs at:")
            print(f"   {os.path.join(DATA_PATH, 'PDFs')}")
            print()

        print("📊 EXISTING FEATURES FROM V2.3")
        print("   • Enhanced calendar view with daily statistics")
        print("   • Category-based order management (Ready/Missing/Processed)")
        print("   • Batch PDF printing with automatic archiving")
        print("   • Real-time PDF attachment and status updates")
        print()
        print("📦 NEW: BISTRACK CSV IMPORT MANAGEMENT")
        print("   • 📂 Scan CSV folder for material import files")
        print("   • 🔍 Automatic order number extraction from CSV content")
        print("   • ✓ SKU validation against products master file")
        print("   • 🔧 Data quality checks (quantities, required fields)")
        print("   • 🛠️  Auto-fix suggestions for common errors")
        print("   • 📤 Upload validated CSVs to BisTrack import folder")
        print()
        print("Starting Document Manager V2.4...")
        print()

        main()

except ImportError as e:
    print(f"Import error: {e}")
    print("Please make sure all required packages are installed:")
    print("pip install PyQt5 pywin32")
    sys.exit(1)
except Exception as e:
    print(f"Error starting application: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
