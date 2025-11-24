#!/usr/bin/env python3
"""
Document Manager V2.1 - Main Application with 2-Week Calendar and PDF Actions
Enhanced UI with actionable cards and relationship tracking
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
from two_week_calendar_widget import TwoWeekCalendarWidget
from archive_manager import ArchiveManager

class SettingsManagerV2:
    def __init__(self):
        self.settings_file = "settings_v2.json"
        self.default_settings = {
            "csv_path": "",
            "pdf_path": "",
            "archive_path": "archive",
            "version": "2.1.0"
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

class DocumentManagerV21:
    def __init__(self, root):
        self.root = root
        self.root.title("Document Manager V2.1 - Calendar View with PDF Actions")
        self.root.geometry("1600x900")

        # Initialize components
        self.settings_manager = SettingsManagerV2()
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
                logging.FileHandler('document_manager_v2.1.log'),
                logging.StreamHandler()
            ]
        )

        self.setup_ui()

    def setup_ui(self):
        """Create the main user interface"""
        # Create menu bar
        self.create_menu_bar()

        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Search bar at top
        self.create_search_bar(main_frame)

        # Control frame with sync button and info
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(10, 10))

        # Sync button with enhanced styling
        self.sync_btn = ttk.Button(
            control_frame,
            text="🔄 SYNC DATA",
            command=self.sync_data,
            width=25
        )
        self.sync_btn.pack(side=tk.LEFT)

        # Statistics display
        self.stats_frame = ttk.LabelFrame(control_frame, text="Current Status", padding=5)
        self.stats_frame.pack(side=tk.LEFT, padx=(20, 0))

        self.stats_label = tk.Label(self.stats_frame, text="No data loaded", font=("Arial", 9))
        self.stats_label.pack()

        # Status label
        self.status_label = ttk.Label(control_frame, text="Ready - Configure file locations in Settings")
        self.status_label.pack(side=tk.RIGHT)

        # Two-week calendar view
        self.calendar_widget = TwoWeekCalendarWidget(main_frame)
        self.calendar_widget.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Set up calendar callbacks
        self.calendar_widget.on_order_pdf_updated = self.on_order_pdf_updated

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

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_search_bar(self, parent):
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(search_frame, text="Search Orders:").pack(side=tk.LEFT)

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=(10, 5))
        search_entry.bind('<Return>', self.perform_search)

        # Search type selection
        self.search_type_var = tk.StringVar(value="general")
        search_type_combo = ttk.Combobox(
            search_frame,
            textvariable=self.search_type_var,
            values=["general", "order", "customer"],
            width=10,
            state="readonly"
        )
        search_type_combo.pack(side=tk.LEFT, padx=(5, 5))

        ttk.Button(search_frame, text="Search", command=self.perform_search).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(search_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=(5, 0))

    def open_settings_dialog(self):
        """Open the file locations settings dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("File Locations Settings")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()

        # CSV Path setting
        csv_frame = ttk.LabelFrame(dialog, text="Bistrack CSV File Location", padding=10)
        csv_frame.pack(fill=tk.X, padx=10, pady=5)

        self.csv_path_var = tk.StringVar(value=self.settings_manager.get("csv_path"))
        csv_entry = ttk.Entry(csv_frame, textvariable=self.csv_path_var, width=60, state='readonly')
        csv_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(csv_frame, text="Browse", command=self.browse_csv_path).pack(side=tk.RIGHT, padx=(5, 0))

        # PDF Path setting
        pdf_frame = ttk.LabelFrame(dialog, text="PDF Folder Location", padding=10)
        pdf_frame.pack(fill=tk.X, padx=10, pady=5)

        self.pdf_path_var = tk.StringVar(value=self.settings_manager.get("pdf_path"))
        pdf_entry = ttk.Entry(pdf_frame, textvariable=self.pdf_path_var, width=60, state='readonly')
        pdf_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(pdf_frame, text="Browse", command=self.browse_pdf_path).pack(side=tk.RIGHT, padx=(5, 0))

        # Archive Path setting
        archive_frame = ttk.LabelFrame(dialog, text="Archive Folder Location", padding=10)
        archive_frame.pack(fill=tk.X, padx=10, pady=5)

        self.archive_path_var = tk.StringVar(value=self.settings_manager.get("archive_path"))
        archive_entry = ttk.Entry(archive_frame, textvariable=self.archive_path_var, width=60)
        archive_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(archive_frame, text="Browse", command=self.browse_archive_path).pack(side=tk.RIGHT, padx=(5, 0))

        # Information label
        info_label = ttk.Label(
            dialog,
            text="Note: Changes will take effect after clicking Save and running Sync",
            font=("Arial", 9, "italic")
        )
        info_label.pack(pady=10)

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

        # Update archive manager with new path
        self.archive_manager = ArchiveManager(self.settings_manager.get("archive_path"))

        self.settings_dialog.destroy()
        self.status_label.config(text="Settings saved successfully")

        # Update calendar with new PDF folder path
        self.calendar_widget.set_pdf_folder_path(self.settings_manager.get("pdf_path"))

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
            self.update_statistics_display()

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
        self.calendar_widget.clear_all_cards()

        # Get all relationships with their current status
        relationships = self.relationship_manager.get_orders_with_relationships()

        for rel in relationships:
            self.calendar_widget.add_order_card(
                rel,
                rel['has_pdf'],
                rel.get('pdf_path')
            )

    def update_statistics_display(self):
        """Update the statistics display"""
        stats = self.db_manager.get_statistics()

        stats_text = f"Orders: {stats.get('total_relationships', 0)} | " \
                    f"With PDF: {stats.get('relationships_with_pdf', 0)} | " \
                    f"Without PDF: {stats.get('relationships_without_pdf', 0)}"

        self.stats_label.config(text=stats_text)

    def on_order_pdf_updated(self, order_data: dict, pdf_path: str):
        """Handle PDF updates from calendar widget"""
        try:
            order_number = order_data.get('OrderNumber', '')
            relationship = self.relationship_manager.get_relationship_by_order(order_number)

            if relationship:
                success = self.relationship_manager.update_relationship_pdf(
                    relationship['relationship_id'],
                    pdf_path,
                    "manual_attachment"
                )

                if success:
                    self.update_statistics_display()
                    logging.info(f"PDF manually attached to order {order_number}")
                else:
                    messagebox.showerror("Error", "Failed to update PDF assignment")

        except Exception as e:
            logging.error(f"Failed to handle PDF update: {e}")
            messagebox.showerror("Error", f"Failed to update PDF assignment: {str(e)}")

    def perform_search(self, event=None):
        """Perform search in relationships"""
        search_term = self.search_var.get().strip()
        if not search_term:
            return

        try:
            search_type = self.search_type_var.get()
            results = self.db_manager.search_relationships(search_term, search_type)

            if results:
                # Display results in a new window
                self.show_search_results(search_term, results)
            else:
                messagebox.showinfo("Search Results", f"No results found for '{search_term}'")

        except Exception as e:
            logging.error(f"Search failed: {e}")
            messagebox.showerror("Search Error", f"Search failed: {str(e)}")

    def show_search_results(self, search_term: str, results: list):
        """Show search results in a popup window"""
        results_window = tk.Toplevel(self.root)
        results_window.title(f"Search Results: '{search_term}' ({len(results)} found)")
        results_window.geometry("800x600")

        # Create treeview for results
        tree_frame = ttk.Frame(results_window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ('Order', 'Customer', 'Job Ref', 'Designer', 'Date Required', 'PDF Status')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Populate results
        for result in results:
            csv_data = result.get('csv_data', {})
            pdf_status = "✓ Has PDF" if result.get('pdf_path') else "✗ No PDF"

            tree.insert('', tk.END, values=(
                csv_data.get('OrderNumber', ''),
                csv_data.get('Customer', ''),
                csv_data.get('JobReference', ''),
                csv_data.get('Designer', ''),
                csv_data.get('DateRequired', ''),
                pdf_status
            ))

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Close button
        ttk.Button(results_window, text="Close", command=results_window.destroy).pack(pady=5)

    def clear_search(self):
        """Clear search and return to normal view"""
        self.search_var.set("")
        self.update_calendar_display()

    def load_initial_data(self):
        """Load initial data if settings are configured"""
        csv_path = self.settings_manager.get("csv_path")
        pdf_path = self.settings_manager.get("pdf_path")

        if csv_path and pdf_path and Path(csv_path).exists() and Path(pdf_path).exists():
            # Auto-load data on startup
            self.root.after(1000, self.sync_data)  # Delay to allow UI to finish loading

        # Set PDF folder path for calendar widget
        if pdf_path:
            self.calendar_widget.set_pdf_folder_path(pdf_path)

    def show_statistics(self):
        """Show detailed statistics window"""
        stats = self.db_manager.get_statistics()

        stats_window = tk.Toplevel(self.root)
        stats_window.title("Database Statistics")
        stats_window.geometry("400x500")
        stats_window.transient(self.root)

        # Create statistics display
        stats_text = f"""Database Statistics

Relationships:
  Total Active: {stats.get('total_relationships', 0)}
  With PDF: {stats.get('relationships_with_pdf', 0)}
  Without PDF: {stats.get('relationships_without_pdf', 0)}

PDF Operations:
  Total Attachments: {stats.get('total_pdf_attachments', 0)}
  Total Replacements: {stats.get('total_pdf_replacements', 0)}
  Changes Today: {stats.get('pdf_changes_today', 0)}

Archive:
  Archived PDFs: {stats.get('total_archived_pdfs', 0)}

Activity:
  Operations Today: {stats.get('operations_today', 0)}
  Searches This Week: {stats.get('searches_this_week', 0)}
"""

        text_widget = tk.Text(stats_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.insert(tk.END, stats_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)

        ttk.Button(stats_window, text="Close", command=stats_window.destroy).pack(pady=5)

    def view_log(self):
        """Open log file viewer"""
        try:
            log_path = Path("document_manager_v2.1.log")
            if log_path.exists():
                log_window = tk.Toplevel(self.root)
                log_window.title("Application Log")
                log_window.geometry("900x700")

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
        about_text = """Document Manager V2.1

Features:
• 2-week calendar view with Date Required positioning
• Clickable order cards with PDF action menus
• View, Print, Email, Attach/Replace, Save PDF functions
• Relationship tracking with unique identifiers
• OrderNumber-based PDF matching (unchanged)
• Dynamic visual indicators (red ❌ to green ✅)
• Search functionality for historical data
• PDF archival system
• Comprehensive database tracking

Built with Python and Tkinter
Database: SQLite with relationship tracking
"""

        messagebox.showinfo("About Document Manager V2.1", about_text)

def main():
    root = tk.Tk()

    # Set application icon and styling
    try:
        root.tk.call('tk', 'scaling', 1.0)  # Adjust UI scaling if needed
    except:
        pass

    app = DocumentManagerV21(root)
    root.mainloop()

if __name__ == "__main__":
    main()