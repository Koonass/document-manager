#!/usr/bin/env python3
"""
CSV Cleanup Dialog - UI for validating and managing BisTrack CSV imports
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
from pathlib import Path
from typing import List, Dict, Optional
import json

from csv_processor import CSVProcessor
from csv_validator import CSVValidator, ValidationError
from enhanced_database_manager import EnhancedDatabaseManager


class CSVCleanupDialog:
    """Dialog for validating and cleaning CSV files before BisTrack import"""

    def __init__(self, parent, db_manager: EnhancedDatabaseManager,
                 csv_folder: str, products_file: Optional[str] = None):
        """
        Initialize CSV cleanup dialog

        Args:
            parent: Parent tkinter window
            db_manager: Database manager instance
            csv_folder: Path to folder containing CSV files
            products_file: Path to products master file for SKU validation
        """
        self.parent = parent
        self.db_manager = db_manager
        self.csv_folder = Path(csv_folder)
        self.products_file = Path(products_file) if products_file else None

        self.processor = CSVProcessor()
        self.validator = CSVValidator(self.products_file)

        self.csv_files = []  # List of CSV files found
        self.selected_file = None
        self.validation_results = {}  # Map: csv_path -> validation errors

        self.create_dialog()
        self.scan_csv_files()

    def create_dialog(self):
        """Create the dialog window"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("BisTrack CSV Cleanup & Validation")
        self.dialog.geometry("1000x700")
        self.dialog.configure(bg='#ecf0f1')
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Header
        header_frame = tk.Frame(self.dialog, bg='#34495e', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        header_label = tk.Label(
            header_frame,
            text="BisTrack CSV Import Manager",
            font=("Segoe UI", 14, "bold"),
            bg='#34495e',
            fg='white'
        )
        header_label.pack(expand=True)

        # Main container with two panels
        main_container = tk.Frame(self.dialog, bg='#ecf0f1')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel - CSV file list
        left_frame = ttk.LabelFrame(main_container, text="CSV Files", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # CSV list with scrollbar
        list_container = tk.Frame(left_frame)
        list_container.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.csv_listbox = tk.Listbox(
            list_container,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 9),
            selectmode=tk.SINGLE,
            height=20
        )
        self.csv_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.csv_listbox.yview)

        self.csv_listbox.bind('<<ListboxSelect>>', self.on_csv_selected)

        # Buttons for CSV list
        list_buttons_frame = tk.Frame(left_frame, bg='#ecf0f1')
        list_buttons_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Button(
            list_buttons_frame,
            text="🔄 Refresh",
            command=self.scan_csv_files,
            font=("Segoe UI", 9),
            bg='#3498db',
            fg='white',
            border=0,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            list_buttons_frame,
            text="✓ Validate All",
            command=self.validate_all,
            font=("Segoe UI", 9),
            bg='#2ecc71',
            fg='white',
            border=0,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=(0, 5))

        # Right panel - Validation details
        right_frame = ttk.LabelFrame(main_container, text="Validation Details", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # File info frame
        info_frame = tk.Frame(right_frame, bg='white', relief=tk.RIDGE, borderwidth=1)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        self.file_info_label = tk.Label(
            info_frame,
            text="Select a CSV file to view validation details",
            font=("Segoe UI", 9),
            bg='white',
            fg='#7f8c8d',
            justify=tk.LEFT,
            anchor=tk.W,
            padx=10,
            pady=10
        )
        self.file_info_label.pack(fill=tk.X)

        # Validation status frame
        status_frame = tk.Frame(right_frame, bg='white', relief=tk.RIDGE, borderwidth=1)
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.status_label = tk.Label(
            status_frame,
            text="",
            font=("Segoe UI", 10, "bold"),
            bg='white',
            justify=tk.LEFT,
            anchor=tk.W,
            padx=10,
            pady=10
        )
        self.status_label.pack(fill=tk.X)

        # Validation errors list
        errors_container = tk.Frame(right_frame)
        errors_container.pack(fill=tk.BOTH, expand=True)

        errors_scrollbar_y = ttk.Scrollbar(errors_container)
        errors_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        errors_scrollbar_x = ttk.Scrollbar(errors_container, orient=tk.HORIZONTAL)
        errors_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.errors_text = tk.Text(
            errors_container,
            wrap=tk.NONE,
            font=("Consolas", 9),
            yscrollcommand=errors_scrollbar_y.set,
            xscrollcommand=errors_scrollbar_x.set,
            height=15
        )
        self.errors_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        errors_scrollbar_y.config(command=self.errors_text.yview)
        errors_scrollbar_x.config(command=self.errors_text.xview)

        # Configure text tags for colored output
        self.errors_text.tag_configure('error', foreground='#e74c3c', font=("Consolas", 9, "bold"))
        self.errors_text.tag_configure('warning', foreground='#f39c12', font=("Consolas", 9, "bold"))
        self.errors_text.tag_configure('info', foreground='#3498db', font=("Consolas", 9, "italic"))
        self.errors_text.tag_configure('success', foreground='#27ae60', font=("Consolas", 9, "bold"))

        # Action buttons for selected file
        action_buttons_frame = tk.Frame(right_frame, bg='#ecf0f1')
        action_buttons_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Button(
            action_buttons_frame,
            text="✓ Validate",
            command=self.validate_selected,
            font=("Segoe UI", 9),
            bg='#2ecc71',
            fg='white',
            border=0,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            action_buttons_frame,
            text="🔧 Auto-Fix",
            command=self.auto_fix_selected,
            font=("Segoe UI", 9),
            bg='#f39c12',
            fg='white',
            border=0,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            action_buttons_frame,
            text="📤 Upload to BisTrack",
            command=self.upload_selected,
            font=("Segoe UI", 9),
            bg='#9b59b6',
            fg='white',
            border=0,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=(0, 5))

        # Bottom button frame
        bottom_frame = tk.Frame(self.dialog, bg='#ecf0f1')
        bottom_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        tk.Button(
            bottom_frame,
            text="Close",
            command=self.dialog.destroy,
            font=("Segoe UI", 10),
            bg='#95a5a6',
            fg='white',
            border=0,
            padx=20,
            pady=8
        ).pack(side=tk.RIGHT)

    def scan_csv_files(self):
        """Scan folder for CSV files and populate list"""
        try:
            self.csv_files = []
            self.csv_listbox.delete(0, tk.END)

            if not self.csv_folder.exists():
                messagebox.showerror("Error", f"CSV folder not found: {self.csv_folder}")
                return

            # Find all CSV files
            for csv_file in self.csv_folder.glob('*.csv'):
                if csv_file.is_file():
                    # Extract order number
                    order_number = self.processor.extract_sales_order(csv_file)

                    # Get database status
                    db_status = self.db_manager.get_csv_files_by_order(order_number) if order_number else []

                    file_info = {
                        'path': csv_file,
                        'filename': csv_file.name,
                        'order_number': order_number,
                        'db_status': db_status[0]['status'] if db_status else 'not_tracked',
                        'validation_status': db_status[0]['validation_status'] if db_status else 'not_validated'
                    }

                    self.csv_files.append(file_info)

                    # Format list display
                    status_icon = self._get_status_icon(file_info['validation_status'])
                    display_text = f"{status_icon} {csv_file.name:<40} Order: {order_number or 'N/A'}"
                    self.csv_listbox.insert(tk.END, display_text)

            logging.info(f"Found {len(self.csv_files)} CSV files")

        except Exception as e:
            logging.error(f"Error scanning CSV files: {e}")
            messagebox.showerror("Error", f"Failed to scan CSV files: {e}")

    def _get_status_icon(self, validation_status: str) -> str:
        """Get status icon based on validation status"""
        icons = {
            'not_validated': '⚪',
            'valid': '✅',
            'has_errors': '❌',
            'has_warnings': '⚠️'
        }
        return icons.get(validation_status, '⚪')

    def on_csv_selected(self, event):
        """Handle CSV file selection"""
        selection = self.csv_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        self.selected_file = self.csv_files[index]

        # Display file info
        file_info = f"File: {self.selected_file['filename']}\n"
        file_info += f"Order: {self.selected_file['order_number'] or 'Not found'}\n"
        file_info += f"Status: {self.selected_file['db_status']}\n"
        file_info += f"Validation: {self.selected_file['validation_status']}"

        self.file_info_label.config(text=file_info)

        # Check if already validated
        csv_path = str(self.selected_file['path'])
        if csv_path in self.validation_results:
            self.display_validation_results(self.validation_results[csv_path])
        else:
            self.errors_text.delete('1.0', tk.END)
            self.errors_text.insert('1.0', "Click 'Validate' to check this file for errors")
            self.status_label.config(text="Not yet validated", fg='#95a5a6')

    def validate_selected(self):
        """Validate the selected CSV file"""
        if not self.selected_file:
            messagebox.showwarning("No Selection", "Please select a CSV file first")
            return

        try:
            csv_path = self.selected_file['path']

            # Validate the CSV
            errors = self.validator.validate_csv(csv_path, strict_mode=False)

            # Store results
            self.validation_results[str(csv_path)] = errors

            # Update database
            if errors:
                error_count = len([e for e in errors if e.severity == ValidationError.ERROR])
                warning_count = len([e for e in errors if e.severity == ValidationError.WARNING])

                if error_count > 0:
                    validation_status = 'has_errors'
                elif warning_count > 0:
                    validation_status = 'has_warnings'
                else:
                    validation_status = 'valid'
            else:
                validation_status = 'valid'

            # Serialize errors for database
            errors_data = [{
                'line': e.line_number,
                'severity': e.severity,
                'field': e.field,
                'message': e.message,
                'current_value': str(e.current_value),
                'suggested_fix': e.suggested_fix
            } for e in errors]

            self.db_manager.update_csv_validation(
                str(csv_path),
                validation_status,
                errors_data
            )

            # Display results
            self.display_validation_results(errors)

            # Update list display
            self.scan_csv_files()

        except Exception as e:
            logging.error(f"Error validating CSV: {e}")
            messagebox.showerror("Validation Error", f"Failed to validate CSV: {e}")

    def display_validation_results(self, errors: List[ValidationError]):
        """Display validation results in the text widget"""
        self.errors_text.delete('1.0', tk.END)

        if not errors:
            self.errors_text.insert('1.0', "✅ No issues found - CSV is valid and ready to upload!\n", 'success')
            self.status_label.config(text="✅ Valid - Ready to Upload", fg='#27ae60')
            return

        # Group by severity
        errors_list = [e for e in errors if e.severity == ValidationError.ERROR]
        warnings_list = [e for e in errors if e.severity == ValidationError.WARNING]
        info_list = [e for e in errors if e.severity == ValidationError.INFO]

        # Display summary
        summary = f"Total Issues: {len(errors)}\n"
        summary += f"  Errors: {len(errors_list)} (must fix)\n"
        summary += f"  Warnings: {len(warnings_list)} (recommended)\n"
        summary += f"  Info: {len(info_list)} (informational)\n\n"

        self.errors_text.insert(tk.END, summary)

        # Update status label
        if errors_list:
            self.status_label.config(text=f"❌ {len(errors_list)} Errors - Cannot Upload", fg='#e74c3c')
        elif warnings_list:
            self.status_label.config(text=f"⚠️ {len(warnings_list)} Warnings - Can Upload", fg='#f39c12')
        else:
            self.status_label.config(text=f"ℹ️ {len(info_list)} Info - Can Upload", fg='#3498db')

        # Display errors
        if errors_list:
            self.errors_text.insert(tk.END, "ERRORS (Must Fix):\n", 'error')
            self.errors_text.insert(tk.END, "-" * 80 + "\n")
            for error in errors_list[:20]:  # Show first 20
                self.errors_text.insert(tk.END, f"Line {error.line_number}: {error.field}\n")
                self.errors_text.insert(tk.END, f"  ✗ {error.message}\n", 'error')
                if error.suggested_fix:
                    self.errors_text.insert(tk.END, f"  → Fix: {error.suggested_fix}\n", 'info')
                self.errors_text.insert(tk.END, "\n")

            if len(errors_list) > 20:
                self.errors_text.insert(tk.END, f"  ... and {len(errors_list) - 20} more errors\n\n")

        # Display warnings
        if warnings_list:
            self.errors_text.insert(tk.END, "WARNINGS (Recommended to Fix):\n", 'warning')
            self.errors_text.insert(tk.END, "-" * 80 + "\n")
            for warning in warnings_list[:10]:  # Show first 10
                self.errors_text.insert(tk.END, f"Line {warning.line_number}: {warning.field}\n")
                self.errors_text.insert(tk.END, f"  ⚠ {warning.message}\n", 'warning')
                if warning.suggested_fix:
                    self.errors_text.insert(tk.END, f"  → Fix: {warning.suggested_fix}\n", 'info')
                self.errors_text.insert(tk.END, "\n")

            if len(warnings_list) > 10:
                self.errors_text.insert(tk.END, f"  ... and {len(warnings_list) - 10} more warnings\n\n")

    def auto_fix_selected(self):
        """Auto-fix errors in selected CSV"""
        if not self.selected_file:
            messagebox.showwarning("No Selection", "Please select a CSV file first")
            return

        csv_path = self.selected_file['path']

        # Check if validated
        if str(csv_path) not in self.validation_results:
            messagebox.showinfo("Not Validated", "Please validate the file first before auto-fixing")
            return

        errors = self.validation_results[str(csv_path)]

        # Check if there are fixable errors
        fixable_errors = [e for e in errors if e.suggested_fix]

        if not fixable_errors:
            messagebox.showinfo("No Fixes Available", "No automatic fixes are available for this file")
            return

        # Confirm with user
        response = messagebox.askyesno(
            "Auto-Fix Confirmation",
            f"Apply {len(fixable_errors)} automatic fixes?\n\n"
            "A new file will be created with '_cleaned' suffix."
        )

        if not response:
            return

        try:
            # Apply fixes
            fixed_path = self.validator.auto_fix_errors(csv_path, errors)

            messagebox.showinfo(
                "Success",
                f"Created cleaned file:\n{fixed_path.name}\n\n"
                "Please review the cleaned file before uploading."
            )

            # Refresh list
            self.scan_csv_files()

        except Exception as e:
            logging.error(f"Error auto-fixing CSV: {e}")
            messagebox.showerror("Auto-Fix Error", f"Failed to fix CSV: {e}")

    def validate_all(self):
        """Validate all CSV files"""
        if not self.csv_files:
            messagebox.showinfo("No Files", "No CSV files found to validate")
            return

        progress_dialog = tk.Toplevel(self.dialog)
        progress_dialog.title("Validating CSVs...")
        progress_dialog.geometry("400x150")
        progress_dialog.transient(self.dialog)
        progress_dialog.grab_set()

        tk.Label(
            progress_dialog,
            text="Validating CSV files...",
            font=("Segoe UI", 11)
        ).pack(pady=20)

        progress_var = tk.StringVar(value="0 / 0")
        progress_label = tk.Label(progress_dialog, textvariable=progress_var, font=("Segoe UI", 10))
        progress_label.pack(pady=10)

        progress_bar = ttk.Progressbar(progress_dialog, length=300, mode='determinate')
        progress_bar.pack(pady=10)

        total = len(self.csv_files)
        progress_bar['maximum'] = total

        for i, file_info in enumerate(self.csv_files):
            csv_path = file_info['path']

            # Validate
            errors = self.validator.validate_csv(csv_path, strict_mode=False)
            self.validation_results[str(csv_path)] = errors

            # Update database
            if errors:
                error_count = len([e for e in errors if e.severity == ValidationError.ERROR])
                warning_count = len([e for e in errors if e.severity == ValidationError.WARNING])

                if error_count > 0:
                    validation_status = 'has_errors'
                elif warning_count > 0:
                    validation_status = 'has_warnings'
                else:
                    validation_status = 'valid'
            else:
                validation_status = 'valid'

            errors_data = [{
                'line': e.line_number,
                'severity': e.severity,
                'field': e.field,
                'message': e.message
            } for e in errors]

            self.db_manager.update_csv_validation(str(csv_path), validation_status, errors_data)

            # Update progress
            progress_bar['value'] = i + 1
            progress_var.set(f"{i + 1} / {total}")
            progress_dialog.update()

        progress_dialog.destroy()

        # Refresh list
        self.scan_csv_files()

        messagebox.showinfo("Validation Complete", f"Validated {total} CSV files")

    def upload_selected(self):
        """Upload selected CSV to BisTrack import folder"""
        if not self.selected_file:
            messagebox.showwarning("No Selection", "Please select a CSV file first")
            return

        # Check validation status
        csv_path = str(self.selected_file['path'])
        if csv_path not in self.validation_results:
            messagebox.showwarning("Not Validated", "Please validate the file first")
            return

        errors = self.validation_results[csv_path]
        error_count = len([e for e in errors if e.severity == ValidationError.ERROR])

        if error_count > 0:
            messagebox.showerror(
                "Cannot Upload",
                f"CSV has {error_count} errors that must be fixed first.\n\n"
                "Use 'Auto-Fix' or manually correct the errors."
            )
            return

        # Get BisTrack import folder from settings
        # For now, show file dialog
        import_folder = filedialog.askdirectory(
            title="Select BisTrack Import Folder",
            initialdir=self.csv_folder
        )

        if not import_folder:
            return

        try:
            import shutil

            source = Path(csv_path)
            destination = Path(import_folder) / source.name

            # Copy file
            shutil.copy2(source, destination)

            # Mark as uploaded in database
            self.db_manager.mark_csv_uploaded(csv_path)

            messagebox.showinfo(
                "Upload Successful",
                f"CSV uploaded to:\n{destination}\n\n"
                "The file is ready for BisTrack import."
            )

            # Refresh
            self.scan_csv_files()

        except Exception as e:
            logging.error(f"Error uploading CSV: {e}")
            messagebox.showerror("Upload Error", f"Failed to upload CSV: {e}")


def show_csv_cleanup_dialog(parent, db_manager, csv_folder, products_file=None):
    """
    Show the CSV cleanup dialog

    Args:
        parent: Parent tkinter window
        db_manager: Database manager instance
        csv_folder: Path to folder containing CSV files
        products_file: Path to products master file
    """
    dialog = CSVCleanupDialog(parent, db_manager, csv_folder, products_file)
    parent.wait_window(dialog.dialog)
