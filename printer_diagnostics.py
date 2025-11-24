#!/usr/bin/env python3
"""
Printer Diagnostics Tool - IT troubleshooting utility
Comprehensive diagnostic tool for network printer deployment
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Dict, List
from pathlib import Path
import json

from network_printer_manager import NetworkPrinterManager
from user_preferences import UserPreferencesManager
from error_logger import log_info
from printer_setup_wizard import run_setup_wizard


class PrinterDiagnosticsWindow:
    """Main diagnostics window"""

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Printer Diagnostics & Setup Tool")
        self.window.geometry("900x700")
        self.window.configure(bg='#ecf0f1')

        # Initialize managers
        self.network_manager = NetworkPrinterManager()
        self.user_prefs = UserPreferencesManager()

        self.create_ui()
        self.run_diagnostics()

    def create_ui(self):
        """Create the UI"""
        # Header
        header_frame = tk.Frame(self.window, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text="🔧 Printer Diagnostics & Setup Tool",
            font=("Segoe UI", 20, "bold"),
            bg='#2c3e50',
            fg='white'
        ).pack(pady=20)

        # Main content
        content_frame = tk.Frame(self.window, bg='#ecf0f1')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Tabs
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        self.create_overview_tab()
        self.create_printers_tab()
        self.create_config_tab()
        self.create_test_tab()

        # Action buttons
        button_frame = tk.Frame(self.window, bg='#ecf0f1')
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        tk.Button(
            button_frame,
            text="🔄 Refresh Diagnostics",
            command=self.run_diagnostics,
            font=("Segoe UI", 11),
            bg='#3498db',
            fg='white',
            border=0,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT)

        tk.Button(
            button_frame,
            text="⚙️ Run Setup Wizard",
            command=self.run_wizard,
            font=("Segoe UI", 11),
            bg='#9b59b6',
            fg='white',
            border=0,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=(10, 0))

        tk.Button(
            button_frame,
            text="💾 Export Report",
            command=self.export_report,
            font=("Segoe UI", 11),
            bg='#27ae60',
            fg='white',
            border=0,
            padx=20,
            pady=10
        ).pack(side=tk.RIGHT)

    def create_overview_tab(self):
        """Create overview tab"""
        tab = tk.Frame(self.notebook, bg='#ffffff')
        self.notebook.add(tab, text="Overview")

        self.overview_text = scrolledtext.ScrolledText(
            tab,
            font=("Consolas", 10),
            bg='#ffffff',
            fg='#2c3e50',
            wrap=tk.WORD
        )
        self.overview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_printers_tab(self):
        """Create printers tab"""
        tab = tk.Frame(self.notebook, bg='#ffffff')
        self.notebook.add(tab, text="Available Printers")

        # Treeview for printers
        tree_frame = tk.Frame(tab, bg='#ffffff')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ('Printer Name', 'Status', 'Category', 'Configured')
        self.printers_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)

        for col in columns:
            self.printers_tree.heading(col, text=col)
            self.printers_tree.column(col, width=200)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.printers_tree.yview)
        self.printers_tree.configure(yscrollcommand=scrollbar.set)

        self.printers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Test button
        tk.Button(
            tab,
            text="Test Selected Printer",
            command=self.test_selected_printer,
            font=("Segoe UI", 10),
            bg='#3498db',
            fg='white',
            border=0,
            padx=15,
            pady=8
        ).pack(pady=10)

    def create_config_tab(self):
        """Create configuration tab"""
        tab = tk.Frame(self.notebook, bg='#ffffff')
        self.notebook.add(tab, text="Configuration")

        self.config_text = scrolledtext.ScrolledText(
            tab,
            font=("Consolas", 9),
            bg='#ffffff',
            fg='#2c3e50',
            wrap=tk.WORD
        )
        self.config_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_test_tab(self):
        """Create test tab"""
        tab = tk.Frame(self.notebook, bg='#ffffff')
        self.notebook.add(tab, text="Connection Tests")

        self.test_text = scrolledtext.ScrolledText(
            tab,
            font=("Consolas", 10),
            bg='#ffffff',
            fg='#2c3e50',
            wrap=tk.WORD
        )
        self.test_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Button(
            tab,
            text="Run Connection Tests",
            command=self.run_connection_tests,
            font=("Segoe UI", 11, "bold"),
            bg='#27ae60',
            fg='white',
            border=0,
            padx=20,
            pady=10
        ).pack(pady=10)

    def run_diagnostics(self):
        """Run comprehensive diagnostics"""
        # Refresh managers
        self.network_manager = NetworkPrinterManager()

        # Update overview
        self.update_overview()

        # Update printers list
        self.update_printers_list()

        # Update configuration
        self.update_configuration()

    def update_overview(self):
        """Update overview tab"""
        self.overview_text.delete('1.0', tk.END)

        status = self.network_manager.get_status_report()

        output = "=" * 70 + "\n"
        output += "PRINTER SYSTEM DIAGNOSTIC REPORT\n"
        output += "=" * 70 + "\n\n"

        # System Status
        output += "📊 SYSTEM STATUS\n"
        output += "-" * 70 + "\n"
        output += f"Network Config Loaded: {'✓ YES' if status['config_loaded'] else '✗ NO'}\n"
        output += f"Available Printers: {status['available_printers_count']}\n"
        output += f"Needs Setup: {'⚠️  YES' if status['needs_setup'] else '✓ NO'}\n"
        output += "\n"

        if status['config_loaded']:
            output += "📁 CONFIGURED PRINTERS\n"
            output += "-" * 70 + "\n"
            output += f"11×17 Printers: {status.get('configured_11x17', 0)}\n"
            output += f"24×36 Printers: {status.get('configured_24x36', 0)}\n"
            output += f"Label Printers: {status.get('configured_folder_label', 0)}\n"
            output += f"Template Path: {status.get('template_path', '(not set)')}\n"
            output += "\n"

            if status.get('printers_missing'):
                output += "⚠️  MISSING PRINTERS (CONFIGURED BUT NOT FOUND)\n"
                output += "-" * 70 + "\n"
                for printer in status['printers_missing']:
                    output += f"  ✗ {printer}\n"
                output += "\n"

        # Available printers by category
        categories = self.network_manager.categorize_printers()

        output += "🖨️  AVAILABLE PRINTERS BY CATEGORY\n"
        output += "-" * 70 + "\n"

        category_names = {
            'large_format': '24×36 Large Format',
            'standard': '11×17 Standard',
            'label': 'Label Printers',
            'other': 'Other Printers'
        }

        for category, name in category_names.items():
            printers = categories.get(category, [])
            output += f"\n{name}: ({len(printers)})\n"
            if printers:
                for printer in printers:
                    output += f"  • {printer}\n"
            else:
                output += "  (none)\n"

        output += "\n" + "=" * 70 + "\n"

        if status['needs_setup']:
            output += "\n⚠️  ACTION REQUIRED: Run the Setup Wizard to configure printers\n"
        else:
            output += "\n✓ System is configured and ready for use\n"

        self.overview_text.insert('1.0', output)

    def update_printers_list(self):
        """Update printers list"""
        # Clear existing
        for item in self.printers_tree.get_children():
            self.printers_tree.delete(item)

        # Get all printers
        categories = self.network_manager.categorize_printers()
        all_printers = self.network_manager.available_printers

        # Get configured printers
        configured_printers = set()
        if self.network_manager.config:
            for printer_list in [
                self.network_manager.config.printers_11x17,
                self.network_manager.config.printers_24x36,
                self.network_manager.config.printers_folder_label
            ]:
                configured_printers.update(p.printer_name for p in printer_list)

        # Determine category for each printer
        printer_categories = {}
        for category, printers in categories.items():
            for printer in printers:
                printer_categories[printer] = category

        # Add to tree
        for printer in all_printers:
            category = printer_categories.get(printer, 'other')
            is_configured = '✓ Yes' if printer in configured_printers else '✗ No'

            category_display = {
                'large_format': '24×36',
                'standard': '11×17',
                'label': 'Label',
                'other': 'Other'
            }.get(category, 'Other')

            self.printers_tree.insert('', tk.END, values=(
                printer,
                '✓ Available',
                category_display,
                is_configured
            ))

    def update_configuration(self):
        """Update configuration display"""
        self.config_text.delete('1.0', tk.END)

        output = "=" * 70 + "\n"
        output += "CONFIGURATION FILES\n"
        output += "=" * 70 + "\n\n"

        # Network printer config
        output += "📁 Network Printer Configuration (network_printers.json)\n"
        output += "-" * 70 + "\n"

        config_path = Path("network_printers.json")
        if config_path.exists():
            output += f"Location: {config_path.resolve()}\n"
            output += f"Status: ✓ Exists\n\n"

            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                output += "Content:\n"
                output += json.dumps(config_data, indent=2)
            except Exception as e:
                output += f"Error reading file: {e}\n"
        else:
            output += f"Status: ✗ Not Found\n"
            output += f"Expected Location: {config_path.resolve()}\n"
            output += "⚠️  Run Setup Wizard to create this file\n"

        output += "\n\n"

        # User preferences
        output += "👤 User Preferences (user_preferences.json)\n"
        output += "-" * 70 + "\n"

        prefs_path = Path("user_preferences.json")
        if prefs_path.exists():
            output += f"Location: {prefs_path.resolve()}\n"
            output += f"Status: ✓ Exists\n\n"

            try:
                with open(prefs_path, 'r') as f:
                    prefs_data = json.load(f)
                output += "Content:\n"
                output += json.dumps(prefs_data, indent=2)
            except Exception as e:
                output += f"Error reading file: {e}\n"
        else:
            output += f"Status: ✗ Not Found (will be created on first use)\n"

        self.config_text.insert('1.0', output)

    def test_selected_printer(self):
        """Test connection to selected printer"""
        selection = self.printers_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a printer to test.")
            return

        printer_name = self.printers_tree.item(selection[0])['values'][0]

        # Test connection
        success, message = self.network_manager.test_printer_connection(printer_name)

        if success:
            messagebox.showinfo("Connection Test", message)
        else:
            messagebox.showerror("Connection Test", message)

    def run_connection_tests(self):
        """Run connection tests for all configured printers"""
        self.test_text.delete('1.0', tk.END)

        output = "=" * 70 + "\n"
        output += "PRINTER CONNECTION TESTS\n"
        output += "=" * 70 + "\n\n"

        if not self.network_manager.config:
            output += "⚠️  No configuration found. Run Setup Wizard first.\n"
            self.test_text.insert('1.0', output)
            return

        all_printers = (
            self.network_manager.config.printers_11x17 +
            self.network_manager.config.printers_24x36 +
            self.network_manager.config.printers_folder_label
        )

        output += f"Testing {len(all_printers)} configured printer(s)...\n\n"

        for printer_def in all_printers:
            output += f"Testing: {printer_def.display_name}\n"
            output += f"  Printer Name: {printer_def.printer_name}\n"
            output += f"  Type: {printer_def.printer_type}\n"

            success, message = self.network_manager.test_printer_connection(printer_def.printer_name)

            if success:
                output += f"  Result: ✓ SUCCESS\n"
                output += f"  {message}\n"
            else:
                output += f"  Result: ✗ FAILED\n"
                output += f"  {message}\n"

            output += "\n"

        output += "=" * 70 + "\n"
        output += "Test complete\n"

        self.test_text.insert('1.0', output)

    def run_wizard(self):
        """Run the setup wizard"""
        run_setup_wizard(self.window)
        self.run_diagnostics()  # Refresh after wizard

    def export_report(self):
        """Export diagnostic report to file"""
        try:
            from tkinter import filedialog
            from datetime import datetime

            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                initialfile=f"printer_diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )

            if filename:
                with open(filename, 'w') as f:
                    f.write(self.overview_text.get('1.0', tk.END))
                    f.write("\n\n")
                    f.write("=" * 70 + "\n")
                    f.write("CONFIGURATION\n")
                    f.write("=" * 70 + "\n")
                    f.write(self.config_text.get('1.0', tk.END))

                messagebox.showinfo("Export Complete", f"Report saved to:\n{filename}")

        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export report:\n{str(e)}")

    def run(self):
        """Run the diagnostics window"""
        self.window.mainloop()


def main():
    """Main entry point"""
    app = PrinterDiagnosticsWindow()
    app.run()


if __name__ == "__main__":
    main()
