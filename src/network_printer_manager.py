#!/usr/bin/env python3
"""
Network Printer Manager - Centralized printer configuration for network deployment
Handles printer discovery, validation, and configuration management
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
from error_logger import log_error, log_info, log_warning, log_success


@dataclass
class PrinterDefinition:
    """Defines a printer with its network configuration"""
    display_name: str           # User-friendly name: "11x17 Printer"
    printer_name: str           # Actual Windows/network printer name
    printer_type: str           # Type: "11x17", "24x36", "folder_label", "other"
    is_default: bool = False    # Is this the default for its type?
    is_available: bool = False  # Is printer currently accessible?
    description: str = ""       # Admin notes
    last_verified: str = ""     # Timestamp of last successful connection

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class NetworkPrinterConfig:
    """Network-wide printer configuration"""
    printers_11x17: List[PrinterDefinition]
    printers_24x36: List[PrinterDefinition]
    printers_folder_label: List[PrinterDefinition]
    template_path: str
    auto_discover_on_startup: bool = True
    version: str = "1.0"
    last_updated: str = ""

    def to_dict(self) -> Dict:
        return {
            'printers_11x17': [p.to_dict() for p in self.printers_11x17],
            'printers_24x36': [p.to_dict() for p in self.printers_24x36],
            'printers_folder_label': [p.to_dict() for p in self.printers_folder_label],
            'template_path': self.template_path,
            'auto_discover_on_startup': self.auto_discover_on_startup,
            'version': self.version,
            'last_updated': self.last_updated
        }


class NetworkPrinterManager:
    """Manages network printer configuration and discovery for multi-user deployment"""

    def __init__(self, config_file: str = "network_printers.json"):
        """
        Initialize the network printer manager

        Args:
            config_file: Path to network printer configuration file
        """
        self.config_file = config_file
        self.config: Optional[NetworkPrinterConfig] = None
        self.available_printers: List[str] = []

        # Load configuration
        self.load_config()

        # Discover available printers
        self.discover_printers()

        # If config loaded, validate printer availability
        if self.config:
            self.validate_configured_printers()

    def discover_printers(self) -> List[str]:
        """
        Discover all available printers on the system and network

        Returns:
            List of printer names
        """
        try:
            import win32print

            log_info("Discovering available printers")

            # Get all local and network printers
            printers = win32print.EnumPrinters(
                win32print.PRINTER_ENUM_LOCAL |
                win32print.PRINTER_ENUM_CONNECTIONS
            )

            self.available_printers = [printer[2] for printer in printers]

            log_info(f"Discovered {len(self.available_printers)} printers", {
                'printer_names': self.available_printers
            })

            return self.available_printers

        except ImportError as e:
            log_error("win32print_import_failed", e, {
                'message': 'pywin32 not installed'
            })
            return []
        except Exception as e:
            log_error("printer_discovery_failed", e)
            return []

    def categorize_printers(self) -> Dict[str, List[str]]:
        """
        Automatically categorize discovered printers by type based on name patterns

        Returns:
            Dict with keys: 'large_format', 'standard', 'label', 'other'
        """
        categories = {
            'large_format': [],  # 24x36, plotters
            'standard': [],       # 11x17, tabloid
            'label': [],          # Label printers
            'other': []
        }

        # Keywords for large format printers
        large_format_keywords = [
            'designjet', 'plotter', 'wide', 'format', 'imageprograf',
            '24x36', '36', 'arch', 'cad', 'engineering', 'hp-z'
        ]

        # Keywords for standard printers
        standard_keywords = [
            '11x17', 'tabloid', 'ledger', 'legal'
        ]

        # Keywords for label printers
        label_keywords = [
            'label', 'dymo', 'zebra', 'brother', 'ql', 'p-touch'
        ]

        for printer in self.available_printers:
            printer_lower = printer.lower()

            # Check categories in order
            if any(keyword in printer_lower for keyword in large_format_keywords):
                categories['large_format'].append(printer)
            elif any(keyword in printer_lower for keyword in standard_keywords):
                categories['standard'].append(printer)
            elif any(keyword in printer_lower for keyword in label_keywords):
                categories['label'].append(printer)
            else:
                categories['other'].append(printer)

        log_info("Categorized printers", {
            'large_format': len(categories['large_format']),
            'standard': len(categories['standard']),
            'label': len(categories['label']),
            'other': len(categories['other'])
        })

        return categories

    def validate_configured_printers(self) -> Dict[str, List[str]]:
        """
        Validate that configured printers are available

        Returns:
            Dict with 'available' and 'missing' printer lists
        """
        if not self.config:
            return {'available': [], 'missing': []}

        available = []
        missing = []

        # Check all configured printers
        all_configured = (
            self.config.printers_11x17 +
            self.config.printers_24x36 +
            self.config.printers_folder_label
        )

        for printer_def in all_configured:
            if printer_def.printer_name in self.available_printers:
                printer_def.is_available = True
                printer_def.last_verified = datetime.now().isoformat()
                available.append(printer_def.printer_name)
            else:
                printer_def.is_available = False
                missing.append(printer_def.printer_name)

        if missing:
            log_warning(f"Some configured printers are not available", {
                'missing_count': len(missing),
                'missing_printers': missing
            })
        else:
            log_success("printer_validation", {
                'message': 'All configured printers are available',
                'count': len(available)
            })

        return {'available': available, 'missing': missing}

    def load_config(self) -> bool:
        """
        Load network printer configuration from file

        Returns:
            True if successful, False otherwise
        """
        try:
            config_path = Path(self.config_file)

            if not config_path.exists():
                log_info("No network printer config found, will need initial setup")
                return False

            with open(config_path, 'r') as f:
                data = json.load(f)

            # Parse configuration
            self.config = NetworkPrinterConfig(
                printers_11x17=[
                    PrinterDefinition(**p) for p in data.get('printers_11x17', [])
                ],
                printers_24x36=[
                    PrinterDefinition(**p) for p in data.get('printers_24x36', [])
                ],
                printers_folder_label=[
                    PrinterDefinition(**p) for p in data.get('printers_folder_label', [])
                ],
                template_path=data.get('template_path', ''),
                auto_discover_on_startup=data.get('auto_discover_on_startup', True),
                version=data.get('version', '1.0'),
                last_updated=data.get('last_updated', '')
            )

            log_info("Loaded network printer configuration", {
                'printers_11x17': len(self.config.printers_11x17),
                'printers_24x36': len(self.config.printers_24x36),
                'printers_folder_label': len(self.config.printers_folder_label),
                'template_path': self.config.template_path
            })

            return True

        except Exception as e:
            log_error("load_network_printer_config", e, {
                'config_file': self.config_file
            })
            return False

    def save_config(self) -> bool:
        """
        Save network printer configuration to file

        Returns:
            True if successful, False otherwise
        """
        if not self.config:
            log_error("save_config_no_config", Exception("No config to save"))
            return False

        try:
            # Update timestamp
            self.config.last_updated = datetime.now().isoformat()

            # Save to file
            with open(self.config_file, 'w') as f:
                json.dump(self.config.to_dict(), f, indent=2)

            log_success("save_network_printer_config", {
                'config_file': self.config_file
            })

            return True

        except Exception as e:
            log_error("save_network_printer_config", e, {
                'config_file': self.config_file
            })
            return False

    def create_default_config(self, template_path: str = "") -> bool:
        """
        Create a default configuration with auto-detected printers

        Args:
            template_path: Path to folder label template

        Returns:
            True if successful
        """
        try:
            # Categorize available printers
            categories = self.categorize_printers()

            # Create printer definitions for each category
            printers_11x17 = []
            printers_24x36 = []
            printers_folder_label = []

            # Add standard printers (11x17)
            for i, printer_name in enumerate(categories['standard']):
                printers_11x17.append(PrinterDefinition(
                    display_name=f"11x17 Printer {i+1}",
                    printer_name=printer_name,
                    printer_type="11x17",
                    is_default=(i == 0),  # First one is default
                    is_available=True,
                    description=f"Auto-detected: {printer_name}",
                    last_verified=datetime.now().isoformat()
                ))

            # Add large format printers (24x36)
            for i, printer_name in enumerate(categories['large_format']):
                printers_24x36.append(PrinterDefinition(
                    display_name=f"Large Format Plotter {i+1}",
                    printer_name=printer_name,
                    printer_type="24x36",
                    is_default=(i == 0),
                    is_available=True,
                    description=f"Auto-detected: {printer_name}",
                    last_verified=datetime.now().isoformat()
                ))

            # Add label printers
            for i, printer_name in enumerate(categories['label']):
                printers_folder_label.append(PrinterDefinition(
                    display_name=f"Label Printer {i+1}",
                    printer_name=printer_name,
                    printer_type="folder_label",
                    is_default=(i == 0),
                    is_available=True,
                    description=f"Auto-detected: {printer_name}",
                    last_verified=datetime.now().isoformat()
                ))

            # If no label printers found, check if any standard printer could work
            if not printers_folder_label and categories['other']:
                # Use first "other" printer as potential label printer
                printer_name = categories['other'][0]
                printers_folder_label.append(PrinterDefinition(
                    display_name="Folder Label Printer",
                    printer_name=printer_name,
                    printer_type="folder_label",
                    is_default=True,
                    is_available=True,
                    description=f"Auto-detected (verify): {printer_name}",
                    last_verified=datetime.now().isoformat()
                ))

            # Create configuration
            self.config = NetworkPrinterConfig(
                printers_11x17=printers_11x17,
                printers_24x36=printers_24x36,
                printers_folder_label=printers_folder_label,
                template_path=template_path,
                auto_discover_on_startup=True,
                version="1.0",
                last_updated=datetime.now().isoformat()
            )

            # Save configuration
            success = self.save_config()

            if success:
                log_success("create_default_config", {
                    'printers_11x17': len(printers_11x17),
                    'printers_24x36': len(printers_24x36),
                    'printers_folder_label': len(printers_folder_label)
                })

            return success

        except Exception as e:
            log_error("create_default_config", e)
            return False

    def get_default_printer(self, printer_type: str) -> Optional[PrinterDefinition]:
        """
        Get the default printer for a specific type

        Args:
            printer_type: "11x17", "24x36", or "folder_label"

        Returns:
            PrinterDefinition or None
        """
        if not self.config:
            return None

        printer_list = []
        if printer_type == "11x17":
            printer_list = self.config.printers_11x17
        elif printer_type == "24x36":
            printer_list = self.config.printers_24x36
        elif printer_type == "folder_label":
            printer_list = self.config.printers_folder_label

        # Find default printer
        for printer in printer_list:
            if printer.is_default and printer.is_available:
                return printer

        # If no default or default not available, return first available
        for printer in printer_list:
            if printer.is_available:
                return printer

        # No available printers
        return None

    def get_all_printers_by_type(self, printer_type: str) -> List[PrinterDefinition]:
        """
        Get all printers of a specific type

        Args:
            printer_type: "11x17", "24x36", or "folder_label"

        Returns:
            List of PrinterDefinition objects
        """
        if not self.config:
            return []

        if printer_type == "11x17":
            return self.config.printers_11x17
        elif printer_type == "24x36":
            return self.config.printers_24x36
        elif printer_type == "folder_label":
            return self.config.printers_folder_label

        return []

    def test_printer_connection(self, printer_name: str) -> Tuple[bool, str]:
        """
        Test connection to a specific printer

        Args:
            printer_name: Windows printer name to test

        Returns:
            (success, message) tuple
        """
        try:
            import win32print

            # Try to open printer
            hprinter = win32print.OpenPrinter(printer_name)

            try:
                # Get printer info to verify it's accessible
                printer_info = win32print.GetPrinter(hprinter, 2)

                log_success("test_printer_connection", {
                    'printer_name': printer_name,
                    'status': 'Connected'
                })

                return True, f"Successfully connected to {printer_name}"

            finally:
                win32print.ClosePrinter(hprinter)

        except Exception as e:
            log_error("test_printer_connection", e, {
                'printer_name': printer_name
            })
            return False, f"Failed to connect: {str(e)}"

    def needs_setup(self) -> bool:
        """
        Check if initial setup is needed

        Returns:
            True if setup wizard should run
        """
        if not self.config:
            return True

        # Check if any printer type is configured
        has_11x17 = len(self.config.printers_11x17) > 0
        has_24x36 = len(self.config.printers_24x36) > 0
        has_label = len(self.config.printers_folder_label) > 0
        has_template = bool(self.config.template_path)

        return not (has_11x17 or has_24x36 or has_label) or not has_template

    def get_status_report(self) -> Dict:
        """
        Get comprehensive status report for diagnostics

        Returns:
            Status report dictionary
        """
        report = {
            'config_loaded': self.config is not None,
            'available_printers_count': len(self.available_printers),
            'available_printers': self.available_printers,
            'needs_setup': self.needs_setup()
        }

        if self.config:
            validation = self.validate_configured_printers()
            report.update({
                'configured_11x17': len(self.config.printers_11x17),
                'configured_24x36': len(self.config.printers_24x36),
                'configured_folder_label': len(self.config.printers_folder_label),
                'template_path': self.config.template_path,
                'printers_available': validation['available'],
                'printers_missing': validation['missing'],
                'last_updated': self.config.last_updated
            })

        return report
