#!/usr/bin/env python3
"""
Document Manager V2.2 - Main Application with Statistics Calendar
Simplified 10-box layout with daily statistics display
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime, timedelta
import json

from pdf_processor import PDFProcessor
from enhanced_database_v2 import EnhancedDatabaseV2
from relationship_manager import RelationshipManager
from statistics_calendar_widget import StatisticsCalendarWidget
from archive_manager import ArchiveManager

class SettingsManagerV22:
    def __init__(self):
        self.settings_file = "settings_v2_2.json"
        self.default_settings = {
            "csv_path": "",
            "pdf_path": "",
            "archive_path": "archive",
            "version": "2.2.0"
        }
        self.settings = self.load_settings()

    def load_settings(self) -> dict:
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

class DocumentManagerV22:
    def __init__(self, root):
        self.root = root
        self.root.title("Document Manager V2.2 - Statistics Calendar")
        self.root.geometry("1400x800")

        # Initialize components
        self.settings_manager = SettingsManagerV22()
        self.db_manager = EnhancedDatabaseV2()
        self.relationship_manager = RelationshipManager(self.db_manager)
        self.pdf_processor = PDFProcessor()
        self.archive_manager = ArchiveManager(self.settings_manager.get("archive_path"))

        # Data storage
        self.csv_data = None

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('document_manager_v2.2.log'),
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

        # Statistics calendar (main content)
        self.calendar_widget = StatisticsCalendarWidget(main_frame)
        self.calendar_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Set processors for enhanced functionality
        self.calendar_widget.set_processors(self.pdf_processor, self.relationship_manager)

        # Load initial data if settings are configured
        self.load_initial_data()

    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="File Locations", command=self.open_settings_dialog)
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

    def open_settings_dialog(self):
        """Open the file locations settings dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("File Locations Settings")
        dialog.geometry("650x450")
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

        # CSV Path setting
        csv_frame = ttk.LabelFrame(content_frame, text="Bistrack CSV File Location", padding=15)
        csv_frame.pack(fill=tk.X, pady=(0, 10))

        self.csv_path_var = tk.StringVar(value=self.settings_manager.get("csv_path"))
        csv_entry = ttk.Entry(csv_frame, textvariable=self.csv_path_var, width=60, state='readonly')
        csv_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(csv_frame, text="Browse", command=self.browse_csv_path).pack(side=tk.RIGHT, padx=(10, 0))

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

    def save_settings(self, dialog):
        self.settings_manager.set("csv_path", self.csv_path_var.get())
        self.settings_manager.set("pdf_path", self.pdf_path_var.get())
        self.settings_manager.set("archive_path", self.archive_path_var.get())

        # Update archive manager with new path
        self.archive_manager = ArchiveManager(self.settings_manager.get("archive_path"))

        dialog.destroy()
        self.status_label.config(text="Settings saved successfully")

    def sync_data(self):
        """Main sync operation - load CSV and match PDFs"""
        if not self.validate_settings():
            return

        try:
            self.status_label.config(text="Syncing data...")
            self.sync_btn.config(state="disabled", text="⏳ Syncing...")
            self.root.update()

            # Load CSV data
            csv_path = self.settings_manager.get("csv_path")
            if csv_path and Path(csv_path).exists():
                self.csv_data = pd.read_csv(csv_path)
                logging.info(f"Loaded {len(self.csv_data)} records from CSV")
            else:
                messagebox.showerror("Error", "CSV file not found. Please check file locations in Settings.")
                return

            # Sync CSV data with relationships
            csv_records = self.csv_data.to_dict('records')
            new_count, updated_count, unchanged_count = self.relationship_manager.sync_csv_data(csv_records)

            # Match PDFs to relationships
            pdf_folder = Path(self.settings_manager.get("pdf_path"))
            pdf_files = [str(f) for f in pdf_folder.glob("*.pdf")]
            matched_count, unmatched_count = self.relationship_manager.match_pdfs_to_relationships(
                pdf_files, self.pdf_processor
            )

            # Update calendar display
            self.update_calendar_display()

            # Update statistics
            self.update_overall_statistics_display()

            self.status_label.config(
                text=f"Sync complete: {new_count} new orders, {matched_count} PDFs matched"
            )

            logging.info(
                f"Sync completed - Orders: {new_count} new, {updated_count} updated | "
                f"PDFs: {matched_count} matched, {unmatched_count} unmatched"
            )

        except Exception as e:
            messagebox.showerror("Sync Error", f"Failed to sync data:\n{str(e)}")
            logging.error(f"Sync failed: {e}")
            self.status_label.config(text="Sync failed")

        finally:
            self.sync_btn.config(state="normal", text="🔄 SYNC DATA")

    def validate_settings(self) -> bool:
        csv_path = self.settings_manager.get("csv_path")
        pdf_path = self.settings_manager.get("pdf_path")

        if not csv_path or not pdf_path:
            messagebox.showwarning(
                "Settings Required",
                "Please configure CSV and PDF paths in Settings > File Locations"
            )
            return False

        if not Path(csv_path).exists():
            messagebox.showerror("File Not Found", f"CSV file not found: {csv_path}")
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

    def perform_search(self, event=None):
        """Perform search in relationships"""
        search_term = self.search_var.get().strip()
        if not search_term:
            return

        try:
            results = self.db_manager.search_relationships(search_term, 'general')

            if results:
                self.show_search_results(search_term, results)
            else:
                messagebox.showinfo("Search Results", f"No results found for '{search_term}'")

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
            self.relationship_manager
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
        csv_path = self.settings_manager.get("csv_path")
        pdf_path = self.settings_manager.get("pdf_path")

        if csv_path and pdf_path and Path(csv_path).exists() and Path(pdf_path).exists():
            # Auto-load data on startup
            self.root.after(1000, self.sync_data)  # Delay to allow UI to finish loading

    def show_statistics(self):
        """Show detailed statistics window"""
        stats = self.db_manager.get_statistics()

        stats_window = tk.Toplevel(self.root)
        stats_window.title("Database Statistics")
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
        about_window.title("About Document Manager V2.2")
        about_window.geometry("500x400")
        about_window.configure(bg='#ecf0f1')
        about_window.transient(self.root)

        # Header
        header_frame = tk.Frame(about_window, bg='#34495e', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        header_label = tk.Label(
            header_frame,
            text="Document Manager V2.2",
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

    app = DocumentManagerV22(root)
    root.mainloop()

if __name__ == "__main__":
    main()