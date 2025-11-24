#!/usr/bin/env python3
"""
Document Manager - Redesigned Main Application
Enhanced UI with Settings, Card Display, and 2-Week View
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import sqlite3
from pathlib import Path
import logging
from datetime import datetime, timedelta
import re
import shutil
import json
from typing import Dict, List, Optional

from pdf_processor import PDFProcessor
from database_manager import DatabaseManager

class SettingsManager:
    def __init__(self):
        self.settings_file = "settings.json"
        self.default_settings = {
            "csv_path": "",
            "pdf_path": "",
            "archive_path": "archive"
        }
        self.settings = self.load_settings()

    def load_settings(self) -> Dict:
        try:
            if Path(self.settings_file).exists():
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logging.warning(f"Could not load settings: {e}")
        return self.default_settings.copy()

    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            logging.error(f"Could not save settings: {e}")

    def get(self, key: str) -> str:
        return self.settings.get(key, self.default_settings.get(key, ""))

    def set(self, key: str, value: str):
        self.settings[key] = value
        self.save_settings()

class OrderCard(ttk.Frame):
    def __init__(self, parent, order_data: Dict, has_pdf: bool = False, **kwargs):
        super().__init__(parent, **kwargs)

        self.order_data = order_data
        self.has_pdf = has_pdf
        self.pdf_path = None

        self.setup_card()

    def setup_card(self):
        # Configure the card styling
        self.configure(relief='raised', borderwidth=2, padding=5)

        # Create main content frame
        content_frame = ttk.Frame(self)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Header with Order Number and Status Indicator
        header_frame = ttk.Frame(content_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))

        order_num = self.order_data.get('OrderNumber', 'N/A')
        ttk.Label(header_frame, text=f"Order: {order_num}", font=("Arial", 10, "bold")).pack(side=tk.LEFT)

        # Status indicator (checkmark or X)
        status_color = "green" if self.has_pdf else "red"
        status_symbol = "✓" if self.has_pdf else "✗"
        status_label = tk.Label(header_frame, text=status_symbol, fg=status_color, font=("Arial", 12, "bold"))
        status_label.pack(side=tk.RIGHT)

        # Order details
        details_frame = ttk.Frame(content_frame)
        details_frame.pack(fill=tk.X, pady=(0, 5))

        customer = self.order_data.get('Customer', 'N/A')
        job_ref = self.order_data.get('JobReference', 'N/A')
        designer = self.order_data.get('Designer', 'N/A')

        ttk.Label(details_frame, text=f"Customer: {customer}").pack(anchor=tk.W)
        ttk.Label(details_frame, text=f"Job Ref: {job_ref}").pack(anchor=tk.W)
        ttk.Label(details_frame, text=f"Designer: {designer}").pack(anchor=tk.W)

        # Browse button
        browse_btn = ttk.Button(content_frame, text="Browse PDF", command=self.browse_pdf)
        browse_btn.pack(pady=(5, 0))

    def browse_pdf(self):
        """Allow manual PDF selection for this order"""
        file_path = filedialog.askopenfilename(
            title=f"Select PDF for Order {self.order_data.get('OrderNumber', '')}",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if file_path:
            self.pdf_path = file_path
            self.has_pdf = True
            messagebox.showinfo("PDF Selected", f"PDF assigned to order {self.order_data.get('OrderNumber', '')}")
            # TODO: Update the visual indicator and notify parent

class TwoWeekView(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.current_start_date = self.get_week_start(datetime.now())
        self.order_cards = []

        self.setup_ui()

    def get_week_start(self, date: datetime) -> datetime:
        """Get the Monday of the week containing the given date"""
        days_since_monday = date.weekday()
        return date - timedelta(days=days_since_monday)

    def setup_ui(self):
        # Navigation header
        nav_frame = ttk.Frame(self)
        nav_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(nav_frame, text="< Previous", command=self.prev_2weeks).pack(side=tk.LEFT)
        self.date_label = ttk.Label(nav_frame, text="", font=("Arial", 12, "bold"))
        self.date_label.pack(side=tk.LEFT, expand=True)
        ttk.Button(nav_frame, text="Next >", command=self.next_2weeks).pack(side=tk.RIGHT)

        # Scrollable content area
        self.create_scrollable_area()

        self.update_date_display()

    def create_scrollable_area(self):
        # Create canvas and scrollbar for scrollable content
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def update_date_display(self):
        end_date = self.current_start_date + timedelta(days=13)  # 2 weeks
        date_text = f"{self.current_start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
        self.date_label.config(text=date_text)

    def prev_2weeks(self):
        self.current_start_date -= timedelta(days=14)
        self.update_date_display()
        self.refresh_cards()

    def next_2weeks(self):
        self.current_start_date += timedelta(days=14)
        self.update_date_display()
        self.refresh_cards()

    def clear_cards(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.order_cards.clear()

    def add_order_card(self, order_data: Dict, has_pdf: bool = False):
        card = OrderCard(self.scrollable_frame, order_data, has_pdf)
        card.pack(fill=tk.X, padx=5, pady=2)
        self.order_cards.append(card)

    def refresh_cards(self):
        # This will be called by the parent to refresh the display
        self.clear_cards()

class DocumentManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Document Manager - Bistrack Plot Correlation")
        self.root.geometry("1400x900")

        # Initialize components
        self.settings_manager = SettingsManager()
        self.db_manager = DatabaseManager()
        self.pdf_processor = PDFProcessor()

        # Data storage
        self.csv_data = None
        self.current_orders = []

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('document_manager.log'),
                logging.StreamHandler()
            ]
        )

        self.setup_ui()
        self.setup_archive_folder()

    def setup_archive_folder(self):
        """Create archive folder if it doesn't exist"""
        archive_path = Path(self.settings_manager.get("archive_path"))
        archive_path.mkdir(exist_ok=True)

    def setup_ui(self):
        """Create the main user interface"""
        # Create menu bar
        self.create_menu_bar()

        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Search bar at top
        self.create_search_bar(main_frame)

        # Control frame with sync button
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(10, 10))

        # Single Sync button
        self.sync_btn = ttk.Button(
            control_frame,
            text="🔄 SYNC",
            command=self.sync_data,
            width=20,
            style="Accent.TButton"
        )
        self.sync_btn.pack(side=tk.LEFT)

        # Status label
        self.status_label = ttk.Label(control_frame, text="Ready - Configure file locations in Settings")
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))

        # Two-week view
        self.two_week_view = TwoWeekView(main_frame)
        self.two_week_view.pack(fill=tk.BOTH, expand=True)

    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="File Locations", command=self.open_settings_dialog)
        settings_menu.add_separator()
        settings_menu.add_command(label="View Log", command=self.view_log)

    def create_search_bar(self, parent):
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(search_frame, text="Search Historical Data:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=(10, 5))
        search_entry.bind('<Return>', self.perform_search)

        ttk.Button(search_frame, text="Search", command=self.perform_search).pack(side=tk.LEFT)
        ttk.Button(search_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=(5, 0))

    def open_settings_dialog(self):
        """Open the file locations settings dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("File Locations Settings")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()

        # CSV Path setting
        csv_frame = ttk.LabelFrame(dialog, text="Bistrack CSV File Location", padding=10)
        csv_frame.pack(fill=tk.X, padx=10, pady=5)

        self.csv_path_var = tk.StringVar(value=self.settings_manager.get("csv_path"))
        ttk.Entry(csv_frame, textvariable=self.csv_path_var, width=50, state='readonly').pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(csv_frame, text="Browse", command=self.browse_csv_path).pack(side=tk.RIGHT, padx=(5, 0))

        # PDF Path setting
        pdf_frame = ttk.LabelFrame(dialog, text="PDF Folder Location", padding=10)
        pdf_frame.pack(fill=tk.X, padx=10, pady=5)

        self.pdf_path_var = tk.StringVar(value=self.settings_manager.get("pdf_path"))
        ttk.Entry(pdf_frame, textvariable=self.pdf_path_var, width=50, state='readonly').pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(pdf_frame, text="Browse", command=self.browse_pdf_path).pack(side=tk.RIGHT, padx=(5, 0))

        # Archive Path setting
        archive_frame = ttk.LabelFrame(dialog, text="Archive Folder Location", padding=10)
        archive_frame.pack(fill=tk.X, padx=10, pady=5)

        self.archive_path_var = tk.StringVar(value=self.settings_manager.get("archive_path"))
        ttk.Entry(archive_frame, textvariable=self.archive_path_var, width=50).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(archive_frame, text="Browse", command=self.browse_archive_path).pack(side=tk.RIGHT, padx=(5, 0))

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Save", command=self.save_settings).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=(0, 5))

        self.settings_dialog = dialog

    def browse_csv_path(self):
        file_path = filedialog.askopenfilename(
            title="Select Bistrack CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.csv_path_var.set(file_path)

    def browse_pdf_path(self):
        folder_path = filedialog.askdirectory(title="Select PDF Folder")
        if folder_path:
            self.pdf_path_var.set(folder_path)

    def browse_archive_path(self):
        folder_path = filedialog.askdirectory(title="Select Archive Folder")
        if folder_path:
            self.archive_path_var.set(folder_path)

    def save_settings(self):
        self.settings_manager.set("csv_path", self.csv_path_var.get())
        self.settings_manager.set("pdf_path", self.pdf_path_var.get())
        self.settings_manager.set("archive_path", self.archive_path_var.get())

        self.settings_dialog.destroy()
        self.status_label.config(text="Settings saved successfully")

    def sync_data(self):
        """Main sync operation - refresh CSV and correlate PDFs"""
        if not self.validate_settings():
            return

        try:
            self.status_label.config(text="Syncing data...")
            self.root.update()

            # Load CSV data
            csv_path = self.settings_manager.get("csv_path")
            if csv_path and Path(csv_path).exists():
                self.csv_data = pd.read_csv(csv_path)
                logging.info(f"Loaded {len(self.csv_data)} records from CSV")
            else:
                messagebox.showerror("Error", "CSV file not found. Please check file locations in Settings.")
                return

            # Process PDF correlations
            self.process_pdf_correlations()

            # Update display
            self.update_display()

            self.status_label.config(text=f"Sync complete - {len(self.current_orders)} orders processed")

        except Exception as e:
            messagebox.showerror("Sync Error", f"Failed to sync data:\n{str(e)}")
            logging.error(f"Sync failed: {e}")
            self.status_label.config(text="Sync failed")

    def validate_settings(self) -> bool:
        csv_path = self.settings_manager.get("csv_path")
        pdf_path = self.settings_manager.get("pdf_path")

        if not csv_path or not pdf_path:
            messagebox.showwarning("Settings Required", "Please configure CSV and PDF paths in Settings > File Locations")
            return False

        if not Path(csv_path).exists():
            messagebox.showerror("File Not Found", f"CSV file not found: {csv_path}")
            return False

        if not Path(pdf_path).exists():
            messagebox.showerror("Folder Not Found", f"PDF folder not found: {pdf_path}")
            return False

        return True

    def process_pdf_correlations(self):
        """Process PDF files and match with CSV orders"""
        pdf_folder = Path(self.settings_manager.get("pdf_path"))
        pdf_files = list(pdf_folder.glob("*.pdf"))

        # Create a dictionary of found PDFs by order number
        pdf_matches = {}
        for pdf_file in pdf_files:
            order_num = self.pdf_processor.extract_sales_order(pdf_file)
            if order_num:
                pdf_matches[order_num] = str(pdf_file)

        # Process each CSV order
        self.current_orders = []
        for _, row in self.csv_data.iterrows():
            order_data = row.to_dict()
            order_num = str(order_data.get('OrderNumber', ''))

            # Check if this order has a matching PDF
            has_pdf = order_num in pdf_matches

            order_info = {
                'order_data': order_data,
                'has_pdf': has_pdf,
                'pdf_path': pdf_matches.get(order_num, None)
            }
            self.current_orders.append(order_info)

    def update_display(self):
        """Update the two-week view with current orders"""
        self.two_week_view.clear_cards()

        # Filter orders for current 2-week period (if date filtering is needed)
        # For now, show all orders
        for order_info in self.current_orders:
            self.two_week_view.add_order_card(
                order_info['order_data'],
                order_info['has_pdf']
            )

    def perform_search(self, event=None):
        """Perform search in historical data"""
        search_term = self.search_var.get().strip()
        if not search_term:
            return

        # TODO: Implement historical search functionality
        messagebox.showinfo("Search", f"Searching for: {search_term}\n(Search functionality to be implemented)")

    def clear_search(self):
        """Clear search and return to normal view"""
        self.search_var.set("")
        if hasattr(self, 'csv_data') and self.csv_data is not None:
            self.update_display()

    def view_log(self):
        """Open log file viewer"""
        try:
            log_path = Path("document_manager.log")
            if log_path.exists():
                # Create a simple log viewer window
                log_window = tk.Toplevel(self.root)
                log_window.title("Application Log")
                log_window.geometry("800x600")

                text_widget = tk.Text(log_window, wrap=tk.WORD)
                scrollbar = ttk.Scrollbar(log_window, orient=tk.VERTICAL, command=text_widget.yview)
                text_widget.configure(yscrollcommand=scrollbar.set)

                with open(log_path, 'r') as f:
                    log_content = f.read()
                    text_widget.insert(tk.END, log_content)

                text_widget.config(state=tk.DISABLED)
                text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            else:
                messagebox.showinfo("Log", "No log file found")

        except Exception as e:
            messagebox.showerror("Error", f"Could not open log file: {e}")

def main():
    root = tk.Tk()
    app = DocumentManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()