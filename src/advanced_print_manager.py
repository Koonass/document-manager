#!/usr/bin/env python3
"""
Advanced Print Manager - Large Format Printing Support
Handles multiple printers, paper sizes, and professional printing workflows
"""

import win32print
import win32api
import win32gui
import win32con
import subprocess
import json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import PyPDF2
import tempfile
import os

@dataclass
class PrinterInfo:
    name: str
    max_width: float
    max_height: float
    supported_sizes: List[Tuple[str, float, float]]
    is_large_format: bool
    default_media: str

@dataclass
class PaperSize:
    name: str
    width: float
    height: float
    windows_size_id: int

class AdvancedPrintManager:
    def __init__(self):
        self.printers = {}
        self.paper_sizes = self._initialize_paper_sizes()
        self.discover_printers()

    def _initialize_paper_sizes(self) -> Dict[str, PaperSize]:
        """Initialize standard large format paper sizes"""
        return {
            '11x17': PaperSize('11×17" (Tabloid)', 11.0, 17.0, win32con.DMPAPER_TABLOID),
            '12x18': PaperSize('12×18"', 12.0, 18.0, win32con.DMPAPER_USER),
            '18x24': PaperSize('18×24" (Arch C)', 18.0, 24.0, win32con.DMPAPER_USER),
            '24x36': PaperSize('24×36" (Arch D)', 24.0, 36.0, win32con.DMPAPER_USER),
            '30x42': PaperSize('30×42" (Arch E)', 30.0, 42.0, win32con.DMPAPER_USER),
            'custom': PaperSize('Custom Size', 0.0, 0.0, win32con.DMPAPER_USER)
        }

    def discover_printers(self):
        """Discover available printers and their capabilities"""
        try:
            printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)

            for printer in printers:
                printer_name = printer[2]
                try:
                    # Get printer capabilities
                    printer_info = self._analyze_printer(printer_name)
                    self.printers[printer_name] = printer_info
                    logging.info(f"Discovered printer: {printer_name} - Large Format: {printer_info.is_large_format}")
                except Exception as e:
                    logging.warning(f"Could not analyze printer {printer_name}: {e}")

        except Exception as e:
            logging.error(f"Failed to discover printers: {e}")

    def _analyze_printer(self, printer_name: str) -> PrinterInfo:
        """Analyze printer capabilities"""
        try:
            # Open printer to get device context
            hprinter = win32print.OpenPrinter(printer_name)
            try:
                # Get printer info
                printer_info = win32print.GetPrinter(hprinter, 2)

                # Try to determine if it's a large format printer
                # This is heuristic - based on common large format printer names/drivers
                driver_name = printer_info.get('pDriverName', '').lower()
                printer_lower = printer_name.lower()

                is_large_format = any(keyword in printer_lower or keyword in driver_name
                                    for keyword in ['designjet', 'imageprograf', 'plotter',
                                                  'wide', 'format', 'cad', 'engineering'])

                # Estimate max paper size based on printer type
                if is_large_format:
                    max_width, max_height = 36.0, 48.0  # Typical large format max
                    supported_sizes = [
                        ('11×17"', 11.0, 17.0),
                        ('18×24"', 18.0, 24.0),
                        ('24×36"', 24.0, 36.0),
                        ('30×42"', 30.0, 42.0)
                    ]
                    default_media = 'Bond Paper'
                else:
                    max_width, max_height = 11.0, 17.0  # Standard printer max
                    supported_sizes = [
                        ('8.5×11"', 8.5, 11.0),
                        ('11×17"', 11.0, 17.0)
                    ]
                    default_media = 'Plain Paper'

                return PrinterInfo(
                    name=printer_name,
                    max_width=max_width,
                    max_height=max_height,
                    supported_sizes=supported_sizes,
                    is_large_format=is_large_format,
                    default_media=default_media
                )

            finally:
                win32print.ClosePrinter(hprinter)

        except Exception as e:
            logging.warning(f"Could not get detailed info for {printer_name}: {e}")
            # Fallback - assume standard printer
            return PrinterInfo(
                name=printer_name,
                max_width=11.0,
                max_height=17.0,
                supported_sizes=[('11×17"', 11.0, 17.0)],
                is_large_format=False,
                default_media='Plain Paper'
            )

    def get_pdf_dimensions(self, pdf_path: str) -> Tuple[float, float]:
        """Get PDF dimensions in inches"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page = pdf_reader.pages[0]

                # Get page dimensions in points (1/72 inch)
                mediabox = page.mediabox
                width_points = float(mediabox.width)
                height_points = float(mediabox.height)

                # Convert to inches
                width_inches = width_points / 72.0
                height_inches = height_points / 72.0

                return width_inches, height_inches

        except Exception as e:
            logging.warning(f"Could not determine PDF dimensions for {pdf_path}: {e}")
            return 11.0, 17.0  # Default assumption

    def suggest_optimal_printer_and_size(self, pdf_path: str) -> Tuple[Optional[str], Optional[str]]:
        """Suggest the best printer and paper size for a PDF"""
        pdf_width, pdf_height = self.get_pdf_dimensions(pdf_path)

        # Find printers that can handle this size
        suitable_printers = []
        for printer_name, printer_info in self.printers.items():
            if (pdf_width <= printer_info.max_width and
                pdf_height <= printer_info.max_height):
                suitable_printers.append((printer_name, printer_info))

        if not suitable_printers:
            return None, None

        # Prefer large format printers for large documents
        large_format_printers = [p for p in suitable_printers if p[1].is_large_format]
        if large_format_printers and (pdf_width > 11.0 or pdf_height > 17.0):
            best_printer = large_format_printers[0][0]
        else:
            best_printer = suitable_printers[0][0]

        # Suggest paper size
        best_size = self._suggest_paper_size(pdf_width, pdf_height)

        return best_printer, best_size

    def _suggest_paper_size(self, width: float, height: float) -> str:
        """Suggest the best paper size for given dimensions"""
        # Add some margin (0.5 inches)
        required_width = width + 0.5
        required_height = height + 0.5

        # Check standard sizes
        size_options = [
            ('11x17', 11.0, 17.0),
            ('18x24', 18.0, 24.0),
            ('24x36', 24.0, 36.0),
            ('30x42', 30.0, 42.0)
        ]

        for size_key, size_width, size_height in size_options:
            if required_width <= size_width and required_height <= size_height:
                return size_key

        return 'custom'

    def open_print_dialog(self, pdf_files: List[str], parent_window=None):
        """Open advanced print dialog for multiple PDFs"""
        if not pdf_files:
            messagebox.showwarning("No Files", "No PDF files to print")
            return

        dialog = AdvancedPrintDialog(parent_window, self, pdf_files)
        return dialog.show()

class AdvancedPrintDialog:
    def __init__(self, parent, print_manager: AdvancedPrintManager, pdf_files: List[str]):
        self.parent = parent
        self.print_manager = print_manager
        self.pdf_files = pdf_files
        self.result = None

    def show(self):
        """Show the advanced print dialog"""
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("Advanced Print Settings")
        self.window.geometry("600x500")
        self.window.configure(bg='#ecf0f1')

        if self.parent:
            self.window.transient(self.parent)
            self.window.grab_set()

        self.create_dialog()

        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.window.winfo_screenheight() // 2) - (500 // 2)
        self.window.geometry(f"600x500+{x}+{y}")

        self.window.wait_window()
        return self.result

    def create_dialog(self):
        """Create the print dialog interface"""
        # Header
        header_frame = tk.Frame(self.window, bg='#34495e', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text=f"🖨️ Print {len(self.pdf_files)} PDF(s)",
            font=("Segoe UI", 16, "bold"),
            bg='#34495e',
            fg='white'
        ).pack(expand=True)

        # Main content
        content_frame = tk.Frame(self.window, bg='#ecf0f1')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Printer selection
        printer_frame = ttk.LabelFrame(content_frame, text="Printer Selection", padding=15)
        printer_frame.pack(fill=tk.X, pady=(0, 10))

        self.printer_var = tk.StringVar()
        printer_combo = ttk.Combobox(
            printer_frame,
            textvariable=self.printer_var,
            values=list(self.print_manager.printers.keys()),
            state='readonly',
            width=50
        )
        printer_combo.pack(fill=tk.X)

        # Set default printer
        if self.print_manager.printers:
            # Try to suggest optimal printer for first PDF
            suggested_printer, suggested_size = self.print_manager.suggest_optimal_printer_and_size(self.pdf_files[0])
            if suggested_printer:
                self.printer_var.set(suggested_printer)
            else:
                self.printer_var.set(list(self.print_manager.printers.keys())[0])

        # Paper size selection
        size_frame = ttk.LabelFrame(content_frame, text="Paper Size", padding=15)
        size_frame.pack(fill=tk.X, pady=(0, 10))

        self.size_var = tk.StringVar()
        size_combo = ttk.Combobox(
            size_frame,
            textvariable=self.size_var,
            values=[f"{size.name} ({size.width}×{size.height}\")"
                   for size in self.print_manager.paper_sizes.values()],
            state='readonly',
            width=50
        )
        size_combo.pack(fill=tk.X)

        # Set suggested size
        if 'suggested_size' in locals() and suggested_size:
            size_info = self.print_manager.paper_sizes[suggested_size]
            self.size_var.set(f"{size_info.name} ({size_info.width}×{size_info.height}\")")

        # Print options
        options_frame = ttk.LabelFrame(content_frame, text="Print Options", padding=15)
        options_frame.pack(fill=tk.X, pady=(0, 10))

        self.scale_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Scale to fit paper (recommended for plots)",
            variable=self.scale_var
        ).pack(anchor=tk.W)

        self.auto_rotate_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Auto-rotate for optimal fit",
            variable=self.auto_rotate_var
        ).pack(anchor=tk.W)

        # File preview
        files_frame = ttk.LabelFrame(content_frame, text="Files to Print", padding=15)
        files_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Create listbox with scrollbar
        list_frame = tk.Frame(files_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.files_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Segoe UI", 9)
        )
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.files_listbox.yview)

        # Populate file list with dimensions
        for pdf_file in self.pdf_files:
            filename = Path(pdf_file).name
            try:
                width, height = self.print_manager.get_pdf_dimensions(pdf_file)
                self.files_listbox.insert(tk.END, f"{filename} ({width:.1f}×{height:.1f}\")")
            except:
                self.files_listbox.insert(tk.END, filename)

        # Buttons
        button_frame = tk.Frame(content_frame, bg='#ecf0f1')
        button_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel,
            font=("Segoe UI", 10),
            bg='#95a5a6',
            fg='white',
            border=0,
            padx=20,
            pady=8
        ).pack(side=tk.RIGHT)

        tk.Button(
            button_frame,
            text="🖨️ Print All",
            command=self.print_files,
            font=("Segoe UI", 11, "bold"),
            bg='#27ae60',
            fg='white',
            border=0,
            padx=25,
            pady=8
        ).pack(side=tk.RIGHT, padx=(0, 10))

    def print_files(self):
        """Execute the print job"""
        if not self.printer_var.get():
            messagebox.showwarning("No Printer", "Please select a printer")
            return

        # Prepare print settings
        print_settings = {
            'printer': self.printer_var.get(),
            'paper_size': self.size_var.get(),
            'scale_to_fit': self.scale_var.get(),
            'auto_rotate': self.auto_rotate_var.get()
        }

        self.result = {
            'action': 'print',
            'settings': print_settings,
            'files': self.pdf_files
        }

        self.window.destroy()

    def cancel(self):
        """Cancel the print dialog"""
        self.result = None
        self.window.destroy()

# Example usage and integration functions
def enhanced_print_pdfs(pdf_files: List[str], parent_window=None) -> bool:
    """Enhanced printing function for integration with existing code"""
    try:
        print_manager = AdvancedPrintManager()
        result = print_manager.open_print_dialog(pdf_files, parent_window)

        if result and result['action'] == 'print':
            # Execute the actual printing
            success_count = 0
            for pdf_file in result['files']:
                try:
                    # Use advanced printing logic here
                    # For now, fallback to system default with selected printer
                    printer = result['settings']['printer']

                    # Use Windows printing with specific printer
                    win32print.SetDefaultPrinter(printer)
                    win32api.ShellExecute(0, "print", pdf_file, None, ".", 0)
                    success_count += 1

                except Exception as e:
                    logging.error(f"Failed to print {pdf_file}: {e}")

            return success_count > 0

        return False

    except Exception as e:
        logging.error(f"Enhanced printing failed: {e}")
        messagebox.showerror("Print Error", f"Printing failed: {str(e)}")
        return False

def batch_print_with_configs(print_jobs: List[Dict], parent_window=None) -> bool:
    """
    Execute batch printing with individual printer configurations for each job

    Args:
        print_jobs: List of dicts with keys: pdf_path, printer_name, color_mode, copies, order_number
        parent_window: Parent window for dialogs

    Returns:
        True if successful, False otherwise
    """
    try:
        if not print_jobs:
            messagebox.showwarning("No Print Jobs", "No print jobs configured.")
            return False

        # Show confirmation dialog with details
        dialog = tk.Toplevel(parent_window) if parent_window else tk.Tk()
        dialog.title("Batch Print Confirmation")
        dialog.geometry("650x500")
        dialog.configure(bg='#ecf0f1')

        if parent_window:
            dialog.transient(parent_window)
            dialog.grab_set()

        # Header
        header_frame = tk.Frame(dialog, bg='#34495e', height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text=f"🖨️ Batch Print: {len(print_jobs)} Orders",
            font=("Segoe UI", 18, "bold"),
            bg='#34495e',
            fg='white'
        ).pack(expand=True)

        # Content
        content_frame = tk.Frame(dialog, bg='#ecf0f1')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Job list
        jobs_frame = ttk.LabelFrame(content_frame, text="Print Jobs", padding=10)
        jobs_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Create treeview for jobs
        tree_frame = tk.Frame(jobs_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('Order', 'Printer', 'Mode', 'Copies')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        for job in print_jobs:
            tree.insert('', tk.END, values=(
                job['order_number'],
                job['printer_name'][:30],  # Truncate long printer names
                job['color_mode'],
                job['copies']
            ))

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Summary
        summary_text = f"Total: {len(print_jobs)} orders\n"
        summary_text += f"Total copies: {sum(job['copies'] for job in print_jobs)}"

        summary_label = tk.Label(
            content_frame,
            text=summary_text,
            font=("Segoe UI", 10),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        summary_label.pack(pady=(0, 15))

        # Result variable
        result = {'confirmed': False}

        def confirm_print():
            result['confirmed'] = True
            dialog.destroy()

        def cancel_print():
            result['confirmed'] = False
            dialog.destroy()

        # Buttons
        button_frame = tk.Frame(content_frame, bg='#ecf0f1')
        button_frame.pack(fill=tk.X)

        tk.Button(
            button_frame,
            text="Cancel",
            command=cancel_print,
            font=("Segoe UI", 11),
            bg='#95a5a6',
            fg='white',
            border=0,
            padx=25,
            pady=10
        ).pack(side=tk.RIGHT)

        tk.Button(
            button_frame,
            text="🖨️ Start Printing",
            command=confirm_print,
            font=("Segoe UI", 11, "bold"),
            bg='#27ae60',
            fg='white',
            border=0,
            padx=25,
            pady=10
        ).pack(side=tk.RIGHT, padx=(0, 10))

        # Center the window
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (650 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"650x500+{x}+{y}")

        dialog.wait_window()

        if not result['confirmed']:
            return False

        # Execute printing
        successful = 0
        failed = 0

        for job in print_jobs:
            try:
                pdf_path = job['pdf_path']
                printer_name = job['printer_name']
                copies = job['copies']

                # Print each copy
                for copy_num in range(copies):
                    try:
                        # Set the printer
                        win32print.SetDefaultPrinter(printer_name)

                        # Print the PDF
                        win32api.ShellExecute(
                            0,
                            "print",
                            pdf_path,
                            None,
                            ".",
                            0  # SW_HIDE
                        )

                        logging.info(f"Sent to printer: {job['order_number']} (copy {copy_num + 1}/{copies}) on {printer_name}")

                    except Exception as e:
                        logging.error(f"Failed to print copy {copy_num + 1} of {job['order_number']}: {e}")
                        failed += 1
                        continue

                successful += 1

            except Exception as e:
                logging.error(f"Failed to process print job for {job['order_number']}: {e}")
                failed += 1

        # Show results
        if successful > 0:
            return True
        else:
            return False

    except Exception as e:
        logging.error(f"Batch print with configs failed: {e}")
        messagebox.showerror("Batch Print Error", f"Batch printing failed:\n{str(e)}")
        return False

if __name__ == "__main__":
    # Test the print manager
    root = tk.Tk()
    root.withdraw()  # Hide main window

    print_manager = AdvancedPrintManager()
    print("Available printers:")
    for name, info in print_manager.printers.items():
        print(f"  {name} - Large Format: {info.is_large_format}")

    root.destroy()