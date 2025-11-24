#!/usr/bin/env python3
"""
Document Manager V2.4 - Main Application with BisTrack CSV Management
Includes CSV validation, SKU checking, and BisTrack import workflow
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime, timedelta
import json
from typing import Optional

from pdf_processor import PDFProcessor
from enhanced_database_v2 import EnhancedDatabaseV2
from relationship_manager import RelationshipManager
from statistics_calendar_widget import StatisticsCalendarWidget
from archive_manager import ArchiveManager
from csv_cleanup_dialog import show_csv_cleanup_dialog
from csv_processor import CSVProcessor
from enhanced_database_manager import EnhancedDatabaseManager

class SettingsManagerV24:
    def __init__(self):
        self.settings_file = "settings_v2_4.json"

        # Determine template path relative to application location (portable across machines)
        # Look for template in LABEL TEMPLATE folder relative to the script location
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level from src/ to the root Document Manager folder
        root_dir = os.path.dirname(script_dir)
        self.template_path = os.path.join(root_dir, "LABEL TEMPLATE", "Contract_Lumber_Label_Template.docx")

        # Log the template path for debugging
        logging.info(f"Template path set to: {self.template_path}")

        self.default_settings = {
            "html_path": "",
            "pdf_path": "",
            "archive_path": "archive",
            "db_path": "document_manager_v2.1.db",
            # CSV/BisTrack settings
            "products_file_path": "",
            "bistrack_import_folder": "",
            # Printer preferences
            "printer1_name": "",
            "printer1_color_mode": "Color",
            "printer1_copies": 1,
            "printer1_enabled": True,
            "printer2_name": "",
            "printer2_color_mode": "Color",
            "printer2_copies": 1,
            "printer2_enabled": True,
            "folder_printer_name": "",
            "folder_printer_enabled": True,
            "version": "2.4.0"
        }
        self.settings = self.load_settings()

    def load_settings(self) -> dict:
        try:
            if Path(self.settings_file).exists():
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Remove template_path from loaded settings if it exists (we use hardcoded relative path)
                    if 'template_path' in loaded_settings:
                        del loaded_settings['template_path']
                        logging.info("Removed old template_path from settings (using relative path)")
                    return loaded_settings
        except Exception as e:
            logging.warning(f"Could not load settings: {e}")
        return self.default_settings.copy()

    def save_settings(self):
        try:
            # Make a copy of settings and remove template_path before saving
            settings_to_save = self.settings.copy()
            if 'template_path' in settings_to_save:
                del settings_to_save['template_path']

            with open(self.settings_file, 'w') as f:
                json.dump(settings_to_save, f, indent=2)
        except Exception as e:
            logging.error(f"Could not save settings: {e}")

    def get(self, key: str) -> str:
        # Special case for template_path - return hardcoded value
        if key == "template_path":
            return self.template_path
        return self.settings.get(key, self.default_settings.get(key, ""))

    def set(self, key: str, value: str):
        # Ignore attempts to set template_path (it's hardcoded)
        if key == "template_path":
            return
        self.settings[key] = value
        self.save_settings()

class DocumentManagerV24:
    def __init__(self, root):
        self.root = root
        self.root.title("Document Manager V2.4 - Enhanced Search & Navigation")
        self.root.geometry("1400x800")

        # Initialize components
        self.settings_manager = SettingsManagerV24()
        self.db_manager = EnhancedDatabaseV2(self.settings_manager.get("db_path"))
        self.relationship_manager = RelationshipManager(self.db_manager)
        self.pdf_processor = PDFProcessor()
        self.archive_manager = ArchiveManager(self.settings_manager.get("archive_path"))

        # Initialize CSV database manager for CSV tracking
        self.csv_db = EnhancedDatabaseManager(self.settings_manager.get("db_path"))

        # Data storage
        self.html_data = None

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('document_manager_v2.3.log'),
                logging.StreamHandler()
            ]
        )

        self.setup_ui()

    def setup_ui(self):
        """Create the main user interface"""
        # Configure root window
        self.root.configure(bg='#ecf0f1')

        # Create menu bar
        self.create_menu_bar()

        # Main container with modern styling
        main_frame = tk.Frame(self.root, bg='#ecf0f1')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header section
        self.create_header_section(main_frame)

        # Content container: sidebar + calendar
        content_container = tk.Frame(main_frame, bg='#ecf0f1')
        content_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Left sidebar
        self.create_sidebar(content_container)

        # Statistics calendar (main content)
        self.calendar_widget = StatisticsCalendarWidget(content_container)
        self.calendar_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Set processors for enhanced functionality
        self.calendar_widget.set_processors(
            self.pdf_processor,
            self.relationship_manager,
            self.archive_manager,
            self.settings_manager.get("template_path"),
            self.settings_manager,
            csv_db=self.csv_db  # Pass CSV database for CSV tracking
        )

        # Load initial data if settings are configured
        self.load_initial_data()

    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="File Locations", command=self.open_settings_dialog)
        settings_menu.add_command(label="Printer Settings", command=self.open_printer_settings_dialog)
        settings_menu.add_separator()
        settings_menu.add_command(label="Database Statistics", command=self.show_statistics)
        settings_menu.add_command(label="View Log", command=self.view_log)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Archive Management", command=self.open_archive_manager)
        tools_menu.add_command(label="Export Data", command=self.export_data)
        tools_menu.add_command(label="Cleanup Old Data", command=self.cleanup_data)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh Statistics", command=self.refresh_all_statistics)
        view_menu.add_command(label="Go to Today", command=self.go_to_today)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_header_section(self, parent):
        """Create the header section with controls and search"""
        header_frame = tk.Frame(parent, bg='#34495e', height=120)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Left section - Sync button and status
        left_frame = tk.Frame(header_frame, bg='#34495e')
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=15)

        # Sync button with enhanced styling
        self.sync_btn = tk.Button(
            left_frame,
            text="🔄 SYNC DATA",
            command=self.sync_data,
            font=("Segoe UI", 12, "bold"),
            bg='#27ae60',
            fg='white',
            border=0,
            padx=25,
            pady=10,
            cursor='hand2'
        )
        self.sync_btn.pack(side=tk.TOP)

        # Status label
        self.status_label = tk.Label(
            left_frame,
            text="Ready - Configure file locations in Settings",
            font=("Segoe UI", 9),
            bg='#34495e',
            fg='#bdc3c7'
        )
        self.status_label.pack(side=tk.TOP, pady=(5, 0))

        # Center section - Title and overall statistics
        center_frame = tk.Frame(header_frame, bg='#34495e')
        center_frame.pack(expand=True, fill=tk.BOTH, pady=15)

        # Application title
        title_label = tk.Label(
            center_frame,
            text="Document Manager",
            font=("Segoe UI", 20, "bold"),
            bg='#34495e',
            fg='white'
        )
        title_label.pack()

        # Overall statistics
        self.overall_stats_label = tk.Label(
            center_frame,
            text="No data loaded",
            font=("Segoe UI", 11),
            bg='#34495e',
            fg='#bdc3c7'
        )
        self.overall_stats_label.pack(pady=(5, 0))

        # HTML file info display
        self.html_file_info_label = tk.Label(
            center_frame,
            text="",
            font=("Segoe UI", 9, "italic"),
            bg='#34495e',
            fg='#95a5a6'
        )
        self.html_file_info_label.pack(pady=(3, 0))

        # Right section - Search (make it more prominent)
        right_frame = tk.Frame(header_frame, bg='#34495e', width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=15)
        right_frame.pack_propagate(False)

        # Search label
        search_label = tk.Label(
            right_frame,
            text="Search Orders:",
            font=("Segoe UI", 12, "bold"),
            bg='#34495e',
            fg='white'
        )
        search_label.pack(anchor=tk.W, pady=(0, 5))

        # Search entry and button container
        search_container = tk.Frame(right_frame, bg='#34495e')
        search_container.pack(fill=tk.X)

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_container,
            textvariable=self.search_var,
            font=("Segoe UI", 11),
            width=20
        )
        search_entry.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        search_entry.bind('<Return>', self.perform_search)

        search_btn = tk.Button(
            search_container,
            text="🔍 SEARCH ORDERS",
            command=self.perform_search,
            font=("Segoe UI", 11, "bold"),
            bg='#e67e22',
            fg='white',
            border=0,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        search_btn.pack(side=tk.TOP, fill=tk.X)

    def create_sidebar(self, parent):
        """Create the left sidebar with quick links"""
        sidebar_frame = tk.Frame(parent, bg='#34495e', width=180)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        sidebar_frame.pack_propagate(False)

        # Sidebar title
        sidebar_title = tk.Label(
            sidebar_frame,
            text="Quick Views",
            font=("Segoe UI", 14, "bold"),
            bg='#34495e',
            fg='white'
        )
        sidebar_title.pack(pady=(20, 10), padx=10)

        # Separator
        separator = tk.Frame(sidebar_frame, bg='#7f8c8d', height=1)
        separator.pack(fill=tk.X, padx=10, pady=(0, 10))

        # View Week button
        view_week_btn = tk.Button(
            sidebar_frame,
            text="📅 View Week",
            command=self.show_current_week_view,
            font=("Segoe UI", 11),
            bg='#3498db',
            fg='white',
            border=0,
            padx=15,
            pady=10,
            cursor='hand2',
            anchor='w'
        )
        view_week_btn.pack(fill=tk.X, padx=10, pady=5)

        # View Unmatched PDFs button
        unmatched_btn = tk.Button(
            sidebar_frame,
            text="📄 Unmatched PDFs",
            command=self.show_unmatched_pdfs,
            font=("Segoe UI", 11),
            bg='#e67e22',
            fg='white',
            border=0,
            padx=15,
            pady=10,
            cursor='hand2',
            anchor='w'
        )
        unmatched_btn.pack(fill=tk.X, padx=10, pady=5)

        # Process CSVs button
        csv_btn = tk.Button(
            sidebar_frame,
            text="📦 Process CSVs",
            command=self.show_csv_processing_view,
            font=("Segoe UI", 11),
            bg='#9b59b6',
            fg='white',
            border=0,
            padx=15,
            pady=10,
            cursor='hand2',
            anchor='w'
        )
        csv_btn.pack(fill=tk.X, padx=10, pady=5)

        # View Shipping Schedule button
        shipping_btn = tk.Button(
            sidebar_frame,
            text="📅 View Shipping Schedule",
            command=self.show_shipping_schedule,
            font=("Segoe UI", 11),
            bg='#16a085',
            fg='white',
            border=0,
            padx=15,
            pady=10,
            cursor='hand2',
            anchor='w'
        )
        shipping_btn.pack(fill=tk.X, padx=10, pady=5)

        # Info label
        info_label = tk.Label(
            sidebar_frame,
            text="Quick access to\nkey views",
            font=("Segoe UI", 9, "italic"),
            bg='#34495e',
            fg='#bdc3c7',
            justify=tk.CENTER
        )
        info_label.pack(pady=(20, 0))

    def show_current_week_view(self):
        """Show expanded view of all jobs for the current week"""
        from datetime import datetime, timedelta

        # Get start of current week (Monday)
        today = datetime.now()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6)  # Sunday

        logging.info(f"View Week: Querying orders from {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")

        # Query ALL orders from database (not just what's in the calendar widget)
        all_orders = self.relationship_manager.get_orders_with_relationships()

        logging.info(f"View Week: Found {len(all_orders)} total orders in database")

        # Filter to only orders within the current week
        week_orders = []
        for order in all_orders:
            csv_data = order.get('csv_data', {})
            date_required = csv_data.get('DateRequired', '')

            if date_required:
                try:
                    # Try to parse the date
                    order_date = None
                    for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d']:
                        try:
                            order_date = datetime.strptime(str(date_required), fmt).date()
                            break
                        except:
                            continue

                    # Check if order is within current week
                    if order_date and week_start.date() <= order_date <= week_end.date():
                        # Add display date
                        order_with_date = order.copy()
                        order_with_date['display_date'] = order_date.strftime('%a %m/%d')
                        week_orders.append(order_with_date)
                        logging.debug(f"Added order {csv_data.get('OrderNumber')} with date {order_date}")
                except Exception as e:
                    logging.warning(f"Could not parse date '{date_required}' for order {csv_data.get('OrderNumber')}: {e}")

        logging.info(f"View Week: Filtered to {len(week_orders)} orders in current week")

        # Sort by date
        week_orders.sort(key=lambda x: x.get('display_date', ''))

        # Open enhanced expanded view for the week
        from enhanced_expanded_view import EnhancedExpandedView

        archive_manager = getattr(self, 'archive_manager', None)
        template_path = self.settings_manager.get("template_path")

        expanded_view = EnhancedExpandedView(
            self.root,
            week_start,  # Use week start as the date
            week_orders,  # Use the filtered week orders
            self.pdf_processor,
            self.relationship_manager,
            archive_manager,
            template_path,
            self.settings_manager,
            title=f"Current Week: {week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}",
            show_date_column=True  # Enable date column for week view
        )
        expanded_view.set_statistics_refresh_callback(self.refresh_all_statistics)

    def show_unmatched_pdfs(self):
        """Show all PDFs that don't have a match in the database"""
        pdf_folder = Path(self.settings_manager.get("pdf_path"))

        if not pdf_folder.exists():
            messagebox.showwarning("PDF Folder Not Found", "Please configure the PDF folder path in Settings.")
            return

        # Get all PDF files
        all_pdfs = list(pdf_folder.glob("*.pdf"))
        logging.info(f"Unmatched PDFs: Found {len(all_pdfs)} total PDF files in {pdf_folder}")

        # Get all matched PDFs from database
        matched_pdfs = set()
        if hasattr(self, 'relationship_manager'):
            # Query database for all PDFs with matches
            relationships = self.relationship_manager.get_orders_with_relationships()
            for rel in relationships:
                if rel.get('pdf_path'):
                    matched_pdfs.add(str(Path(rel['pdf_path']).name))

        logging.info(f"Unmatched PDFs: Found {len(matched_pdfs)} matched PDFs in database")

        # Find unmatched PDFs
        unmatched_pdfs = []
        for pdf_path in all_pdfs:
            if pdf_path.name not in matched_pdfs:
                unmatched_pdfs.append({
                    'path': str(pdf_path),
                    'name': pdf_path.name,
                    'size': pdf_path.stat().st_size,
                    'modified': datetime.fromtimestamp(pdf_path.stat().st_mtime)
                })
                logging.debug(f"Unmatched: {pdf_path.name}")

        logging.info(f"Unmatched PDFs: {len(unmatched_pdfs)} unmatched files to display")

        # Show unmatched PDFs dialog
        self.show_unmatched_pdfs_dialog(unmatched_pdfs)

    def show_unmatched_pdfs_dialog(self, unmatched_pdfs):
        """Display dialog showing unmatched PDFs"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Unmatched PDFs")
        dialog.geometry("900x600")
        dialog.configure(bg='#ecf0f1')
        dialog.transient(self.root)

        # Header
        header_frame = tk.Frame(dialog, bg='#34495e', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        header_label = tk.Label(
            header_frame,
            text=f"Unmatched PDFs ({len(unmatched_pdfs)} files)",
            font=("Segoe UI", 14, "bold"),
            bg='#34495e',
            fg='white'
        )
        header_label.pack(expand=True)

        # Content
        content_frame = tk.Frame(dialog, bg='#ecf0f1')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        if not unmatched_pdfs:
            tk.Label(
                content_frame,
                text="✅ All PDFs are matched to orders!",
                font=("Segoe UI", 12),
                bg='#ecf0f1',
                fg='#27ae60'
            ).pack(expand=True)
        else:
            logging.info(f"Creating treeview with {len(unmatched_pdfs)} unmatched PDFs")

            # Create treeview
            columns = ('Filename', 'Size', 'Modified')
            tree = ttk.Treeview(content_frame, columns=columns, show='headings', height=20)

            tree.heading('Filename', text='Filename')
            tree.heading('Size', text='Size')
            tree.heading('Modified', text='Modified')

            tree.column('Filename', width=400)
            tree.column('Size', width=100)
            tree.column('Modified', width=150)

            # Add scrollbar
            scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)

            # Populate tree
            items_added = 0
            for pdf in unmatched_pdfs:
                try:
                    size_kb = pdf['size'] / 1024
                    size_str = f"{size_kb:.1f} KB"
                    modified_str = pdf['modified'].strftime("%Y-%m-%d %H:%M")

                    item_id = tree.insert('', tk.END, values=(pdf['name'], size_str, modified_str))
                    # Store full path in a hidden way - we'll use tags instead
                    tree.item(item_id, tags=(pdf['path'],))
                    items_added += 1
                    logging.debug(f"Added tree item: {pdf['name']}")
                except Exception as e:
                    logging.error(f"Error adding PDF {pdf.get('name', 'unknown')} to tree: {e}")

            logging.info(f"Successfully added {items_added} items to treeview")

            # Bind double-click to open PDF
            def on_double_click(event):
                if tree.selection():
                    item = tree.selection()[0]
                    tags = tree.item(item, 'tags')
                    if tags:
                        pdf_path = tags[0]
                        self.open_file(pdf_path)

            tree.bind('<Double-1>', on_double_click)

            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Close button
        close_btn = tk.Button(
            dialog,
            text="Close",
            command=dialog.destroy,
            font=("Segoe UI", 10),
            bg='#95a5a6',
            fg='white',
            border=0,
            padx=20,
            pady=8
        )
        close_btn.pack(pady=(0, 20))

    def open_file(self, file_path):
        """Open a file with the default system application"""
        import subprocess
        import platform

        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', file_path))
            else:  # Linux
                subprocess.call(('xdg-open', file_path))
        except Exception as e:
            logging.error(f"Failed to open file {file_path}: {e}")
            messagebox.showerror("Error", f"Failed to open file:\n{str(e)}")

    def show_csv_processing_view(self):
        """Show CSV processing view for current calendar period"""
        from datetime import datetime, timedelta
        from enhanced_expanded_view import EnhancedExpandedView

        logging.info("Opening CSV Processing View")

        # Get current calendar date range (2-week period)
        if hasattr(self, 'calendar_widget') and hasattr(self.calendar_widget, 'start_date'):
            start_date = self.calendar_widget.start_date
            end_date = start_date + timedelta(days=13)  # 2 weeks
        else:
            # Default to current 2-week period
            today = datetime.now()
            days_since_monday = today.weekday()
            start_date = today - timedelta(days=days_since_monday)
            end_date = start_date + timedelta(days=13)

        logging.info(f"CSV Processing View: Date range {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

        # Get all orders with relationships
        all_orders = self.relationship_manager.get_orders_with_relationships()

        # Filter orders in current date range AND have CSVs
        csv_orders = []
        for order in all_orders:
            csv_data = order.get('csv_data', {})
            date_required = csv_data.get('DateRequired', '')
            order_number = csv_data.get('OrderNumber', '')

            if date_required and order_number:
                try:
                    # Parse order date
                    order_date = None
                    for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d']:
                        try:
                            order_date = datetime.strptime(str(date_required), fmt).date()
                            break
                        except:
                            continue

                    # Check if in date range
                    if order_date and start_date.date() <= order_date <= end_date.date():
                        # Check if order has CSV files
                        csv_files = self.csv_db.get_csv_files_by_order(order_number)
                        if csv_files:
                            # Add CSV info to order
                            order_with_csv = order.copy()
                            order_with_csv['display_date'] = order_date.strftime('%a %m/%d')
                            order_with_csv['csv_files'] = csv_files
                            order_with_csv['csv_validation_status'] = csv_files[0].get('validation_status', 'not_validated')
                            csv_orders.append(order_with_csv)
                            logging.debug(f"Added order {order_number} with CSV validation status: {order_with_csv['csv_validation_status']}")

                except Exception as e:
                    logging.warning(f"Could not process order {order_number}: {e}")

        logging.info(f"CSV Processing View: Found {len(csv_orders)} orders with CSVs")

        if not csv_orders:
            messagebox.showinfo(
                "No CSVs Found",
                f"No CSV files found for the period:\n{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}\n\n"
                "Run SYNC to detect CSV files."
            )
            return

        # Sort by date
        csv_orders.sort(key=lambda x: x.get('display_date', ''))

        # Open CSV processing view
        archive_manager = getattr(self, 'archive_manager', None)
        template_path = self.settings_manager.get("template_path")

        expanded_view = EnhancedExpandedView(
            self.root,
            start_date,
            csv_orders,
            self.pdf_processor,
            self.relationship_manager,
            archive_manager,
            template_path,
            self.settings_manager,
            title=f"CSV Processing: {start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}",
            show_date_column=True,
            mode='csv'  # CSV mode
        )
        expanded_view.set_statistics_refresh_callback(self.refresh_all_statistics)

    def show_shipping_schedule(self):
        """Show shipping schedule view - all orders grouped by date required"""
        from datetime import datetime, timedelta
        from shipping_schedule_view import ShippingScheduleView

        logging.info("Opening Shipping Schedule View")

        # Get current calendar date range (2-week period)
        if hasattr(self, 'calendar_widget') and hasattr(self.calendar_widget, 'start_date'):
            start_date = self.calendar_widget.start_date
            end_date = start_date + timedelta(days=13)  # 2 weeks
        else:
            # Default to current 2-week period
            today = datetime.now()
            days_since_monday = today.weekday()
            start_date = today - timedelta(days=days_since_monday)
            end_date = start_date + timedelta(days=13)

        logging.info(f"Shipping Schedule: Date range {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

        # Get all orders with relationships
        all_orders = self.relationship_manager.get_orders_with_relationships()

        # Filter orders in current date range
        schedule_orders = []
        for order in all_orders:
            csv_data = order.get('csv_data', {})
            date_required = csv_data.get('DateRequired', '')
            order_number = csv_data.get('OrderNumber', '')

            if date_required:
                try:
                    # Parse order date
                    order_date = None
                    for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d']:
                        try:
                            order_date = datetime.strptime(str(date_required), fmt).date()
                            break
                        except:
                            continue

                    # Check if in date range
                    if order_date and start_date.date() <= order_date <= end_date.date():
                        # Add date information
                        order_with_date = order.copy()
                        order_with_date['parsed_date'] = order_date
                        order_with_date['date_display'] = order_date.strftime('%a, %b %d, %Y')
                        schedule_orders.append(order_with_date)

                except Exception as e:
                    logging.warning(f"Could not process order {order_number}: {e}")

        logging.info(f"Shipping Schedule: Found {len(schedule_orders)} orders")

        if not schedule_orders:
            messagebox.showinfo(
                "No Orders",
                f"No orders found for the period:\n{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
            )
            return

        # Sort by date
        schedule_orders.sort(key=lambda x: x.get('parsed_date'))

        # Open shipping schedule view
        schedule_view = ShippingScheduleView(
            self.root,
            start_date,
            end_date,
            schedule_orders,
            self.csv_db,
            self.pdf_processor,
            self.relationship_manager,
            title=f"Shipping Schedule: {start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
        )

    def show_csv_cleanup(self):
        """Show BisTrack CSV cleanup and validation dialog"""
        pdf_folder = Path(self.settings_manager.get("pdf_path"))
        products_file = self.settings_manager.get("products_file_path")

        if not pdf_folder.exists():
            messagebox.showwarning(
                "CSV Folder Not Set",
                "PDF folder path is not configured.\n\n"
                "CSVs are stored in the same folder as PDFs.\n"
                "Please configure the PDF folder path in Settings first."
            )
            return

        # Initialize EnhancedDatabaseManager for CSV tracking
        db_path = self.settings_manager.get("db_path")
        csv_db = EnhancedDatabaseManager(db_path)

        # Show CSV cleanup dialog
        show_csv_cleanup_dialog(
            self.root,
            csv_db,
            str(pdf_folder),
            products_file if products_file else None
        )

    def open_settings_dialog(self):
        """Open the file locations settings dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("File Locations Settings")
        dialog.geometry("650x800")
        dialog.configure(bg='#ecf0f1')
        dialog.transient(self.root)
        dialog.grab_set()

        # Header
        header_frame = tk.Frame(dialog, bg='#34495e', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        header_label = tk.Label(
            header_frame,
            text="File Locations Configuration",
            font=("Segoe UI", 14, "bold"),
            bg='#34495e',
            fg='white'
        )
        header_label.pack(expand=True)

        # Content frame
        content_frame = tk.Frame(dialog, bg='#ecf0f1')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # HTML Path setting
        html_frame = ttk.LabelFrame(content_frame, text="Bistrack HTML Export Folder Location", padding=15)
        html_frame.pack(fill=tk.X, pady=(0, 10))

        self.html_path_var = tk.StringVar(value=self.settings_manager.get("html_path"))
        html_entry = ttk.Entry(html_frame, textvariable=self.html_path_var, width=60, state='readonly')
        html_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(html_frame, text="Browse", command=self.browse_html_path).pack(side=tk.RIGHT, padx=(10, 0))

        # Info about auto-selection
        tk.Label(
            html_frame,
            text="💡 The newest HTML file in this folder will be used automatically during sync",
            font=("Segoe UI", 8, "italic"),
            fg='#7f8c8d'
        ).pack(anchor=tk.W, pady=(5, 0))

        # PDF Path setting
        pdf_frame = ttk.LabelFrame(content_frame, text="PDF Folder Location", padding=15)
        pdf_frame.pack(fill=tk.X, pady=(0, 10))

        self.pdf_path_var = tk.StringVar(value=self.settings_manager.get("pdf_path"))
        pdf_entry = ttk.Entry(pdf_frame, textvariable=self.pdf_path_var, width=60, state='readonly')
        pdf_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(pdf_frame, text="Browse", command=self.browse_pdf_path).pack(side=tk.RIGHT, padx=(10, 0))

        # Archive Path setting
        archive_frame = ttk.LabelFrame(content_frame, text="Archive Folder Location", padding=15)
        archive_frame.pack(fill=tk.X, pady=(0, 10))

        self.archive_path_var = tk.StringVar(value=self.settings_manager.get("archive_path"))
        archive_entry = ttk.Entry(archive_frame, textvariable=self.archive_path_var, width=60)
        archive_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(archive_frame, text="Browse", command=self.browse_archive_path).pack(side=tk.RIGHT, padx=(10, 0))

        # Database Path setting
        db_frame = ttk.LabelFrame(content_frame, text="Database File Location (Shared/Network)", padding=15)
        db_frame.pack(fill=tk.X, pady=(0, 10))

        self.db_path_var = tk.StringVar(value=self.settings_manager.get("db_path"))
        db_entry = ttk.Entry(db_frame, textvariable=self.db_path_var, width=60)
        db_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(db_frame, text="Browse", command=self.browse_db_path).pack(side=tk.RIGHT, padx=(10, 0))

        # Info about database path
        tk.Label(
            db_frame,
            text="💡 For shared installations, use network path (e.g., \\\\SERVER\\Share\\document_manager_v2.1.db)\n⚠️ Requires application restart to take effect",
            font=("Segoe UI", 8, "italic"),
            fg='#e67e22',
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(5, 0))

        # Products File Path setting (for CSV validation)
        products_frame = ttk.LabelFrame(content_frame, text="Products Master File (for SKU Validation)", padding=15)
        products_frame.pack(fill=tk.X, pady=(0, 10))

        self.products_path_var = tk.StringVar(value=self.settings_manager.get("products_file_path"))
        products_entry = ttk.Entry(products_frame, textvariable=self.products_path_var, width=60, state='readonly')
        products_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(products_frame, text="Browse", command=self.browse_products_file).pack(side=tk.RIGHT, padx=(10, 0))

        tk.Label(
            products_frame,
            text="💡 CSV file with SKU,Description,Active columns for validating BisTrack import CSVs",
            font=("Segoe UI", 8, "italic"),
            fg='#7f8c8d'
        ).pack(anchor=tk.W, pady=(5, 0))

        # BisTrack Import Folder setting
        bistrack_frame = ttk.LabelFrame(content_frame, text="BisTrack Import Folder Location", padding=15)
        bistrack_frame.pack(fill=tk.X, pady=(0, 10))

        self.bistrack_import_var = tk.StringVar(value=self.settings_manager.get("bistrack_import_folder"))
        bistrack_entry = ttk.Entry(bistrack_frame, textvariable=self.bistrack_import_var, width=60, state='readonly')
        bistrack_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(bistrack_frame, text="Browse", command=self.browse_bistrack_folder).pack(side=tk.RIGHT, padx=(10, 0))

        tk.Label(
            bistrack_frame,
            text="💡 Target folder where validated CSVs will be uploaded for BisTrack import",
            font=("Segoe UI", 8, "italic"),
            fg='#7f8c8d'
        ).pack(anchor=tk.W, pady=(5, 0))

        # Information
        info_label = tk.Label(
            content_frame,
            text="💡 Changes will take effect after clicking Save and running Sync",
            font=("Segoe UI", 9, "italic"),
            bg='#ecf0f1',
            fg='#7f8c8d'
        )
        info_label.pack(pady=(10, 0))

        # Buttons
        button_frame = tk.Frame(content_frame, bg='#ecf0f1')
        button_frame.pack(fill=tk.X, pady=(20, 0))

        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            font=("Segoe UI", 10),
            bg='#95a5a6',
            fg='white',
            border=0,
            padx=20,
            pady=8
        )
        cancel_btn.pack(side=tk.RIGHT)

        save_btn = tk.Button(
            button_frame,
            text="Save",
            command=lambda: self.save_settings(dialog),
            font=("Segoe UI", 10, "bold"),
            bg='#27ae60',
            fg='white',
            border=0,
            padx=20,
            pady=8
        )
        save_btn.pack(side=tk.RIGHT, padx=(0, 10))

    def find_latest_html_file(self, folder_path: str) -> Optional[str]:
        """
        Find the newest HTML file in the specified folder

        Args:
            folder_path: Path to folder containing HTML exports

        Returns:
            Path to the newest HTML file, or None if no files found
        """
        try:
            folder = Path(folder_path)
            if not folder.exists() or not folder.is_dir():
                logging.warning(f"HTML folder does not exist: {folder_path}")
                return None

            # Get all .htm and .html files
            html_files = list(folder.glob("*.htm")) + list(folder.glob("*.html"))

            if not html_files:
                logging.warning(f"No HTML files found in {folder_path}")
                return None

            # Sort by modification time (newest first)
            html_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

            latest_file = str(html_files[0])
            logging.info(f"Found latest HTML file: {latest_file}")

            return latest_file

        except Exception as e:
            logging.error(f"Error finding latest HTML file: {e}")
            return None

    def browse_html_path(self):
        folder_path = filedialog.askdirectory(title="Select Bistrack HTML Export Folder")
        if folder_path:
            self.html_path_var.set(folder_path)

    def browse_pdf_path(self):
        folder_path = filedialog.askdirectory(title="Select PDF Folder")
        if folder_path:
            self.pdf_path_var.set(folder_path)

    def browse_archive_path(self):
        folder_path = filedialog.askdirectory(title="Select Archive Folder")
        if folder_path:
            self.archive_path_var.set(folder_path)

    def browse_db_path(self):
        file_path = filedialog.asksaveasfilename(
            title="Select Database File Location",
            defaultextension=".db",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")],
            initialfile="document_manager_v2.1.db"
        )
        if file_path:
            self.db_path_var.set(file_path)

    def browse_products_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Products Master File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.products_path_var.set(file_path)

    def browse_bistrack_folder(self):
        folder_path = filedialog.askdirectory(title="Select BisTrack Import Folder")
        if folder_path:
            self.bistrack_import_var.set(folder_path)

    def save_settings(self, dialog):
        # Check if database path changed
        old_db_path = self.settings_manager.get("db_path")
        new_db_path = self.db_path_var.get()
        db_path_changed = old_db_path != new_db_path

        # Save all settings
        self.settings_manager.set("html_path", self.html_path_var.get())
        self.settings_manager.set("pdf_path", self.pdf_path_var.get())
        self.settings_manager.set("archive_path", self.archive_path_var.get())
        self.settings_manager.set("db_path", new_db_path)
        self.settings_manager.set("products_file_path", self.products_path_var.get())
        self.settings_manager.set("bistrack_import_folder", self.bistrack_import_var.get())

        # Update archive manager with new path
        self.archive_manager = ArchiveManager(self.settings_manager.get("archive_path"))

        # Update calendar widget (template path is hardcoded, no need to update)
        self.calendar_widget.set_processors(
            self.pdf_processor,
            self.relationship_manager,
            self.archive_manager,
            self.settings_manager.get("template_path"),
            self.settings_manager,
            csv_db=self.csv_db
        )

        dialog.destroy()

        # Show appropriate message
        if db_path_changed:
            messagebox.showwarning(
                "Restart Required",
                "Database path has been changed.\n\n"
                "⚠️ You must restart the application for this change to take effect.\n\n"
                f"New database location:\n{new_db_path}\n\n"
                "For shared installations, ensure all users point to the same database path."
            )
            self.status_label.config(text="Settings saved - RESTART REQUIRED for database change")
        else:
            self.status_label.config(text="Settings saved successfully")

    def open_printer_settings_dialog(self):
        """Open the printer settings dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Printer Settings")
        dialog.geometry("700x600")
        dialog.configure(bg='#ecf0f1')
        dialog.transient(self.root)
        dialog.grab_set()

        # Header
        header_frame = tk.Frame(dialog, bg='#34495e', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        header_label = tk.Label(
            header_frame,
            text="Default Printer Configuration",
            font=("Segoe UI", 14, "bold"),
            bg='#34495e',
            fg='white'
        )
        header_label.pack(expand=True)

        # Content frame
        content_frame = tk.Frame(dialog, bg='#ecf0f1')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Get available printers
        try:
            import win32print
            available_printers = [printer[2] for printer in win32print.EnumPrinters(
                win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
        except:
            available_printers = []

        if not available_printers:
            tk.Label(
                content_frame,
                text="⚠️ No printers detected. Please install printers and try again.",
                font=("Segoe UI", 11),
                bg='#ecf0f1',
                fg='#e74c3c'
            ).pack(pady=20)

            tk.Button(
                content_frame,
                text="Close",
                command=dialog.destroy,
                font=("Segoe UI", 10),
                bg='#95a5a6',
                fg='white',
                border=0,
                padx=20,
                pady=8
            ).pack()
            return

        # Printer 1: 11x17 (Small Format)
        printer1_frame = ttk.LabelFrame(content_frame, text="11×17 Printer (Small Format)", padding=15)
        printer1_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            printer1_frame,
            text="Default printer for 11×17 plots:",
            font=("Segoe UI", 10),
            bg='white'
        ).pack(anchor=tk.W, pady=(0, 5))

        self.printer1_settings_var = tk.StringVar(value=self.settings_manager.get("printer1_name"))
        printer1_combo = ttk.Combobox(
            printer1_frame,
            textvariable=self.printer1_settings_var,
            values=available_printers,
            state='readonly',
            width=60
        )
        printer1_combo.pack(fill=tk.X)

        if self.printer1_settings_var.get() in available_printers:
            printer1_combo.set(self.printer1_settings_var.get())
        elif available_printers:
            printer1_combo.current(0)

        # Printer 2: 24x36 (Large Format)
        printer2_frame = ttk.LabelFrame(content_frame, text="24×36 Printer (Large Format)", padding=15)
        printer2_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            printer2_frame,
            text="Default printer for 24×36 and larger plots:",
            font=("Segoe UI", 10),
            bg='white'
        ).pack(anchor=tk.W, pady=(0, 5))

        self.printer2_settings_var = tk.StringVar(value=self.settings_manager.get("printer2_name"))
        printer2_combo = ttk.Combobox(
            printer2_frame,
            textvariable=self.printer2_settings_var,
            values=available_printers,
            state='readonly',
            width=60
        )
        printer2_combo.pack(fill=tk.X)

        if self.printer2_settings_var.get() in available_printers:
            printer2_combo.set(self.printer2_settings_var.get())
        elif available_printers:
            printer2_combo.current(0)

        # Folder Printer
        folder_frame = ttk.LabelFrame(content_frame, text="Folder Label Printer", padding=15)
        folder_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            folder_frame,
            text="Default printer for folder labels (Word templates):",
            font=("Segoe UI", 10),
            bg='white'
        ).pack(anchor=tk.W, pady=(0, 5))

        self.folder_settings_var = tk.StringVar(value=self.settings_manager.get("folder_printer_name"))
        folder_combo = ttk.Combobox(
            folder_frame,
            textvariable=self.folder_settings_var,
            values=available_printers,
            state='readonly',
            width=60
        )
        folder_combo.pack(fill=tk.X)

        if self.folder_settings_var.get() in available_printers:
            folder_combo.set(self.folder_settings_var.get())
        elif available_printers:
            folder_combo.current(0)

        # Information
        info_label = tk.Label(
            content_frame,
            text="💡 These printers will be used by default when batch printing.\n"
                 "You can still enable/disable each printer and adjust settings in the batch print window.",
            font=("Segoe UI", 9, "italic"),
            bg='#ecf0f1',
            fg='#7f8c8d',
            justify=tk.LEFT
        )
        info_label.pack(pady=(10, 0))

        # Buttons
        button_frame = tk.Frame(content_frame, bg='#ecf0f1')
        button_frame.pack(fill=tk.X, pady=(20, 0))

        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            font=("Segoe UI", 10),
            bg='#95a5a6',
            fg='white',
            border=0,
            padx=20,
            pady=8
        )
        cancel_btn.pack(side=tk.RIGHT)

        save_btn = tk.Button(
            button_frame,
            text="Save",
            command=lambda: self.save_printer_settings(dialog),
            font=("Segoe UI", 10, "bold"),
            bg='#27ae60',
            fg='white',
            border=0,
            padx=20,
            pady=8
        )
        save_btn.pack(side=tk.RIGHT, padx=(0, 10))

    def save_printer_settings(self, dialog):
        """Save printer settings"""
        self.settings_manager.set("printer1_name", self.printer1_settings_var.get())
        self.settings_manager.set("printer2_name", self.printer2_settings_var.get())
        self.settings_manager.set("folder_printer_name", self.folder_settings_var.get())

        dialog.destroy()
        self.status_label.config(text="Printer settings saved successfully")

    def sync_data(self):
        """Main sync operation - load HTML and match PDFs"""
        print("\n" + "="*80)
        print("SYNC DEBUG: Starting sync operation...")
        print("="*80)

        if not self.validate_settings():
            print("SYNC DEBUG: Settings validation failed")
            return

        try:
            self.status_label.config(text="Syncing data...")
            self.sync_btn.config(state="disabled", text="⏳ Syncing...")
            self.root.update()

            # Load HTML data
            html_folder = self.settings_manager.get("html_path")
            print(f"SYNC DEBUG: HTML folder from settings: {html_folder}")

            # Find the latest HTML file in the folder
            html_path = self.find_latest_html_file(html_folder) if html_folder else None

            if not html_path:
                print(f"SYNC DEBUG: No HTML file found in folder")
                messagebox.showerror("Error", "No HTML files found in the configured folder.\nPlease check file locations in Settings.")
                return

            print(f"SYNC DEBUG: Using HTML file: {html_path}")

            # Get file modification time for display
            file_stat = Path(html_path).stat()
            file_mtime = datetime.fromtimestamp(file_stat.st_mtime)
            file_name = Path(html_path).name

            # Store for later display update
            self.current_html_file = file_name
            self.current_html_time = file_mtime

            if Path(html_path).exists():
                print(f"SYNC DEBUG: HTML file exists, reading with pandas...")
                # Read HTML with explicit header row (first row contains column names)
                html_tables = pd.read_html(html_path, header=0)
                self.html_data = html_tables[0]  # Use first table

                # If columns are still numeric, the first row might be the header
                if isinstance(self.html_data.columns[0], int):
                    print(f"SYNC DEBUG: Columns are numeric, using first row as header...")
                    # First row contains the actual column names
                    self.html_data.columns = self.html_data.iloc[0]
                    # Drop the first row since it's now the header
                    self.html_data = self.html_data.drop(0).reset_index(drop=True)

                print(f"SYNC DEBUG: Successfully loaded {len(self.html_data)} records from HTML")
                print(f"SYNC DEBUG: Columns: {list(self.html_data.columns)[:10]}...")  # Show first 10 columns

                # Check for 4079038 specifically
                if 'OrderNumber' in self.html_data.columns:
                    test_match = self.html_data[self.html_data['OrderNumber'].astype(str).str.contains('4079038', na=False)]
                    print(f"SYNC DEBUG: Order 4079038 in HTML? {len(test_match) > 0}")
                else:
                    print(f"SYNC DEBUG: WARNING - 'OrderNumber' column not found!")
                    print(f"SYNC DEBUG: Available columns: {list(self.html_data.columns)}")

                logging.info(f"Loaded {len(self.html_data)} records from HTML")
            else:
                print(f"SYNC DEBUG: HTML file not found or path is empty")
                messagebox.showerror("Error", "HTML file not found. Please check file locations in Settings.")
                return

            # Sync HTML data with relationships
            print(f"SYNC DEBUG: Converting to records for sync...")
            html_records = self.html_data.to_dict('records')
            print(f"SYNC DEBUG: Starting relationship sync with {len(html_records)} records...")

            new_count, updated_count, unchanged_count = self.relationship_manager.sync_csv_data(html_records)
            print(f"SYNC DEBUG: Sync results - New: {new_count}, Updated: {updated_count}, Unchanged: {unchanged_count}")

            # Clean up orphaned PDFs (PDFs that no longer exist on disk)
            print(f"SYNC DEBUG: Checking for orphaned PDFs...")
            orphaned_count = self.cleanup_orphaned_pdfs()
            print(f"SYNC DEBUG: Cleaned up {orphaned_count} orphaned PDF references")

            # Match PDFs to relationships
            pdf_folder = Path(self.settings_manager.get("pdf_path"))
            print(f"SYNC DEBUG: Matching PDFs from folder: {pdf_folder}")
            pdf_files = [str(f) for f in pdf_folder.glob("*.pdf")]
            print(f"SYNC DEBUG: Found {len(pdf_files)} PDF files")

            matched_count, unmatched_count = self.relationship_manager.match_pdfs_to_relationships(
                pdf_files, self.pdf_processor
            )
            print(f"SYNC DEBUG: PDF matching - Matched: {matched_count}, Unmatched: {unmatched_count}")

            # Match CSVs to orders (same folder as PDFs)
            print(f"SYNC DEBUG: Matching CSVs from folder: {pdf_folder}")
            csv_files = [str(f) for f in pdf_folder.glob("*.csv")]
            print(f"SYNC DEBUG: Found {len(csv_files)} CSV files")

            if csv_files:
                print(f"SYNC DEBUG: CSV files found:")
                for csv_file in csv_files[:5]:  # Show first 5
                    print(f"  - {Path(csv_file).name}")

            csv_processor = CSVProcessor()
            csv_db = EnhancedDatabaseManager(self.settings_manager.get("db_path"))
            csv_matched = 0

            for csv_file in csv_files:
                csv_filename = Path(csv_file).name
                print(f"SYNC DEBUG: Processing CSV: {csv_filename}")

                order_number = csv_processor.extract_sales_order(Path(csv_file))
                print(f"SYNC DEBUG:   → Extracted order number: {order_number}")

                if order_number:
                    # Get material count
                    structure = csv_processor.parse_csv_structure(Path(csv_file))
                    material_count = structure.get('material_count', 0)
                    print(f"SYNC DEBUG:   → Material count: {material_count}")

                    # Assign to database
                    if csv_db.assign_csv_to_order(order_number, csv_file, material_count):
                        csv_matched += 1
                        print(f"SYNC DEBUG:   → ✓ Matched to order {order_number}")
                else:
                    print(f"SYNC DEBUG:   → ✗ Could not extract order number")

            print(f"SYNC DEBUG: CSV matching - Matched: {csv_matched} of {len(csv_files)} CSVs to orders")

            # Update calendar display
            print(f"SYNC DEBUG: Updating calendar display...")
            self.update_calendar_display()

            # Update statistics
            print(f"SYNC DEBUG: Updating statistics...")
            self.update_overall_statistics_display()

            # Update HTML file info display
            print(f"SYNC DEBUG: Updating HTML file info...")
            self.update_html_file_info_display()

            self.status_label.config(
                text=f"Sync complete: {new_count} new orders, {matched_count} PDFs, {csv_matched} CSVs matched"
            )

            logging.info(
                f"Sync completed - Orders: {new_count} new, {updated_count} updated | "
                f"PDFs: {matched_count} matched, {unmatched_count} unmatched"
            )

            print("SYNC DEBUG: Sync completed successfully!")
            print("="*80 + "\n")

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"SYNC DEBUG: ERROR occurred!")
            print(f"SYNC DEBUG: Error type: {type(e).__name__}")
            print(f"SYNC DEBUG: Error message: {str(e)}")
            print(f"SYNC DEBUG: Full traceback:\n{error_details}")

            messagebox.showerror("Sync Error", f"Failed to sync data:\n{str(e)}\n\nCheck console for details.")
            logging.error(f"Sync failed: {e}")
            self.status_label.config(text="Sync failed")

        finally:
            self.sync_btn.config(state="normal", text="🔄 SYNC DATA")

    def cleanup_orphaned_pdfs(self) -> int:
        """
        Remove PDF references from database where the PDF file no longer exists

        Returns:
            Number of orphaned PDFs cleaned up
        """
        try:
            orphaned_count = 0

            # Get all orders with PDF attachments
            all_orders = self.relationship_manager.get_orders_with_relationships()

            for order in all_orders:
                pdf_path = order.get('pdf_path')

                # If order has a PDF path, check if file exists
                if pdf_path:
                    pdf_file = Path(pdf_path)

                    if not pdf_file.exists():
                        # File doesn't exist - remove the PDF reference
                        order_number = order.get('csv_data', {}).get('OrderNumber', 'Unknown')
                        relationship_id = order.get('relationship_id')

                        if relationship_id:
                            # Remove PDF from relationship
                            success = self.relationship_manager.remove_pdf_from_relationship(
                                relationship_id,
                                removal_reason="file_deleted"
                            )

                            if success:
                                orphaned_count += 1
                                logging.info(f"Removed orphaned PDF reference for order {order_number}: {pdf_path}")
                            else:
                                logging.warning(f"Failed to remove orphaned PDF for order {order_number}")

            if orphaned_count > 0:
                logging.info(f"Cleaned up {orphaned_count} orphaned PDF references")

            return orphaned_count

        except Exception as e:
            logging.error(f"Error cleaning up orphaned PDFs: {e}")
            return 0

    def validate_settings(self) -> bool:
        html_path = self.settings_manager.get("html_path")
        pdf_path = self.settings_manager.get("pdf_path")

        if not html_path or not pdf_path:
            messagebox.showwarning(
                "Settings Required",
                "Please configure HTML and PDF paths in Settings > File Locations"
            )
            return False

        # Handle backward compatibility: if html_path is a file, convert to folder
        html_path_obj = Path(html_path)
        if html_path_obj.is_file():
            # Auto-convert old file path to folder path
            folder_path = str(html_path_obj.parent)
            self.settings_manager.set("html_path", folder_path)
            logging.info(f"Auto-converted HTML file path to folder: {folder_path}")
            html_path = folder_path
            html_path_obj = Path(html_path)

        if not html_path_obj.exists() or not html_path_obj.is_dir():
            messagebox.showerror("Folder Not Found", f"HTML export folder not found: {html_path}")
            return False

        if not Path(pdf_path).exists():
            messagebox.showerror("Folder Not Found", f"PDF folder not found: {pdf_path}")
            return False

        return True

    def update_calendar_display(self):
        """Update the calendar with current relationships"""
        # Get all relationships with their current status
        relationships = self.relationship_manager.get_orders_with_relationships()

        # Update calendar widget
        self.calendar_widget.update_calendar_data(relationships)

    def update_overall_statistics_display(self):
        """Update the overall statistics display in header"""
        stats = self.db_manager.get_statistics()

        stats_text = f"📊 Total Orders: {stats.get('total_relationships', 0)} | " \
                    f"✅ With PDF: {stats.get('relationships_with_pdf', 0)} | " \
                    f"❌ Without PDF: {stats.get('relationships_without_pdf', 0)}"

        self.overall_stats_label.config(text=stats_text)

    def update_html_file_info_display(self):
        """Update the HTML file info display in header"""
        if hasattr(self, 'current_html_file') and hasattr(self, 'current_html_time'):
            # Format the datetime nicely
            time_str = self.current_html_time.strftime("%b %d, %Y %I:%M %p")
            info_text = f"📄 Data from: {self.current_html_file} ({time_str})"
            self.html_file_info_label.config(text=info_text)
        else:
            self.html_file_info_label.config(text="")

    def perform_search(self, event=None):
        """Perform search in relationships"""
        search_term = self.search_var.get().strip()
        if not search_term:
            return

        try:
            results = self.db_manager.search_relationships(search_term, 'general')

            # Always show search dialog, even with no results (allows continued searching)
            self.show_search_results(search_term, results)

        except Exception as e:
            logging.error(f"Search failed: {e}")
            messagebox.showerror("Search Error", f"Search failed: {str(e)}")

    def show_search_results(self, search_term: str, results: list):
        """Show search results in an enhanced expanded view card"""
        from enhanced_search_view import EnhancedSearchView

        # Create search view with proper date (using today as placeholder)
        from datetime import datetime
        search_view = EnhancedSearchView(
            self.root,
            search_term,
            results,
            self.pdf_processor,
            self.relationship_manager,
            self.archive_manager
        )
        search_view.set_statistics_refresh_callback(self.refresh_all_statistics)

    def refresh_all_statistics(self):
        """Refresh all statistics displays"""
        if hasattr(self, 'calendar_widget'):
            self.calendar_widget.refresh_statistics()
        self.update_overall_statistics_display()

    def go_to_today(self):
        """Navigate calendar to current date"""
        # This would be implemented to reset calendar to current 2-week period
        messagebox.showinfo("Go to Today", "Navigate to today functionality coming soon!")

    def load_initial_data(self):
        """Load initial data if settings are configured"""
        html_path = self.settings_manager.get("html_path")
        pdf_path = self.settings_manager.get("pdf_path")

        if html_path and pdf_path and Path(html_path).exists() and Path(pdf_path).exists():
            # Auto-load data on startup
            self.root.after(1000, self.sync_data)  # Delay to allow UI to finish loading

    def show_statistics(self):
        """Show detailed statistics window"""
        stats = self.db_manager.get_statistics()

        stats_window = tk.Toplevel(self.root)
        stats_window.title("Database Statistics - V2.4")
        stats_window.geometry("450x550")
        stats_window.configure(bg='#ecf0f1')
        stats_window.transient(self.root)

        # Header
        header_frame = tk.Frame(stats_window, bg='#34495e', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        header_label = tk.Label(
            header_frame,
            text="Database Statistics",
            font=("Segoe UI", 14, "bold"),
            bg='#34495e',
            fg='white'
        )
        header_label.pack(expand=True)

        # Statistics content
        stats_text = f"""
📊 RELATIONSHIPS
   Total Active: {stats.get('total_relationships', 0)}
   With PDF: {stats.get('relationships_with_pdf', 0)}
   Without PDF: {stats.get('relationships_without_pdf', 0)}

📄 PDF OPERATIONS
   Total Attachments: {stats.get('total_pdf_attachments', 0)}
   Total Replacements: {stats.get('total_pdf_replacements', 0)}
   Changes Today: {stats.get('pdf_changes_today', 0)}

🗂️ ARCHIVE
   Archived PDFs: {stats.get('total_archived_pdfs', 0)}

⚡ ACTIVITY
   Operations Today: {stats.get('operations_today', 0)}
   Searches This Week: {stats.get('searches_this_week', 0)}
        """

        text_widget = tk.Text(
            stats_window,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            bg='white',
            fg='#2c3e50',
            padx=20,
            pady=20,
            border=0
        )
        text_widget.insert(tk.END, stats_text.strip())
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Close button
        close_btn = tk.Button(
            stats_window,
            text="Close",
            command=stats_window.destroy,
            font=("Segoe UI", 10),
            bg='#95a5a6',
            fg='white',
            border=0,
            padx=20,
            pady=8
        )
        close_btn.pack(pady=(0, 20))

    def view_log(self):
        """Open log file viewer"""
        try:
            log_path = Path("document_manager_v2.2.log")
            if log_path.exists():
                log_window = tk.Toplevel(self.root)
                log_window.title("Application Log")
                log_window.geometry("1000x700")
                log_window.configure(bg='#ecf0f1')

                # Header
                header_frame = tk.Frame(log_window, bg='#34495e', height=60)
                header_frame.pack(fill=tk.X)
                header_frame.pack_propagate(False)

                header_label = tk.Label(
                    header_frame,
                    text="Application Log",
                    font=("Segoe UI", 14, "bold"),
                    bg='#34495e',
                    fg='white'
                )
                header_label.pack(expand=True)

                # Log content
                text_frame = tk.Frame(log_window, bg='#ecf0f1')
                text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

                text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 9))
                scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
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

    def open_archive_manager(self):
        """Open archive management dialog"""
        messagebox.showinfo("Archive Manager", "Archive management features coming soon!")

    def export_data(self):
        """Export data to file"""
        export_path = filedialog.asksaveasfilename(
            title="Export Data",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if export_path:
            try:
                success = self.db_manager.export_data(export_path)
                if success:
                    messagebox.showinfo("Export", f"Data exported successfully to:\n{export_path}")
                else:
                    messagebox.showerror("Export Error", "Failed to export data")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export data:\n{str(e)}")

    def cleanup_data(self):
        """Clean up old data"""
        result = messagebox.askyesno(
            "Cleanup Confirmation",
            "This will remove old processing logs and search history.\n"
            "Order data and relationships will be preserved.\n\n"
            "Continue with cleanup?"
        )

        if result:
            try:
                cleanup_stats = self.db_manager.cleanup_old_data()
                messagebox.showinfo(
                    "Cleanup Complete",
                    f"Cleanup completed:\n"
                    f"Processing logs removed: {cleanup_stats.get('processing_logs_removed', 0)}\n"
                    f"Search history removed: {cleanup_stats.get('searches_removed', 0)}\n"
                    f"PDF change history removed: {cleanup_stats.get('pdf_changes_removed', 0)}"
                )
            except Exception as e:
                messagebox.showerror("Cleanup Error", f"Cleanup failed:\n{str(e)}")

    def show_about(self):
        """Show about dialog"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About Document Manager V2.4")
        about_window.geometry("500x400")
        about_window.configure(bg='#ecf0f1')
        about_window.transient(self.root)

        # Header
        header_frame = tk.Frame(about_window, bg='#34495e', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        header_label = tk.Label(
            header_frame,
            text="Document Manager V2.4",
            font=("Segoe UI", 16, "bold"),
            bg='#34495e',
            fg='white'
        )
        header_label.pack(expand=True)

        # About content
        about_text = """
🗓️ STATISTICS CALENDAR
• Clean 10-box layout (2 weeks × 5 weekdays)
• Daily statistics at a glance
• Click any day for detailed order view

📊 DAILY STATISTICS
• ✅ Successful PDF matches per day
• ❌ Orders without PDFs per day
• 📋 Previously processed orders per day

🔗 SMART FEATURES
• OrderNumber-based PDF matching
• Relationship tracking with unique identifiers
• Dynamic statistics calculation
• Search historical data

⚙️ ENHANCED WORKFLOW
• Settings-based file location management
• One-click sync operation
• Archive management system
• Comprehensive logging and statistics

Built with Python and Tkinter
Database: SQLite with relationship tracking
        """

        text_widget = tk.Text(
            about_window,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg='white',
            fg='#2c3e50',
            padx=20,
            pady=20,
            border=0
        )
        text_widget.insert(tk.END, about_text.strip())
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Close button
        close_btn = tk.Button(
            about_window,
            text="Close",
            command=about_window.destroy,
            font=("Segoe UI", 10),
            bg='#95a5a6',
            fg='white',
            border=0,
            padx=20,
            pady=8
        )
        close_btn.pack(pady=(0, 20))

def main():
    root = tk.Tk()

    # Set application styling
    try:
        root.tk.call('tk', 'scaling', 1.0)
    except:
        pass

    app = DocumentManagerV24(root)
    root.mainloop()

if __name__ == "__main__":
    main()