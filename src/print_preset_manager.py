#!/usr/bin/env python3
"""
Print Preset Manager - Manages printer configuration presets for batch printing
"""

import json
import logging
from typing import Dict, List, Optional
from pathlib import Path


class PrintPreset:
    """Represents a print configuration preset"""
    def __init__(self, name: str, preset_data: Dict):
        self.name = name
        self.printer_11x17_enabled = preset_data.get('printer_11x17_enabled', True)
        self.printer_11x17_script = preset_data.get('printer_11x17_script', '')
        self.printer_11x17_copies = preset_data.get('printer_11x17_copies', 1)

        self.printer_24x36_enabled = preset_data.get('printer_24x36_enabled', True)
        self.printer_24x36_script = preset_data.get('printer_24x36_script', '')
        self.printer_24x36_copies = preset_data.get('printer_24x36_copies', 1)

        self.folder_label_enabled = preset_data.get('folder_label_enabled', True)
        self.folder_label_printer = preset_data.get('folder_label_printer', '')

        self.is_default = preset_data.get('is_default', False)

    def to_dict(self) -> Dict:
        """Convert preset to dictionary for storage"""
        return {
            'printer_11x17_enabled': self.printer_11x17_enabled,
            'printer_11x17_script': self.printer_11x17_script,
            'printer_11x17_copies': self.printer_11x17_copies,
            'printer_24x36_enabled': self.printer_24x36_enabled,
            'printer_24x36_script': self.printer_24x36_script,
            'printer_24x36_copies': self.printer_24x36_copies,
            'folder_label_enabled': self.folder_label_enabled,
            'folder_label_printer': self.folder_label_printer,
            'is_default': self.is_default
        }

    def get_printers_config(self, template_path: str = None) -> List[Dict]:
        """
        Get printer configuration list for batch printing

        Returns:
            List of printer configs ready for batch execution
        """
        printers_config = []

        if self.printer_11x17_enabled and self.printer_11x17_script:
            printers_config.append({
                'type': '11x17',
                'printer_name': self.printer_11x17_script,
                'copies': self.printer_11x17_copies
            })

        if self.printer_24x36_enabled and self.printer_24x36_script:
            printers_config.append({
                'type': '24x36',
                'printer_name': self.printer_24x36_script,
                'copies': self.printer_24x36_copies
            })

        if self.folder_label_enabled and self.folder_label_printer:
            printers_config.append({
                'type': 'folder',
                'printer_name': self.folder_label_printer,
                'template_path': template_path
            })

        return printers_config


class PrintPresetManager:
    """Manages print presets - saving, loading, and retrieving"""

    def __init__(self, presets_file: str = "print_presets.json"):
        self.presets_file = presets_file
        self.presets: Dict[str, PrintPreset] = {}
        self.load_presets()

        # Create default presets if none exist
        if not self.presets:
            self._create_default_presets()

    def load_presets(self):
        """Load presets from file"""
        try:
            if Path(self.presets_file).exists():
                with open(self.presets_file, 'r') as f:
                    data = json.load(f)

                for name, preset_data in data.items():
                    self.presets[name] = PrintPreset(name, preset_data)

                logging.info(f"Loaded {len(self.presets)} print presets")
            else:
                logging.info("No presets file found, will create defaults")
        except Exception as e:
            logging.error(f"Failed to load presets: {e}")

    def save_presets(self):
        """Save presets to file"""
        try:
            data = {}
            for name, preset in self.presets.items():
                data[name] = preset.to_dict()

            with open(self.presets_file, 'w') as f:
                json.dump(data, f, indent=2)

            logging.info(f"Saved {len(self.presets)} print presets")
            return True
        except Exception as e:
            logging.error(f"Failed to save presets: {e}")
            return False

    def _create_default_presets(self):
        """Create default presets for new installations"""
        default_presets = {
            "Standard Plot": {
                'printer_11x17_enabled': True,
                'printer_11x17_script': '',
                'printer_11x17_copies': 1,
                'printer_24x36_enabled': True,
                'printer_24x36_script': '',
                'printer_24x36_copies': 1,
                'folder_label_enabled': True,
                'folder_label_printer': '',
                'is_default': True
            },
            "11x17 Only": {
                'printer_11x17_enabled': True,
                'printer_11x17_script': '',
                'printer_11x17_copies': 1,
                'printer_24x36_enabled': False,
                'printer_24x36_script': '',
                'printer_24x36_copies': 1,
                'folder_label_enabled': True,
                'folder_label_printer': '',
                'is_default': False
            },
            "24x36 Only": {
                'printer_11x17_enabled': False,
                'printer_11x17_script': '',
                'printer_11x17_copies': 1,
                'printer_24x36_enabled': True,
                'printer_24x36_script': '',
                'printer_24x36_copies': 1,
                'folder_label_enabled': True,
                'folder_label_printer': '',
                'is_default': False
            }
        }

        for name, preset_data in default_presets.items():
            self.presets[name] = PrintPreset(name, preset_data)

        self.save_presets()
        logging.info("Created default print presets")

    def get_preset(self, name: str) -> Optional[PrintPreset]:
        """Get a preset by name"""
        return self.presets.get(name)

    def get_all_presets(self) -> Dict[str, PrintPreset]:
        """Get all presets"""
        return self.presets.copy()

    def get_preset_names(self) -> List[str]:
        """Get list of preset names"""
        return list(self.presets.keys())

    def get_default_preset(self) -> Optional[PrintPreset]:
        """Get the default preset"""
        for preset in self.presets.values():
            if preset.is_default:
                return preset

        # If no default set, return first preset
        if self.presets:
            return list(self.presets.values())[0]

        return None

    def add_preset(self, name: str, preset_data: Dict) -> bool:
        """Add a new preset"""
        try:
            if name in self.presets:
                logging.warning(f"Preset '{name}' already exists, will be overwritten")

            self.presets[name] = PrintPreset(name, preset_data)
            return self.save_presets()
        except Exception as e:
            logging.error(f"Failed to add preset '{name}': {e}")
            return False

    def update_preset(self, name: str, preset_data: Dict) -> bool:
        """Update an existing preset"""
        try:
            if name not in self.presets:
                logging.error(f"Preset '{name}' does not exist")
                return False

            self.presets[name] = PrintPreset(name, preset_data)
            return self.save_presets()
        except Exception as e:
            logging.error(f"Failed to update preset '{name}': {e}")
            return False

    def delete_preset(self, name: str) -> bool:
        """Delete a preset"""
        try:
            if name not in self.presets:
                logging.error(f"Preset '{name}' does not exist")
                return False

            # Don't allow deleting the last preset
            if len(self.presets) <= 1:
                logging.error("Cannot delete the last preset")
                return False

            # If deleting default preset, set another as default
            if self.presets[name].is_default:
                del self.presets[name]
                # Set first remaining preset as default
                first_preset = list(self.presets.values())[0]
                first_preset.is_default = True
            else:
                del self.presets[name]

            return self.save_presets()
        except Exception as e:
            logging.error(f"Failed to delete preset '{name}': {e}")
            return False

    def set_default_preset(self, name: str) -> bool:
        """Set a preset as the default"""
        try:
            if name not in self.presets:
                logging.error(f"Preset '{name}' does not exist")
                return False

            # Unset all defaults
            for preset in self.presets.values():
                preset.is_default = False

            # Set new default
            self.presets[name].is_default = True

            return self.save_presets()
        except Exception as e:
            logging.error(f"Failed to set default preset '{name}': {e}")
            return False

    def get_available_printers(self) -> List[str]:
        """Get list of available printers (print server scripts)"""
        try:
            import win32print
            printers = win32print.EnumPrinters(
                win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
            )
            return [printer[2] for printer in printers]
        except Exception as e:
            logging.error(f"Failed to get available printers: {e}")
            return []
