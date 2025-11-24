#!/usr/bin/env python3
"""
Printer Setup Wizard - Admin tool for initial network printer configuration
Guides IT/admins through printer setup for network deployment
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Optional
from pathlib import Path
from network_printer_manager import NetworkPrinterManager, PrinterDefinition, NetworkPrinterConfig
from error_logger import log_info, log_error, log_success
from datetime import datetime


class PrinterSetupWizard:
    """Setup wizard for configuring network printers"""

    def __init__(self, parent=None, network_manager: NetworkPrinterManager = None):
        """
        Initialize the setup wizard

        Args:
            parent: Parent window (optional)
            network_manager: NetworkPrinterManager instance (optional, creates new if None)
        """
        self.parent = parent
        self.network_manager = network_manager or NetworkPrinterManager()
        self.window = None
        self.current_step = 0

        # Configuration being built
        self.selected_11x17 = []
        self.selected_24x36 = []
        self.selected_folder_label = []
        self.template_path = ""

        # Wizard steps
        self.steps = [
            ("Welcome", self.create_welcome_step),
            ("Discover Printers", self.create_discovery_step),
            ("Configure 11x17 Printers", self.create_11x17_step),
            ("Configure 24x36 Printers", self.create_24x36_step),
            ("Configure Label Printers", self.create_label_step),
            ("Template Path", self.create_template_step),
            ("Review & Save", self.create_review_step)
        ]

    def show(self):
        """Show the setup wizard"""
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("Network Printer Setup Wizard")
        self.window.geometry("800x600")
        self.window.configure(bg='#ecf0f1')

        if self.parent:
            self.window.transient(self.parent)
            self.window.grab_set()

        # Create main layout
        self.create_header()
        self.create_content_area()
        self.create_navigation()

        # Show first step
        self.show_step(0)

        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"800x600+{x}+{y}")

        self.window.wait_window()

    def create_header(self):
        """Create wizard header"""
        self.header_frame = tk.Frame(self.window, bg='#2c3e50', height=80)
        self.header_frame.pack(fill=tk.X)
        self.header_frame.pack_propagate(False)

        self.title_label = tk.Label(
            self.header_frame,
            text="Network Printer Setup",
            font=("Segoe UI", 20, "bold"),
            bg='#2c3e50',
            fg='white'
        )
        self.title_label.pack(pady=20)

        self.step_label = tk.Label(
            self.header_frame,
            text="Step 1 of 7",
            font=("Segoe UI", 10),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        self.step_label.pack()

    def create_content_area(self):
        """Create main content area"""
        self.content_frame = tk.Frame(self.window, bg='#ecf0f1')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

    def create_navigation(self):
        """Create navigation buttons"""
        self.nav_frame = tk.Frame(self.window, bg='#ecf0f1', height=60)
        self.nav_frame.pack(fill=tk.X, padx=30, pady=(0, 20))
        self.nav_frame.pack_propagate(False)

        self.back_btn = tk.Button(
            self.nav_frame,
            text="← Back",
            command=self.go_back,
            font=("Segoe UI", 11),
            bg='#95a5a6',
            fg='white',
            border=0,
            padx=25,
            pady=10,
            state=tk.DISABLED
        )
        self.back_btn.pack(side=tk.LEFT)

        self.cancel_btn = tk.Button(
            self.nav_frame,
            text="Cancel",
            command=self.cancel,
            font=("Segoe UI", 11),
            bg='#e74c3c',
            fg='white',
            border=0,
            padx=25,
            pady=10
        )
        self.cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))

        self.next_btn = tk.Button(
            self.nav_frame,
            text="Next →",
            command=self.go_next,
            font=("Segoe UI", 11, "bold"),
            bg='#27ae60',
            fg='white',
            border=0,
            padx=25,
            pady=10
        )
        self.next_btn.pack(side=tk.RIGHT)

    def show_step(self, step_index: int):
        """Show a specific wizard step"""
        if step_index < 0 or step_index >= len(self.steps):
            return

        self.current_step = step_index

        # Update header
        step_name, step_func = self.steps[step_index]
        self.title_label.config(text=step_name)
        self.step_label.config(text=f"Step {step_index + 1} of {len(self.steps)}")

        # Clear content area
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Show step content
        step_func()

        # Update navigation buttons
        self.back_btn.config(state=tk.NORMAL if step_index > 0 else tk.DISABLED)

        if step_index == len(self.steps) - 1:
            self.next_btn.config(text="Finish & Save", bg='#2980b9')
        else:
            self.next_btn.config(text="Next →", bg='#27ae60')

    def go_back(self):
        """Go to previous step"""
        if self.current_step > 0:
            self.show_step(self.current_step - 1)

    def go_next(self):
        """Go to next step"""
        # Validate current step
        if not self.validate_step(self.current_step):
            return

        if self.current_step < len(self.steps) - 1:
            self.show_step(self.current_step + 1)
        else:
            # Final step - save configuration
            self.finish()

    def validate_step(self, step_index: int) -> bool:
        """Validate current step before proceeding"""
        # Step-specific validation
        if step_index == 5:  # Template path step
            if not self.template_path:
                messagebox.showwarning(
                    "Template Required",
                    "Please select a folder label template file.",
                    parent=self.window
                )
                return False

            if not Path(self.template_path).exists():
                messagebox.showwarning(
                    "Template Not Found",
                    "The selected template file does not exist.",
                    parent=self.window
                )
                return False

        return True

    def cancel(self):
        """Cancel the wizard"""
        result = messagebox.askyesno(
            "Cancel Setup",
            "Are you sure you want to cancel the setup wizard?",
            parent=self.window
        )
        if result:
            self.window.destroy()

    def finish(self):
        """Complete wizard and save configuration"""
        try:
            # Create printer definitions
            printers_11x17 = []
            for i, printer_name in enumerate(self.selected_11x17):
                printers_11x17.append(PrinterDefinition(
                    display_name=f"11x17 Printer {i+1}",
                    printer_name=printer_name,
                    printer_type="11x17",
                    is_default=(i == 0),
                    is_available=True,
                    description="Configured via setup wizard",
                    last_verified=datetime.now().isoformat()
                ))

            printers_24x36 = []
            for i, printer_name in enumerate(self.selected_24x36):
                printers_24x36.append(PrinterDefinition(
                    display_name=f"24x36 Plotter {i+1}",
                    printer_name=printer_name,
                    printer_type="24x36",
                    is_default=(i == 0),
                    is_available=True,
                    description="Configured via setup wizard",
                    last_verified=datetime.now().isoformat()
                ))

            printers_folder_label = []
            for i, printer_name in enumerate(self.selected_folder_label):
                printers_folder_label.append(PrinterDefinition(
                    display_name=f"Label Printer {i+1}",
                    printer_name=printer_name,
                    printer_type="folder_label",
                    is_default=(i == 0),
                    is_available=True,
                    description="Configured via setup wizard",
                    last_verified=datetime.now().isoformat()
                ))

            # Create configuration
            self.network_manager.config = NetworkPrinterConfig(
                printers_11x17=printers_11x17,
                printers_24x36=printers_24x36,
                printers_folder_label=printers_folder_label,
                template_path=self.template_path,
                auto_discover_on_startup=True,
                version="1.0",
                last_updated=datetime.now().isoformat()
            )

            # Save configuration
            if self.network_manager.save_config():
                log_success("setup_wizard_complete", {
                    'printers_11x17': len(printers_11x17),
                    'printers_24x36': len(printers_24x36),
                    'printers_folder_label': len(printers_folder_label),
                    'template_path': self.template_path
                })

                messagebox.showinfo(
                    "Setup Complete",
                    f"Network printer configuration saved successfully!\n\n"
                    f"11x17 Printers: {len(printers_11x17)}\n"
                    f"24x36 Printers: {len(printers_24x36)}\n"
                    f"Label Printers: {len(printers_folder_label)}\n\n"
                    f"The application is now ready for use.",
                    parent=self.window
                )

                self.window.destroy()
            else:
                messagebox.showerror(
                    "Save Failed",
                    "Failed to save configuration. Check logs for details.",
                    parent=self.window
                )

        except Exception as e:
            log_error("setup_wizard_finish", e)
            messagebox.showerror(
                "Setup Error",
                f"An error occurred while saving configuration:\n{str(e)}",
                parent=self.window
            )

    # ===== STEP CREATION METHODS =====

    def create_welcome_step(self):
        """Welcome step"""
        tk.Label(
            self.content_frame,
            text="Welcome to Network Printer Setup",
            font=("Segoe UI", 16, "bold"),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(pady=(20, 10))

        tk.Label(
            self.content_frame,
            text="This wizard will help you configure printers for network deployment.",
            font=("Segoe UI", 11),
            bg='#ecf0f1',
            fg='#34495e'
        ).pack(pady=(0, 30))

        info_frame = tk.Frame(self.content_frame, bg='#ffffff', relief='solid', borderwidth=1)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            info_frame,
            text="What this wizard will do:",
            font=("Segoe UI", 12, "bold"),
            bg='#ffffff',
            fg='#2c3e50'
        ).pack(anchor=tk.W, padx=20, pady=(20, 10))

        steps_text = [
            "1. Discover all available printers on your network",
            "2. Configure 11×17 (standard) printers",
            "3. Configure 24×36 (large format) printers",
            "4. Configure folder label printers",
            "5. Set template file location",
            "6. Save centralized configuration for all users"
        ]

        for step in steps_text:
            tk.Label(
                info_frame,
                text=step,
                font=("Segoe UI", 10),
                bg='#ffffff',
                fg='#34495e',
                justify=tk.LEFT
            ).pack(anchor=tk.W, padx=40, pady=5)

        tk.Label(
            info_frame,
            text="⚠️ Administrator/IT privileges may be required",
            font=("Segoe UI", 9, "italic"),
            bg='#ffffff',
            fg='#e67e22'
        ).pack(anchor=tk.W, padx=20, pady=(20, 20))

    def create_discovery_step(self):
        """Printer discovery step"""
        tk.Label(
            self.content_frame,
            text="Discovering Network Printers...",
            font=("Segoe UI", 14, "bold"),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(pady=(10, 20))

        # Refresh printer list
        self.network_manager.discover_printers()
        categories = self.network_manager.categorize_printers()

        # Display results
        results_frame = tk.Frame(self.content_frame, bg='#ffffff', relief='solid', borderwidth=1)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        canvas = tk.Canvas(results_frame, bg='#ffffff', highlightthickness=0)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#ffffff')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Summary
        tk.Label(
            scrollable_frame,
            text=f"✓ Found {len(self.network_manager.available_printers)} printer(s)",
            font=("Segoe UI", 12, "bold"),
            bg='#ffffff',
            fg='#27ae60'
        ).pack(anchor=tk.W, padx=20, pady=(20, 10))

        # Categories
        for category, printers in categories.items():
            if printers:
                category_names = {
                    'large_format': '24×36 Large Format Printers',
                    'standard': '11×17 Standard Printers',
                    'label': 'Label Printers',
                    'other': 'Other Printers'
                }

                tk.Label(
                    scrollable_frame,
                    text=f"{category_names[category]} ({len(printers)}):",
                    font=("Segoe UI", 11, "bold"),
                    bg='#ffffff',
                    fg='#2c3e50'
                ).pack(anchor=tk.W, padx=20, pady=(15, 5))

                for printer in printers:
                    tk.Label(
                        scrollable_frame,
                        text=f"  • {printer}",
                        font=("Segoe UI", 9),
                        bg='#ffffff',
                        fg='#34495e'
                    ).pack(anchor=tk.W, padx=40, pady=2)

    def create_11x17_step(self):
        """Configure 11x17 printers step"""
        tk.Label(
            self.content_frame,
            text="Select 11×17 (Standard) Printers",
            font=("Segoe UI", 14, "bold"),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(pady=(10, 5))

        tk.Label(
            self.content_frame,
            text="These printers will be used for standard-size plots (11×17 / Tabloid)",
            font=("Segoe UI", 10),
            bg='#ecf0f1',
            fg='#7f8c8d'
        ).pack(pady=(0, 20))

        # Get available printers
        categories = self.network_manager.categorize_printers()
        available = categories['standard'] + categories['other']

        if not available:
            tk.Label(
                self.content_frame,
                text="⚠️ No printers detected. You can configure this later.",
                font=("Segoe UI", 11),
                bg='#ecf0f1',
                fg='#e67e22'
            ).pack(pady=50)
            return

        # Printer selection listbox
        list_frame = tk.Frame(self.content_frame, bg='#ffffff', relief='solid', borderwidth=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(
            list_frame,
            text="Select one or more printers (first selected will be default):",
            font=("Segoe UI", 10),
            bg='#ffffff',
            fg='#2c3e50'
        ).pack(anchor=tk.W, padx=15, pady=(15, 10))

        listbox_frame = tk.Frame(list_frame, bg='#ffffff')
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        listbox = tk.Listbox(
            listbox_frame,
            selectmode=tk.MULTIPLE,
            yscrollcommand=scrollbar.set,
            font=("Segoe UI", 10),
            height=10
        )
        scrollbar.config(command=listbox.yview)

        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Populate listbox
        for printer in available:
            listbox.insert(tk.END, printer)

        # Pre-select if already configured
        for i, printer in enumerate(available):
            if printer in self.selected_11x17:
                listbox.selection_set(i)

        # Save selection when changed
        def save_selection(event=None):
            self.selected_11x17 = [listbox.get(i) for i in listbox.curselection()]

        listbox.bind('<<ListboxSelect>>', save_selection)

    def create_24x36_step(self):
        """Configure 24x36 printers step"""
        tk.Label(
            self.content_frame,
            text="Select 24×36 (Large Format) Printers",
            font=("Segoe UI", 14, "bold"),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(pady=(10, 5))

        tk.Label(
            self.content_frame,
            text="These printers will be used for large format plots (plotters, wide format)",
            font=("Segoe UI", 10),
            bg='#ecf0f1',
            fg='#7f8c8d'
        ).pack(pady=(0, 20))

        # Get available printers
        categories = self.network_manager.categorize_printers()
        available = categories['large_format'] + categories['other']

        if not available:
            tk.Label(
                self.content_frame,
                text="⚠️ No large format printers detected. You can configure this later.",
                font=("Segoe UI", 11),
                bg='#ecf0f1',
                fg='#e67e22'
            ).pack(pady=50)
            return

        # Printer selection listbox
        list_frame = tk.Frame(self.content_frame, bg='#ffffff', relief='solid', borderwidth=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(
            list_frame,
            text="Select one or more printers (first selected will be default):",
            font=("Segoe UI", 10),
            bg='#ffffff',
            fg='#2c3e50'
        ).pack(anchor=tk.W, padx=15, pady=(15, 10))

        listbox_frame = tk.Frame(list_frame, bg='#ffffff')
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        listbox = tk.Listbox(
            listbox_frame,
            selectmode=tk.MULTIPLE,
            yscrollcommand=scrollbar.set,
            font=("Segoe UI", 10),
            height=10
        )
        scrollbar.config(command=listbox.yview)

        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Populate listbox
        for printer in available:
            listbox.insert(tk.END, printer)

        # Pre-select if already configured
        for i, printer in enumerate(available):
            if printer in self.selected_24x36:
                listbox.selection_set(i)

        # Save selection when changed
        def save_selection(event=None):
            self.selected_24x36 = [listbox.get(i) for i in listbox.curselection()]

        listbox.bind('<<ListboxSelect>>', save_selection)

    def create_label_step(self):
        """Configure label printers step"""
        tk.Label(
            self.content_frame,
            text="Select Folder Label Printer",
            font=("Segoe UI", 14, "bold"),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(pady=(10, 5))

        tk.Label(
            self.content_frame,
            text="This printer will be used for printing folder labels",
            font=("Segoe UI", 10),
            bg='#ecf0f1',
            fg='#7f8c8d'
        ).pack(pady=(0, 20))

        # Get available printers
        categories = self.network_manager.categorize_printers()
        available = categories['label'] + categories['standard'] + categories['other']

        if not available:
            tk.Label(
                self.content_frame,
                text="⚠️ No printers detected. You can configure this later.",
                font=("Segoe UI", 11),
                bg='#ecf0f1',
                fg='#e67e22'
            ).pack(pady=50)
            return

        # Printer selection listbox
        list_frame = tk.Frame(self.content_frame, bg='#ffffff', relief='solid', borderwidth=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(
            list_frame,
            text="Select one or more printers (first selected will be default):",
            font=("Segoe UI", 10),
            bg='#ffffff',
            fg='#2c3e50'
        ).pack(anchor=tk.W, padx=15, pady=(15, 10))

        listbox_frame = tk.Frame(list_frame, bg='#ffffff')
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        listbox = tk.Listbox(
            listbox_frame,
            selectmode=tk.MULTIPLE,
            yscrollcommand=scrollbar.set,
            font=("Segoe UI", 10),
            height=10
        )
        scrollbar.config(command=listbox.yview)

        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Populate listbox
        for printer in available:
            listbox.insert(tk.END, printer)

        # Pre-select if already configured
        for i, printer in enumerate(available):
            if printer in self.selected_folder_label:
                listbox.selection_set(i)

        # Save selection when changed
        def save_selection(event=None):
            self.selected_folder_label = [listbox.get(i) for i in listbox.curselection()]

        listbox.bind('<<ListboxSelect>>', save_selection)

    def create_template_step(self):
        """Template path configuration step"""
        tk.Label(
            self.content_frame,
            text="Folder Label Template",
            font=("Segoe UI", 14, "bold"),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(pady=(10, 5))

        tk.Label(
            self.content_frame,
            text="Select the Word template file used for folder labels",
            font=("Segoe UI", 10),
            bg='#ecf0f1',
            fg='#7f8c8d'
        ).pack(pady=(0, 20))

        # Template selection frame
        template_frame = tk.Frame(self.content_frame, bg='#ffffff', relief='solid', borderwidth=1)
        template_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            template_frame,
            text="Template File:",
            font=("Segoe UI", 11, "bold"),
            bg='#ffffff',
            fg='#2c3e50'
        ).pack(anchor=tk.W, padx=15, pady=(15, 10))

        path_frame = tk.Frame(template_frame, bg='#ffffff')
        path_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        self.template_entry = tk.Entry(
            path_frame,
            font=("Segoe UI", 10),
            bg='#ecf0f1'
        )
        self.template_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.template_entry.insert(0, self.template_path)

        tk.Button(
            path_frame,
            text="Browse...",
            command=self.browse_template,
            font=("Segoe UI", 10),
            bg='#3498db',
            fg='white',
            border=0,
            padx=15,
            pady=5
        ).pack(side=tk.RIGHT)

        # Info text
        info_frame = tk.Frame(self.content_frame, bg='#fff8e1', relief='solid', borderwidth=1)
        info_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(
            info_frame,
            text="ℹ️  Template Requirements:",
            font=("Segoe UI", 10, "bold"),
            bg='#fff8e1',
            fg='#f39c12'
        ).pack(anchor=tk.W, padx=15, pady=(10, 5))

        requirements = [
            "• Microsoft Word .docx file",
            "• Contains bookmarks: OrderNumber, Customer, LotSub, Level",
            "• Stored in accessible network location or shared drive",
            "• All users must have read access to this file"
        ]

        for req in requirements:
            tk.Label(
                info_frame,
                text=req,
                font=("Segoe UI", 9),
                bg='#fff8e1',
                fg='#e67e22',
                justify=tk.LEFT
            ).pack(anchor=tk.W, padx=30, pady=2)

        tk.Label(
            info_frame,
            text=" ",
            bg='#fff8e1'
        ).pack(pady=5)

    def browse_template(self):
        """Browse for template file"""
        filename = filedialog.askopenfilename(
            title="Select Folder Label Template",
            filetypes=[
                ("Word Documents", "*.docx"),
                ("All Files", "*.*")
            ],
            parent=self.window
        )

        if filename:
            self.template_path = filename
            self.template_entry.delete(0, tk.END)
            self.template_entry.insert(0, filename)

    def create_review_step(self):
        """Review and confirmation step"""
        tk.Label(
            self.content_frame,
            text="Review Configuration",
            font=("Segoe UI", 14, "bold"),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(pady=(10, 20))

        # Review frame with scrollbar
        review_frame = tk.Frame(self.content_frame, bg='#ffffff', relief='solid', borderwidth=1)
        review_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        canvas = tk.Canvas(review_frame, bg='#ffffff', highlightthickness=0)
        scrollbar = ttk.Scrollbar(review_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#ffffff')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Display configuration summary
        sections = [
            ("11×17 Printers", self.selected_11x17),
            ("24×36 Printers", self.selected_24x36),
            ("Label Printers", self.selected_folder_label)
        ]

        for title, printers in sections:
            tk.Label(
                scrollable_frame,
                text=f"{title}: ({len(printers)})",
                font=("Segoe UI", 11, "bold"),
                bg='#ffffff',
                fg='#2c3e50'
            ).pack(anchor=tk.W, padx=20, pady=(15, 5))

            if printers:
                for i, printer in enumerate(printers):
                    default_text = " [DEFAULT]" if i == 0 else ""
                    tk.Label(
                        scrollable_frame,
                        text=f"  • {printer}{default_text}",
                        font=("Segoe UI", 9),
                        bg='#ffffff',
                        fg='#27ae60' if i == 0 else '#34495e'
                    ).pack(anchor=tk.W, padx=40, pady=2)
            else:
                tk.Label(
                    scrollable_frame,
                    text="  (None configured)",
                    font=("Segoe UI", 9, "italic"),
                    bg='#ffffff',
                    fg='#95a5a6'
                ).pack(anchor=tk.W, padx=40, pady=2)

        # Template path
        tk.Label(
            scrollable_frame,
            text="Template Path:",
            font=("Segoe UI", 11, "bold"),
            bg='#ffffff',
            fg='#2c3e50'
        ).pack(anchor=tk.W, padx=20, pady=(15, 5))

        tk.Label(
            scrollable_frame,
            text=f"  {self.template_path or '(Not configured)'}",
            font=("Segoe UI", 9),
            bg='#ffffff',
            fg='#34495e',
            wraplength=700
        ).pack(anchor=tk.W, padx=40, pady=2)

        # Warning if nothing configured
        if not any([self.selected_11x17, self.selected_24x36, self.selected_folder_label]):
            tk.Label(
                scrollable_frame,
                text="⚠️ Warning: No printers configured. You can add them later.",
                font=("Segoe UI", 10),
                bg='#ffffff',
                fg='#e67e22'
            ).pack(pady=20)


def run_setup_wizard(parent=None):
    """
    Run the printer setup wizard

    Args:
        parent: Parent window (optional)

    Returns:
        NetworkPrinterManager with updated configuration
    """
    network_manager = NetworkPrinterManager()

    wizard = PrinterSetupWizard(parent, network_manager)
    wizard.show()

    return network_manager


if __name__ == "__main__":
    # Standalone testing
    root = tk.Tk()
    root.withdraw()

    run_setup_wizard()

    root.destroy()
