#!/usr/bin/env python3
"""
Batch Print with Presets - New batch printing system using presets
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Callable
import logging
import os
import threading
import time
from print_preset_manager import PrintPresetManager, PrintPreset
from error_logger import log_error, log_info, log_warning, log_success


class PresetSelectionDialog(tk.Toplevel):
    """Dialog for selecting a preset before batch printing"""

    def __init__(self, parent, preset_manager: PrintPresetManager, order_count: int):
        super().__init__(parent)
        self.parent_window = parent
        self.preset_manager = preset_manager
        self.order_count = order_count
        self.selected_preset = None

        self.setup_window()

    def setup_window(self):
        """Create the preset selection window with dynamic sizing"""
        self.title("Quick Print")

        # Calculate dynamic window height based on number of presets
        num_presets = len(self.preset_manager.get_all_presets())
        # Base height + height per preset (approx 70px per preset)
        base_height = 300
        preset_height = 70 * num_presets
        window_height = min(base_height + preset_height, 700)  # Cap at 700px

        self.geometry(f"500x{window_height}")
        self.configure(bg='#ecf0f1')
        self.transient(self.parent_window)
        self.grab_set()

        # Header
        header_frame = tk.Frame(self, bg='#34495e', height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text=f"Quick Print - {self.order_count} orders selected",
            font=("Segoe UI", 16, "bold"),
            bg='#34495e',
            fg='white'
        ).pack(expand=True)

        # Content
        content_frame = tk.Frame(self, bg='#ecf0f1')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Instructions
        tk.Label(
            content_frame,
            text="Choose a preset:",
            font=("Segoe UI", 13, "bold"),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(anchor=tk.W, pady=(0, 15))

        # Preset radio buttons with scrollable frame if needed
        self.preset_var = tk.StringVar()
        default_preset = self.preset_manager.get_default_preset()

        # If many presets, use scrollable canvas
        if num_presets > 5:
            # Create canvas with scrollbar
            canvas = tk.Canvas(content_frame, bg='#ffffff', highlightthickness=0)
            scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
            preset_frame = tk.Frame(canvas, bg='#ffffff', relief='solid', borderwidth=1)

            preset_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=preset_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(0, 20))
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 20))
        else:
            preset_frame = tk.Frame(content_frame, bg='#ffffff', relief='solid', borderwidth=1)
            preset_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        for name, preset in self.preset_manager.get_all_presets().items():
            # Build description
            desc_parts = []
            if preset.printer_11x17_enabled and preset.printer_11x17_script:
                desc_parts.append(f"11×17 ({preset.printer_11x17_copies}×)")
            if preset.printer_24x36_enabled and preset.printer_24x36_script:
                desc_parts.append(f"24×36 ({preset.printer_24x36_copies}×)")
            if preset.folder_label_enabled and preset.folder_label_printer:
                desc_parts.append("Folder Label")

            description = " + ".join(desc_parts) if desc_parts else "No printers configured"

            # Radio button with description
            rb_frame = tk.Frame(preset_frame, bg='#ffffff')
            rb_frame.pack(fill=tk.X, padx=15, pady=10)

            radio_text = f"⭐ {name}" if preset.is_default else name
            tk.Radiobutton(
                rb_frame,
                text=radio_text,
                variable=self.preset_var,
                value=name,
                font=("Segoe UI", 12, "bold"),
                bg='#ffffff',
                fg='#2c3e50',
                selectcolor='#ffffff',
                activebackground='#ffffff'
            ).pack(anchor=tk.W)

            tk.Label(
                rb_frame,
                text=f"    {description}",
                font=("Segoe UI", 10),
                bg='#ffffff',
                fg='#7f8c8d'
            ).pack(anchor=tk.W, padx=(25, 0))

        # Set default selection
        if default_preset:
            for name, preset in self.preset_manager.get_all_presets().items():
                if preset.is_default:
                    self.preset_var.set(name)
                    break

        # Info label
        tk.Label(
            content_frame,
            text="ℹ️ Folder labels will automatically skip processed orders",
            font=("Segoe UI", 9, "italic"),
            bg='#ecf0f1',
            fg='#7f8c8d'
        ).pack(pady=(0, 10))

        # Buttons
        button_frame = tk.Frame(content_frame, bg='#ecf0f1')
        button_frame.pack(fill=tk.X)

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
            text="Review & Print",
            command=self.confirm,
            font=("Segoe UI", 11, "bold"),
            bg='#27ae60',
            fg='white',
            border=0,
            padx=25,
            pady=10
        ).pack(side=tk.RIGHT, padx=(0, 10))

    def confirm(self):
        """Confirm preset selection"""
        preset_name = self.preset_var.get()

        if not preset_name:
            messagebox.showwarning("No Selection", "Please select a preset.")
            return

        self.selected_preset = self.preset_manager.get_preset(preset_name)
        self.destroy()

    def cancel(self):
        """Cancel selection"""
        self.selected_preset = None
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

    Args:
        pdf_path: Path to PDF file
        printer_name: Printer/script name
        timeout: Timeout in seconds (default 60)

    Returns:
        (success: bool, error: str or None)
    """
    context = {
        'pdf_path': pdf_path,
        'printer_name': printer_name,
        'timeout': timeout
    }

    log_info(f"Starting print job", context)

    try:
        import win32print
        import win32api
    except ImportError as e:
        error_msg = f"Missing required module: {e}"
        log_error("import_win32_modules", e, context)
        return False, error_msg

    result = {'success': False, 'error': None, 'completed': False}

    def print_job():
        try:
            import subprocess
            import os
            import pywintypes

            # Set the printer as default
            log_info(f"Setting default printer to: {printer_name}")
            win32print.SetDefaultPrinter(printer_name)

            # Configure printer for "Scale to Fit" printing
            try:
                log_info(f"Configuring printer for scale-to-fit")

                # Get printer handle
                hprinter = win32print.OpenPrinter(printer_name)

                try:
                    # Get current printer properties
                    properties = win32print.GetPrinter(hprinter, 2)

                    # Get device mode (DEVMODE) - this controls print settings
                    pdevmode = properties['pDevMode']
                    if pdevmode is None:
                        pdevmode = win32print.GetPrinter(hprinter, 2)['pDevMode']

                    if pdevmode:
                        # Set scale to 100 (this is percentage - 100 means fit to page)
                        # Note: Different drivers handle this differently
                        # Some use dmScale, others use specific flags

                        # Try to set fit-to-page mode
                        # Many printer drivers support this via dmFields
                        # DM_SCALE = 0x00000010
                        pdevmode.Scale = 100  # 100% = fit to page for most drivers
                        pdevmode.Fields = pdevmode.Fields | 0x00000010  # Enable scale field

                        # Update printer with new settings
                        properties['pDevMode'] = pdevmode
                        win32print.SetPrinter(hprinter, 2, properties, 0)
                        log_info(f"Printer configured for scaling")

                finally:
                    win32print.ClosePrinter(hprinter)

            except Exception as e:
                # Non-fatal - continue with printing even if scaling config fails
                log_warning(f"Could not configure printer scaling (will try print-time scaling): {e}", context)

            log_info(f"Sending print command for: {pdf_path}")

            # Try multiple methods for PDF printing (in order of reliability)
            printed = False

            # Method 1: Try Adobe Reader command line (most reliable, but silent)
            # Note: Adobe /t command doesn't support direct scaling parameters,
            # but will use the printer's DEVMODE settings we configured above
            adobe_paths = [
                r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe",
                r"C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe",
                r"C:\Program Files\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe",
            ]

            for adobe_path in adobe_paths:
                if os.path.exists(adobe_path):
                    try:
                        log_info(f"Using Adobe Reader for printing (will use printer's scale settings)")
                        # /t = print to printer and exit
                        # Adobe should respect the DEVMODE scaling we configured above
                        subprocess.run(
                            [adobe_path, "/t", pdf_path, printer_name],
                            timeout=30,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        printed = True
                        log_info(f"Print job submitted via Adobe Reader")
                        break
                    except Exception as e:
                        log_info(f"Adobe Reader print failed: {e}")
                        continue

            # Method 2: Try SumatraPDF command line (lightweight and reliable)
            if not printed:
                sumatra_paths = [
                    r"C:\Program Files\SumatraPDF\SumatraPDF.exe",
                    r"C:\Program Files (x86)\SumatraPDF\SumatraPDF.exe",
                ]

                for sumatra_path in sumatra_paths:
                    if os.path.exists(sumatra_path):
                        try:
                            log_info(f"Using SumatraPDF for printing with fit-to-page scaling")
                            # SumatraPDF supports -print-settings for scaling
                            # "fit" scales the page to fit the paper
                            subprocess.run(
                                [sumatra_path, "-print-to", printer_name, "-print-settings", "fit", pdf_path],
                                timeout=30,
                                creationflags=subprocess.CREATE_NO_WINDOW
                            )
                            printed = True
                            log_info(f"Print job submitted via SumatraPDF with fit-to-page")
                            break
                        except Exception as e:
                            log_info(f"SumatraPDF print failed: {e}")
                            continue

            # Method 3: Try Ghostscript (most reliable for large format plotters)
            if not printed:
                gs_paths = [
                    r"C:\Program Files\gs\gs10.04.0\bin\gswin64c.exe",
                    r"C:\Program Files\gs\gs10.03.1\bin\gswin64c.exe",
                    r"C:\Program Files\gs\gs10.03.0\bin\gswin64c.exe",
                    r"C:\Program Files\gs\gs10.02.1\bin\gswin64c.exe",
                    r"C:\Program Files\gs\gs10.02.0\bin\gswin64c.exe",
                    r"C:\Program Files\gs\gs10.01.2\bin\gswin64c.exe",
                    r"C:\Program Files (x86)\gs\gs10.04.0\bin\gswin32c.exe",
                    r"C:\Program Files (x86)\gs\gs10.03.1\bin\gswin32c.exe",
                    r"C:\Program Files (x86)\gs\gs10.03.0\bin\gswin32c.exe",
                ]

                # Also check for gs in PATH
                import shutil
                gs_in_path = shutil.which("gswin64c") or shutil.which("gswin32c") or shutil.which("gs")
                if gs_in_path:
                    gs_paths.insert(0, gs_in_path)

                for gs_path in gs_paths:
                    if os.path.exists(gs_path):
                        try:
                            log_info(f"Using Ghostscript for printing (best for large format plotters)")
                            # Ghostscript command for printing with scaling
                            # -dFIXEDMEDIA fixes the output size to the printer's page size
                            # -dPDFFitPage scales the PDF to fit the page
                            # -dBATCH -dNOPAUSE -dQUIET for silent operation
                            subprocess.run(
                                [
                                    gs_path,
                                    "-dPrinted",
                                    "-dBATCH",
                                    "-dNOPAUSE",
                                    "-dNOSAFER",
                                    "-dQUIET",
                                    "-dPDFFitPage",
                                    "-dFIXEDMEDIA",
                                    "-sDEVICE=mswinpr2",
                                    f"-sOutputFile=%printer%{printer_name}",
                                    pdf_path
                                ],
                                timeout=60,
                                creationflags=subprocess.CREATE_NO_WINDOW
                            )
                            printed = True
                            log_info(f"Print job submitted via Ghostscript")
                            break
                        except Exception as e:
                            log_info(f"Ghostscript print failed: {e}")
                            continue

            # Method 4: Fall back to ShellExecute with "print" verb (opens viewer briefly)
            if not printed:
                log_info(f"Using ShellExecute print verb (may briefly show PDF viewer)")
                try:
                    win32api.ShellExecute(
                        0,
                        "print",  # Using "print" verb instead of "printto" - more reliable
                        pdf_path,
                        None,
                        ".",
                        0  # SW_HIDE
                    )
                    printed = True
                    log_info(f"Print job submitted via ShellExecute")
                except Exception as e:
                    log_error("shellexecute_print", e, context)
                    # Last resort: try opening the file and let default handler print
                    os.startfile(pdf_path, "print")
                    printed = True
                    log_info(f"Print job submitted via startfile")

            # Small delay to ensure print job is submitted
            time.sleep(1.5)

            # Verify that the job actually made it to the printer queue
            try:
                log_info(f"Verifying print job in queue")
                hprinter = win32print.OpenPrinter(printer_name)
                try:
                    jobs = []
                    # Get all jobs in the queue
                    job_info = win32print.EnumJobs(hprinter, 0, 99, 1)

                    # Check if there are any jobs with our PDF filename
                    pdf_filename = os.path.basename(pdf_path)
                    for job in job_info:
                        if pdf_filename.lower() in job.get('pDocument', '').lower():
                            jobs.append(job)

                    if jobs:
                        log_info(f"Confirmed: {len(jobs)} job(s) in printer queue for {pdf_filename}")
                    else:
                        log_warning(f"Warning: No jobs found in queue for {pdf_filename} - job may still be processing", context)
                finally:
                    win32print.ClosePrinter(hprinter)
            except Exception as e:
                log_warning(f"Could not verify print queue (non-fatal): {e}", context)

            result['success'] = True
            result['completed'] = True
            log_success("print_job", context)

        except Exception as e:
            result['error'] = str(e)
            result['completed'] = True
            log_error("print_job_execution", e, context)

    # Start print job in thread
    thread = threading.Thread(target=print_job)
    thread.daemon = True
    thread.start()

    # Wait with timeout
    thread.join(timeout=timeout)

    if not result['completed']:
        # Thread is still running - timeout occurred
        result['error'] = f"Timeout after {timeout}s - print server may be slow"
        log_warning(f"Print timeout", context)
        # Note: Job may still complete in background, but we've moved on
        return False, result['error']

    if not result['success'] and result['error']:
        return False, result['error']

    return result['success'], result.get('error')


def should_print_folder_label(order: Dict) -> bool:
    """
    Determine if folder label should be printed for this order

    Folder labels are printed for:
    - Orders in green category (has PDF)
    - Orders in red category (no PDF)

    Folder labels are NOT printed for:
    - Orders in gray category (processed)
    """
    # Skip processed orders
    if order.get('processed', False):
        return False

    return True


def execute_batch_print_with_preset(
    orders: List[Dict],
    preset: PrintPreset,
    template_path: str,
    parent_window,
    mark_processed_callback: Callable = None
) -> bool:
    """
    Execute batch printing using a preset

    Args:
        orders: List of order dictionaries
        preset: PrintPreset to use
        template_path: Path to folder label template
        parent_window: Parent window for dialogs
        mark_processed_callback: Optional callback to mark orders as processed

    Returns:
        True if any jobs succeeded, False otherwise
    """
    log_info(f"Starting batch print with preset", {'order_count': len(orders), 'preset': preset.name if hasattr(preset, 'name') else 'unknown'})

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
        orders_with_pdf_printed = []  # Track orders that actually printed PDFs

        # Get printer configurations from preset
        printers_config = preset.get_printers_config(template_path)

        log_info(f"Preset configuration loaded", {
            'num_printers': len(printers_config),
            'printers': [f"{p['type']}: {p.get('printer_name', 'unknown')}" for p in printers_config]
        })

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
            pdf_was_printed = False  # Track if PDF was actually printed

            # Process each printer for this order
            for printer_config in printers_config:
                log_info(f"Attempting printer: {printer_config['type']}", {
                    'order_number': order_number,
                    'printer_type': printer_config['type'],
                    'printer_name': printer_config.get('printer_name', 'unknown')
                })
                try:
                    printer_type = printer_config['type']

                    if printer_type in ['11x17', '24x36']:
                        # Print PDF to printer
                        printer_name = printer_config['printer_name']
                        copies = printer_config['copies']

                        log_info(f"PDF print requested for {printer_type}", {
                            'order_number': order_number,
                            'pdf_path': pdf_path,
                            'pdf_exists': os.path.exists(pdf_path) if pdf_path else False,
                            'copies': copies
                        })

                        if pdf_path and os.path.exists(pdf_path):
                            # Print multiple copies with timeout protection
                            for copy_num in range(copies):
                                if progress_dialog.cancelled:
                                    break

                                success, error = print_with_timeout(
                                    pdf_path,
                                    printer_name,
                                    timeout=60
                                )

                                if not success:
                                    log_error("print_pdf_copy", Exception(error), {
                                        'order_number': order_number,
                                        'copy_number': copy_num + 1,
                                        'total_copies': copies,
                                        'printer_type': printer_type,
                                        'printer_name': printer_name,
                                        'pdf_path': pdf_path
                                    })
                                    job_success = False
                                    break
                                else:
                                    log_info(f"Printed copy {copy_num + 1}/{copies} to {printer_type} printer for order {order_number}")
                                    pdf_was_printed = True  # Mark that PDF was actually printed

                                # Small delay between copies to avoid overwhelming server
                                if copy_num < copies - 1:
                                    time.sleep(1)
                        else:
                            log_warning(f"PDF not found for order {order_number}", {'pdf_path': pdf_path})
                            # Don't mark as failed if just missing PDF

                    elif printer_type == 'folder':
                        # Print folder label using Word template
                        # Check if should print folder label for this order
                        if should_print_folder_label(order):
                            printer_name = printer_config.get('printer_name')

                            # IMPORTANT: Always use the template_path parameter (calculated relative path)
                            # Ignore any old hardcoded path in the preset config
                            template = template_path

                            log_info(f"Using template path for folder label", {
                                'order_number': order_number,
                                'template_path': template
                            })

                            success = print_folder_label(csv_data, template, printer_name)

                            if success:
                                log_info(f"Printed folder label for order {order_number}")
                            else:
                                log_error("folder_label_print_failed", Exception("print_folder_label returned False"), {
                                    'order_number': order_number,
                                    'printer_name': printer_name,
                                    'template': template,
                                    'csv_data': csv_data
                                })
                                job_success = False
                        else:
                            log_info(f"Skipping folder label for processed order {order_number}")

                except Exception as e:
                    log_error("process_printer_for_order", e, {
                        'order_number': order_number,
                        'printer_type': printer_type,
                        'printer_name': printer_config.get('printer_name', 'unknown')
                    })
                    job_success = False

            # Update progress
            progress_dialog.update_progress(order_number, job_success)

            if job_success:
                successful_orders.append(order)
                # Only track for "mark as processed" if PDF was actually printed
                if pdf_was_printed:
                    orders_with_pdf_printed.append(order)
            else:
                failed_orders.append(order)

        # Mark only orders with printed PDFs as processed (folder labels don't affect status)
        if mark_processed_callback and orders_with_pdf_printed:
            mark_processed_callback(orders_with_pdf_printed)
            log_info(f"Marked {len(orders_with_pdf_printed)} orders with printed PDFs as processed")

        # Finish progress dialog
        progress_dialog.finish()

        # Show final results
        if not progress_dialog.cancelled:
            status_message = f"Batch printing completed!\n\n" \
                           f"✓ Successful: {len(successful_orders)} orders\n" \
                           f"✗ Failed: {len(failed_orders)} orders\n\n"

            if orders_with_pdf_printed:
                status_message += f"{len(orders_with_pdf_printed)} orders with PDFs printed have been marked as processed.\n" \
                                f"Folder labels do not affect order status."
            else:
                status_message += "No PDFs were printed (folder labels don't affect status)."

            messagebox.showinfo(
                "Batch Print Complete",
                status_message,
                parent=progress_dialog
            )

        progress_dialog.destroy()

        log_success("batch_print_complete", {
            'successful': len(successful_orders),
            'failed': len(failed_orders)
        })

        return len(successful_orders) > 0

    except Exception as e:
        log_error("batch_print_execution", e, {
            'order_count': len(orders),
            'template_path': template_path
        })
        error_msg = f"Batch printing failed:\n{str(e)}\n\nCheck print_errors.log for details."
        messagebox.showerror("Batch Print Error", error_msg)
        return False
