#!/usr/bin/env python3
"""
User Preferences Manager - Per-user settings (separate from network config)
Handles user-specific preferences without modifying network printer configuration
"""

import json
import logging
from typing import Dict, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from error_logger import log_info, log_error


@dataclass
class UserPreferences:
    """User-specific preferences"""
    # Printing preferences
    default_11x17_copies: int = 1
    default_24x36_copies: int = 1
    default_folder_label_enabled: bool = True

    # Preferred printers (references to network config)
    preferred_11x17_printer: str = ""  # Printer name from network config
    preferred_24x36_printer: str = ""  # Printer name from network config
    preferred_folder_label_printer: str = ""  # Printer name from network config

    # UI preferences
    last_preset_used: str = ""
    auto_mark_processed: bool = True
    show_print_preview: bool = False

    # User info (for logging/tracking)
    username: str = ""
    last_updated: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


class UserPreferencesManager:
    """Manages user-specific preferences"""

    def __init__(self, preferences_file: str = "user_preferences.json"):
        """
        Initialize user preferences manager

        Args:
            preferences_file: Path to user preferences file
        """
        self.preferences_file = preferences_file
        self.preferences: Optional[UserPreferences] = None

        # Load existing preferences or create defaults
        if not self.load_preferences():
            self.create_default_preferences()

    def load_preferences(self) -> bool:
        """
        Load user preferences from file

        Returns:
            True if successful, False otherwise
        """
        try:
            prefs_path = Path(self.preferences_file)

            if not prefs_path.exists():
                log_info("No user preferences found, will create defaults")
                return False

            with open(prefs_path, 'r') as f:
                data = json.load(f)

            self.preferences = UserPreferences(**data)

            log_info("Loaded user preferences", {
                'username': self.preferences.username,
                'last_preset': self.preferences.last_preset_used
            })

            return True

        except Exception as e:
            log_error("load_user_preferences", e, {
                'preferences_file': self.preferences_file
            })
            return False

    def save_preferences(self) -> bool:
        """
        Save user preferences to file

        Returns:
            True if successful, False otherwise
        """
        if not self.preferences:
            return False

        try:
            from datetime import datetime

            # Update timestamp
            self.preferences.last_updated = datetime.now().isoformat()

            # Save to file
            with open(self.preferences_file, 'w') as f:
                json.dump(self.preferences.to_dict(), f, indent=2)

            log_info("Saved user preferences")
            return True

        except Exception as e:
            log_error("save_user_preferences", e, {
                'preferences_file': self.preferences_file
            })
            return False

    def create_default_preferences(self):
        """Create default user preferences"""
        import os
        from datetime import datetime

        self.preferences = UserPreferences(
            default_11x17_copies=1,
            default_24x36_copies=1,
            default_folder_label_enabled=True,
            preferred_11x17_printer="",
            preferred_24x36_printer="",
            preferred_folder_label_printer="",
            last_preset_used="Standard Plot",
            auto_mark_processed=True,
            show_print_preview=False,
            username=os.getenv('USERNAME', 'Unknown'),
            last_updated=datetime.now().isoformat()
        )

        self.save_preferences()
        log_info("Created default user preferences")

    def get_print_settings(self) -> Dict:
        """
        Get current print settings for batch printing

        Returns:
            Dictionary with print settings
        """
        if not self.preferences:
            self.create_default_preferences()

        return {
            'copies_11x17': self.preferences.default_11x17_copies,
            'copies_24x36': self.preferences.default_24x36_copies,
            'folder_label_enabled': self.preferences.default_folder_label_enabled,
            'preferred_11x17': self.preferences.preferred_11x17_printer,
            'preferred_24x36': self.preferences.preferred_24x36_printer,
            'preferred_folder_label': self.preferences.preferred_folder_label_printer,
            'auto_mark_processed': self.preferences.auto_mark_processed
        }

    def update_print_settings(self, settings: Dict) -> bool:
        """
        Update print settings from user input

        Args:
            settings: Dictionary with new settings

        Returns:
            True if successful
        """
        if not self.preferences:
            self.create_default_preferences()

        try:
            if 'copies_11x17' in settings:
                self.preferences.default_11x17_copies = settings['copies_11x17']
            if 'copies_24x36' in settings:
                self.preferences.default_24x36_copies = settings['copies_24x36']
            if 'folder_label_enabled' in settings:
                self.preferences.default_folder_label_enabled = settings['folder_label_enabled']
            if 'preferred_11x17' in settings:
                self.preferences.preferred_11x17_printer = settings['preferred_11x17']
            if 'preferred_24x36' in settings:
                self.preferences.preferred_24x36_printer = settings['preferred_24x36']
            if 'preferred_folder_label' in settings:
                self.preferences.preferred_folder_label_printer = settings['preferred_folder_label']
            if 'auto_mark_processed' in settings:
                self.preferences.auto_mark_processed = settings['auto_mark_processed']

            return self.save_preferences()

        except Exception as e:
            log_error("update_print_settings", e, {'settings': settings})
            return False

    def remember_last_preset(self, preset_name: str) -> bool:
        """
        Remember the last used preset

        Args:
            preset_name: Name of preset

        Returns:
            True if successful
        """
        if not self.preferences:
            self.create_default_preferences()

        self.preferences.last_preset_used = preset_name
        return self.save_preferences()

    def get_last_preset(self) -> str:
        """
        Get the last used preset name

        Returns:
            Preset name or empty string
        """
        if not self.preferences:
            return ""

        return self.preferences.last_preset_used
