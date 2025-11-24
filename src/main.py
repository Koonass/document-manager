#!/usr/bin/env python3
"""
Document Manager - Main Application Entry Point
Matches Bistrack CSV sales orders with PDF plot files
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import sqlite3
from pathlib import Path
import logging
from datetime import datetime, timedelta
import re
from typing import Dict, List, Optional

from pdf_processor import PDFProcessor
from database_manager import DatabaseManager
from calendar_widget import WeekdayCalendar

class DocumentManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Document Manager - Bistrack Plot Correlation")
        self.root.geometry("1200x800")

        # Initialize components
        self.db_manager = DatabaseManager()
        self.pdf_processor = PDFProcessor()

        # Data storage
        self.csv_data = None
        self.pdf_folder_path = None

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

    def setup_ui(self):
        """Create the main user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="Document Manager", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=2, pady=(0, 20), sticky=(tk.W, tk.E))

        # Import CSV button
        self.import_btn = ttk.Button(
            control_frame,
            text="Import Bistrack Schedule (.csv)",
            command=self.import_csv,
            width=30
        )
        self.import_btn.grid(row=0, column=0, padx=(0, 10))

        # Sync PDF folder button
        self.sync_btn = ttk.Button(
            control_frame,
            text="Sync with Plot Folder (.pdf)",
            command=self.sync_pdf_folder,
            width=30
        )
        self.sync_btn.grid(row=0, column=1, padx=(10, 0))

        # Status label
        self.status_label = ttk.Label(control_frame, text="Ready to import data")
        self.status_label.grid(row=1, column=0, columnspan=2, pady=(10, 0))

        # Calendar and results frame
        results_frame = ttk.Frame(main_frame)
        results_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # Weekday calendar
        self.calendar = WeekdayCalendar(results_frame)
        self.calendar.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def import_csv(self):
        """Import Bistrack CSV schedule"""
        file_path = filedialog.askopenfilename(
            title="Select Bistrack Schedule CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            self.csv_data = pd.read_csv(file_path)
            self.status_label.config(text=f"Imported {len(self.csv_data)} records from CSV")
            logging.info(f"Successfully imported CSV: {file_path}")

            # Store CSV data in database
            self.db_manager.store_csv_data(self.csv_data)

        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import CSV file:\n{str(e)}")
            logging.error(f"CSV import failed: {e}")

    def sync_pdf_folder(self):
        """Sync with PDF folder and correlate with CSV data"""
        if self.csv_data is None:
            messagebox.showwarning("Warning", "Please import CSV data first")
            return

        folder_path = filedialog.askdirectory(
            title="Select PDF Plot Folder"
        )

        if not folder_path:
            return

        try:
            self.pdf_folder_path = Path(folder_path)
            self.status_label.config(text="Processing PDF files...")
            self.root.update()

            # Process PDFs and correlate with CSV
            correlations = self.process_pdf_correlation()

            # Filter out already processed items
            unprocessed = self.filter_unprocessed(correlations)

            # Update calendar display
            self.update_calendar_display(unprocessed)

            self.status_label.config(
                text=f"Found {len(unprocessed)} unprocessed items from {len(correlations)} total correlations"
            )

        except Exception as e:
            messagebox.showerror("Sync Error", f"Failed to sync PDF folder:\n{str(e)}")
            logging.error(f"PDF sync failed: {e}")

    def process_pdf_correlation(self) -> List[Dict]:
        """Process PDF files and correlate with CSV data"""
        correlations = []
        pdf_files = list(self.pdf_folder_path.glob("*.pdf"))

        for pdf_file in pdf_files:
            try:
                # Extract sales order number from PDF
                sales_order = self.pdf_processor.extract_sales_order(pdf_file)

                if sales_order:
                    # Find matching CSV record
                    csv_match = self.find_csv_match(sales_order)

                    if csv_match is not None:
                        correlation = {
                            'sales_order': sales_order,
                            'pdf_path': str(pdf_file),
                            'csv_data': csv_match,
                            'correlation_date': datetime.now()
                        }
                        correlations.append(correlation)

            except Exception as e:
                logging.warning(f"Failed to process PDF {pdf_file}: {e}")

        return correlations

    def find_csv_match(self, sales_order: str) -> Optional[Dict]:
        """Find matching CSV record for sales order"""
        # Assuming CSV has a column named 'Sales Order' or similar
        # This may need adjustment based on actual CSV structure
        for column in self.csv_data.columns:
            if 'sales' in column.lower() and 'order' in column.lower():
                matches = self.csv_data[self.csv_data[column].astype(str) == str(sales_order)]
                if not matches.empty:
                    return matches.iloc[0].to_dict()

        return None

    def filter_unprocessed(self, correlations: List[Dict]) -> List[Dict]:
        """Filter out already processed correlations"""
        unprocessed = []

        for correlation in correlations:
            if not self.db_manager.is_processed(correlation['sales_order'], correlation['pdf_path']):
                unprocessed.append(correlation)

        return unprocessed

    def update_calendar_display(self, unprocessed_items: List[Dict]):
        """Update calendar with unprocessed items"""
        self.calendar.clear_events()

        for item in unprocessed_items:
            # Extract date from CSV data if available
            date_str = self.extract_date_from_csv(item['csv_data'])
            if date_str:
                self.calendar.add_event(date_str, f"SO: {item['sales_order']}", item)

    def extract_date_from_csv(self, csv_row: Dict) -> Optional[str]:
        """Extract date from CSV row data"""
        # Look for date columns in CSV
        date_columns = [col for col in csv_row.keys() if 'date' in col.lower()]

        if date_columns:
            date_value = csv_row[date_columns[0]]
            try:
                # Parse date and return in YYYY-MM-DD format
                parsed_date = pd.to_datetime(date_value)
                return parsed_date.strftime('%Y-%m-%d')
            except:
                pass

        return None

def main():
    root = tk.Tk()
    app = DocumentManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()