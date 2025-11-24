#!/usr/bin/env python3
"""
Network Batch Print - Updated batch printing system using network printer configuration
Replaces the old preset system with centralized network printer management
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Callable, Optional
import logging
import os
import threading
import time
from network_printer_manager import NetworkPrinterManager, PrinterDefinition
from user_preferences import UserPreferencesManager
from error_logger import log_error, log_info, log_warning, log_success


class PrintJobConfigDialog(tk.Toplevel):
    """Dialog for configuring a batch print job using network printers"""

    def __init__(self, parent, network_manager: NetworkPrinterManager,
                 user_prefs: UserPreferencesManager, order_count: int):
        super().__init__(parent)
        self.parent_window = parent
        self.network_manager = network_manager
        self.user_prefs = user_prefs
        self.order_count = order_count
        self.result = None

        self.setup_window()

    def setup_window(self):
        """Create the print job configuration window"""
        self.title("Configure Print Job")
        self.geometry("600x700")
        self.configure(bg='#ecf0f1')
        self.transient(self.parent_window)
        self.grab_set()

        # Header
        header_frame = tk.Frame(self, bg='#34495e', height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text=f"Print Configuration - {self.order_count} orders",
            font=("Segoe UI", 16, "bold"),
            bg='#34495e',
            fg='white'
        ).pack(expand=True)

        # Content
        content_frame = tk.Frame(self, bg='#ecf0f1')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Scrollable content
        canvas = tk.Canvas(content_frame, bg='#ecf0f1', highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#ecf0f1')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 11x17 Printer Section
        self.create_printer_section(
            scrollable_frame,
            "11×17 Printer",
            "11x17",
            "Standard size plots"
        )

        # 24x36 Printer Section
        self.create_printer_section(
            scrollable_frame,
            "24×36 Printer",
            "24x36",
            "Large format plots"
        )

        # Folder Label Section
        self.create_printer_section(
            scrollable_frame,
            "Folder Label Printer",
            "folder_label",
            "Folder labels (auto-skips processed orders)"
        )

        # Buttons
        button_frame = tk.Frame(self, bg='#ecf0f1')
        button_frame.pack(fill=tk.X, padx=30, pady=(0, 20))

        tk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel,
            font=("Segoe UI", 11),
            bg='#95a5a6',
            fg='white',
            border=0,
            padx=25,
            pady=10
        ).pack(side=tk.RIGHT)

        tk.Button(
            button_frame,
            text="Start Printing",
            command=self.confirm,
            font=("Segoe UI", 11, "bold"),
            bg='#27ae60',
            fg='white',
            border=0,
            padx=25,
            pady=10
        ).pack(side=tk.RIGHT, padx=(0, 10))

    def create_printer_section(self, parent, title: str, printer_type: str, description: str):
        """Create a printer configuration section"""
        section_frame = tk.Frame(parent, bg='#ffffff', relief='solid', borderwidth=1)
        section_frame.pack(fill=tk.X, pady=(0, 15))

        # Section header
        tk.Label(
            section_frame,
            text=title,
            font=("Segoe UI", 12, "bold"),
            bg='#ffffff',
            fg='#2c3e50'
        ).pack(anchor=tk.W, padx=15, pady=(15, 5))

        tk.Label(
            section_frame,
            text=description,
            font=("Segoe UI", 9),
            bg='#ffffff',
            fg='#7f8c8d'
        ).pack(anchor=tk.W, padx=15, pady=(0, 10))

        # Enable checkbox
        enabled_var = tk.BooleanVar(value=False)
        enable_cb = ttk.Checkbutton(
            section_frame,
            text="Enable this printer",
            variable=enabled_var
        )
        enable_cb.pack(anchor=tk.W, padx=15, pady=(0, 10))

        # Get available printers for this type
        printers = self.network_manager.get_all_printers_by_type(printer_type)

        if not printers:
            tk.Label(
                section_frame,
                text="⚠️ No printers configured for this type",
                font=("Segoe UI", 9, "italic"),
                bg='#ffffff',
                fg='#e67e22'
            ).pack(anchor=tk.W, padx=15, pady=(0, 15))

            # Store empty config
            setattr(self, f"{printer_type}_enabled", enabled_var)
            setattr(self, f"{printer_type}_printer", tk.StringVar(value=""))
            setattr(self, f"{printer_type}_copies", tk.IntVar(value=1))
            return

        # Check for available printers
        available_printers = [p for p in printers if p.is_available]

        if not available_printers:
            tk.Label(
                section_frame,
                text="⚠️ No printers currently available (offline or not found)",
                font=("Segoe UI", 9, "italic"),
                bg='#ffffff',
                fg='#e74c3c'
            ).pack(anchor=tk.W, padx=15, pady=(0, 15))

            # Store empty config
            setattr(self, f"{printer_type}_enabled", enabled_var)
            setattr(self, f"{printer_type}_printer", tk.StringVar(value=""))
            setattr(self, f"{printer_type}_copies", tk.IntVar(value=1))
            return

        # Printer selection
        tk.Label(
            section_frame,
            text="Printer:",
            font=("Segoe UI", 10),
            bg='#ffffff',
            fg='#2c3e50'
        ).pack(anchor=tk.W, padx=15, pady=(0, 5))

        printer_var = tk.StringVar()
        printer_combo = ttk.Combobox(
            section_frame,
            textvariable=printer_var,
            values=[p.display_name for p in available_printers],
            state='readonly',
            width=50
        )
        printer_combo.pack(fill=tk.X, padx=15, pady=(0, 10))

        # Set default printer
        default_printer = self.network_manager.get_default_printer(printer_type)
        if default_printer and default_printer.is_available:
            printer_combo.set(default_printer.display_name)
            enabled_var.set(True)  # Enable by default if printer available
        elif available_printers:
            printer_combo.set(available_printers[0].display_name)

        # Copies (only for non-label printers)
        if printer_type != "folder_label":
            tk.Label(
                section_frame,
                text="Copies:",
                font=("Segoe UI", 10),
                bg='#ffffff',
                fg='#2c3e50'
            ).pack(anchor=tk.W, padx=15, pady=(0, 5))

            copies_var = tk.IntVar(value=1)
            copies_spin = ttk.Spinbox(
                section_frame,
                from_=1,
                to=10,
                textvariable=copies_var,
                width=10
            )
            copies_spin.pack(anchor=tk.W, padx=15, pady=(0, 15))

            setattr(self, f"{printer_type}_copies", copies_var)
        else:
            setattr(self, f"{printer_type}_copies", tk.IntVar(value=1))

        # Store variables for later retrieval
        setattr(self, f"{printer_type}_enabled", enabled_var)
        setattr(self, f"{printer_type}_printer", printer_var)
        setattr(self, f"{printer_type}_printers_list", available_printers)

    def confirm(self):
        """Confirm and return configuration"""
        # Build configuration
        config = {
            'printers': []
        }

        # Add 11x17 if enabled
        if self.printer_11x17_enabled.get() and hasattr(self, 'printer_11x17_printers_list'):
            selected_name = self.printer_11x17_printer.get()
            for printer in self.printer_11x17_printers_list:
                if printer.display_name == selected_name:
                    config['printers'].append({
                        'type': '11x17',
                        'printer_name': printer.printer_name,
                        'display_name': printer.display_name,
                        'copies': self.printer_11x17_copies.get()
                    })
                    break

        # Add 24x36 if enabled
        if self.printer_24x36_enabled.get() and hasattr(self, 'printer_24x36_printers_list'):
            selected_name = self.printer_24x36_printer.get()
            for printer in self.printer_24x36_printers_list:
                if printer.display_name == selected_name:
                    config['printers'].append({
                        'type': '24x36',
                        'printer_name': printer.printer_name,
                        'display_name': printer.display_name,
                        'copies': self.printer_24x36_copies.get()
                    })
                    break

        # Add folder label if enabled
        if self.folder_label_enabled.get() and hasattr(self, 'folder_label_printers_list'):
            selected_name = self.folder_label_printer.get()
            for printer in self.folder_label_printers_list:
                if printer.display_name == selected_name:
                    config['printers'].append({
                        'type': 'folder_label',
                        'printer_name': printer.printer_name,
                        'display_name': printer.display_name,
                        'copies': 1
                    })
                    break

        # Validate at least one printer selected
        if not config['printers']:
            messagebox.showwarning(
                "No Printers Selected",
                "Please enable at least one printer.",
                parent=self
            )
            return

        self.result = config
        self.destroy()

    def cancel(self):
        """Cancel the dialog"""
        self.result = None
        self.destroy()


class BatchPrintProgressDialog(tk.Toplevel):
    """Progress dialog for batch printing"""

    def __init__(self, parent, total_jobs: int):
        super().__init__(parent)
        self.parent_window = parent
        self.total_jobs = total_jobs
        self.current_job = 0
        self.successful = 0
        self.failed = 0
        self.cancelled = False

        self.setup_window()

    def setup_window(self):
        """Create progress window"""
        self.title("Batch Printing")
        self.geometry("550x300")
        self.configure(bg='#ecf0f1')
        self.transient(self.parent_window)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        # Header
        header_frame = tk.Frame(self, bg='#34495e', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text="🖨️ Batch Printing in Progress",
            font=("Segoe UI", 16, "bold"),
            bg='#34495e',
            fg='white'
        ).pack(expand=True)

        # Content
        content_frame = tk.Frame(self, bg='#ecf0f1')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Status label
        self.status_label = tk.Label(
            content_frame,
            text="Preparing to print...",
            font=("Segoe UI", 12),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        self.status_label.pack(pady=(0, 15))

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            content_frame,
            variable=self.progress_var,
            maximum=100,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(pady=(0, 20))

        # Stats
        self.stats_label = tk.Label(
            content_frame,
            text=f"Progress: 0/{self.total_jobs}  |  ✓ Success: 0  |  ✗ Failed: 0",
            font=("Segoe UI", 11),
            bg='#ecf0f1',
            fg='#7f8c8d'
        )
        self.stats_label.pack(pady=(0, 20))

        # Cancel button
        self.cancel_btn = tk.Button(
            content_frame,
            text="Cancel Remaining",
            command=self.on_cancel,
            font=("Segoe UI", 10),
            bg='#e74c3c',
            fg='white',
            border=0,
            padx=20,
            pady=8
        )
        self.cancel_btn.pack()

    def update_progress(self, order_number: str, success: bool):
        """Update progress"""
        self.current_job += 1
        if success:
            self.successful += 1
        else:
            self.failed += 1

        # Update UI
        status_icon = "✓" if success else "✗"
        self.status_label.config(text=f"{status_icon} Order {order_number}")

        progress = (self.current_job / self.total_jobs) * 100
        self.progress_var.set(progress)

        self.stats_label.config(
            text=f"Progress: {self.current_job}/{self.total_jobs}  |  ✓ Success: {self.successful}  |  ✗ Failed: {self.failed}"
        )

        self.update()

    def finish(self):
        """Finish and show results"""
        self.status_label.config(text="Batch printing complete!")
        self.cancel_btn.config(text="Close", command=self.destroy)

    def on_cancel(self):
        """Handle cancel request"""
        if self.current_job < self.total_jobs:
            result = messagebox.askyesno(
                "Cancel Batch Print",
                "Are you sure you want to cancel the remaining print jobs?",
                parent=self
            )
            if result:
                self.cancelled = True
                self.status_label.config(text="Cancelling...")
        else:
            self.destroy()


def print_with_timeout(pdf_path: str, printer_name: str, timeout: int = 60) -> tuple:
    """
    Print PDF with timeout protection for slow print servers
    Uses the improved printing methods from batch_print_with_presets.py
    """
    # Import the existing print function to avoid code duplication
    from batch_print_with_presets import print_with_timeout as legacy_print
    return legacy_print(pdf_path, printer_name, timeout)


def execute_network_batch_print(
    orders: List[Dict],
    network_manager: NetworkPrinterManager,
    print_config: Dict,
    parent_window,
    mark_processed_callback: Callable = None
) -> bool:
    """
    Execute batch printing using network printer configuration

    Args:
        orders: List of order dictionaries
        network_manager: NetworkPrinterManager instance
        print_config: Print configuration from dialog
        parent_window: Parent window for dialogs
        mark_processed_callback: Optional callback to mark orders as processed

    Returns:
        True if any jobs succeeded, False otherwise
    """
    log_info("Starting network batch print", {
        'order_count': len(orders),
        'printers': [p['display_name'] for p in print_config['printers']]
    })

    try:
        from word_template_processor import print_folder_label
    except ImportError as e:
        error_msg = f"Could not import word_template_processor: {e}"
        log_error("import_word_processor", e)
        messagebox.showerror("Import Error", error_msg)
        return False

    try:
        import win32print
        import win32api
    except ImportError as e:
        error_msg = f"Missing required Windows modules: {e}\n\nPlease install: pip install pywin32"
        log_error("import_win32_modules", e)
        messagebox.showerror("Import Error", error_msg)
        return False

    try:
        # Create progress dialog
        progress_dialog = BatchPrintProgressDialog(parent_window, len(orders))
        progress_dialog.update()

        successful_orders = []
        failed_orders = []
        orders_with_pdf_printed = []

        # Get template path from network config
        template_path = network_manager.config.template_path if network_manager.config else ""

        for order in orders:
            if progress_dialog.cancelled:
                break

            order_number = order.get('csv_data', {}).get('OrderNumber', 'Unknown')
            csv_data = order.get('csv_data', {})
            pdf_path = order.get('pdf_path')

            log_info(f"Processing order {order_number}", {
                'has_pdf': bool(pdf_path),
                'pdf_path': pdf_path,
                'processed': order.get('processed', False)
            })

            job_success = True
            pdf_was_printed = False

            # Process each printer for this order
            for printer_config in print_config['printers']:
                try:
                    printer_type = printer_config['type']
                    printer_name = printer_config['printer_name']
                    display_name = printer_config['display_name']

                    log_info(f"Attempting printer: {display_name}", {
                        'order_number': order_number,
                        'printer_type': printer_type,
                        'printer_name': printer_name
                    })

                    if printer_type in ['11x17', '24x36']:
                        # Print PDF
                        copies = printer_config['copies']

                        if pdf_path and os.path.exists(pdf_path):
                            for copy_num in range(copies):
                                if progress_dialog.cancelled:
                                    break

                                success, error = print_with_timeout(
                                    pdf_path,
                                    printer_name,
                                    timeout=60
                                )

                                if not success:
                                    log_error("print_pdf_network", Exception(error), {
                                        'order_number': order_number,
                                        'copy_number': copy_num + 1,
                                        'printer_name': printer_name,
                                        'display_name': display_name
                                    })
                                    job_success = False
                                    messagebox.showwarning(
                                        "Print Failed",
                                        f"Failed to print order {order_number} to {display_name}:\n{error}",
                                        parent=progress_dialog
                                    )
                                    break
                                else:
                                    log_info(f"Printed copy {copy_num + 1}/{copies} to {display_name}")
                                    pdf_was_printed = True

                                if copy_num < copies - 1:
                                    time.sleep(1)
                        else:
                            log_warning(f"PDF not found for order {order_number}", {'pdf_path': pdf_path})

                    elif printer_type == 'folder_label':
                        # Print folder label
                        if not order.get('processed', False):  # Skip processed orders
                            if template_path and os.path.exists(template_path):
                                success = print_folder_label(csv_data, template_path, printer_name)

                                if success:
                                    log_info(f"Printed folder label to {display_name}")
                                else:
                                    log_error("folder_label_print_network", Exception("print_folder_label returned False"), {
                                        'order_number': order_number,
                                        'printer_name': printer_name
                                    })
                                    job_success = False
                            else:
                                log_warning("Template not found", {'template_path': template_path})
                        else:
                            log_info(f"Skipping folder label for processed order {order_number}")

                except Exception as e:
                    log_error("process_network_printer", e, {
                        'order_number': order_number,
                        'printer_type': printer_type,
                        'printer_name': printer_config.get('printer_name')
                    })
                    job_success = False

            # Update progress
            progress_dialog.update_progress(order_number, job_success)

            if job_success:
                successful_orders.append(order)
                if pdf_was_printed:
                    orders_with_pdf_printed.append(order)
            else:
                failed_orders.append(order)

        # Mark processed
        if mark_processed_callback and orders_with_pdf_printed:
            mark_processed_callback(orders_with_pdf_printed)
            log_info(f"Marked {len(orders_with_pdf_printed)} orders as processed")

        # Finish progress dialog
        progress_dialog.finish()

        # Show results
        if not progress_dialog.cancelled:
            status_message = f"Batch printing completed!\n\n" \
                           f"✓ Successful: {len(successful_orders)} orders\n" \
                           f"✗ Failed: {len(failed_orders)} orders\n\n"

            if orders_with_pdf_printed:
                status_message += f"{len(orders_with_pdf_printed)} orders have been marked as processed."
            else:
                status_message += "No PDFs were printed."

            messagebox.showinfo(
                "Batch Print Complete",
                status_message,
                parent=progress_dialog
            )

        progress_dialog.destroy()

        log_success("network_batch_print_complete", {
            'successful': len(successful_orders),
            'failed': len(failed_orders)
        })

        return len(successful_orders) > 0

    except Exception as e:
        log_error("network_batch_print_execution", e, {
            'order_count': len(orders)
        })
        error_msg = f"Batch printing failed:\n{str(e)}\n\nCheck logs for details."
        messagebox.showerror("Batch Print Error", error_msg)
        return False


def show_print_config_dialog(
    parent,
    network_manager: NetworkPrinterManager,
    user_prefs: UserPreferencesManager,
    order_count: int
) -> Optional[Dict]:
    """
    Show print configuration dialog

    Returns:
        Print configuration dict or None if cancelled
    """
    dialog = PrintJobConfigDialog(parent, network_manager, user_prefs, order_count)
    dialog.wait_window()
    return dialog.result
