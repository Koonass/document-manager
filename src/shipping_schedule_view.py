#!/usr/bin/env python3
"""
Shipping Schedule View - Display orders grouped by date required
Read-only view for reviewing upcoming shipments
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime
from typing import List, Dict
from collections import defaultdict
from pathlib import Path
import platform
import subprocess
import os


class DateSection(tk.Frame):
    """Section showing all orders for a specific date"""

    def __init__(self, parent, date_str: str, orders: List[Dict], csv_db=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.date_str = date_str
        self.orders = orders
        self.csv_db = csv_db

        self.setup_section()

    def setup_section(self):
        """Create the date section with header and order list"""
        # Configure main frame
        self.configure(bg='#ffffff', relief='solid', borderwidth=1)

        # Header frame with date
        header_frame = tk.Frame(self, bg='#3498db', height=40)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Header title with date and count
        header_label = tk.Label(
            header_frame,
            text=f"{self.date_str} ({len(self.orders)} orders)",
            font=("Segoe UI", 14, "bold"),
            bg='#3498db',
            fg='white'
        )
        header_label.pack(side=tk.LEFT, padx=15, pady=10)

        # Create orders list
        if self.orders:
            self.create_orders_list()
        else:
            # Empty state
            empty_label = tk.Label(
                self,
                text="No orders for this date",
                font=("Segoe UI", 10, "italic"),
                bg='#ffffff',
                fg='#7f8c8d'
            )
            empty_label.pack(pady=20)

    def create_orders_list(self):
        """Create the detailed orders list"""
        # Create treeview frame
        tree_frame = tk.Frame(self, bg='#ffffff')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Define columns - same as search results plus CSV Status
        columns = ('Order', 'Customer', 'Job Ref', 'Designer', 'PDF Status', 'CSV Status')

        # Configure style for larger text
        style = ttk.Style()
        style.configure("Schedule.Treeview", rowheight=28, font=("Segoe UI", 11))
        style.configure("Schedule.Treeview.Heading", font=("Segoe UI", 12, "bold"))

        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                 height=min(len(self.orders), 10), style="Schedule.Treeview")

        # Configure columns
        column_widths = {
            'Order': 100,
            'Customer': 200,
            'Job Ref': 150,
            'Designer': 120,
            'PDF Status': 130,
            'CSV Status': 180
        }

        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'CSV Status':
                self.tree.column(col, width=column_widths.get(col, 100), anchor='center')
            else:
                self.tree.column(col, width=column_widths.get(col, 100))

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Populate orders
        for order in self.orders:
            self.add_order_to_tree(order)

        # Bind double-click to view PDF
        self.tree.bind('<Double-1>', self.on_tree_double_click)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def add_order_to_tree(self, order: Dict):
        """Add an order to the tree view"""
        csv_data = order.get('csv_data', {})

        # Get PDF status
        if order.get('pdf_path') or order.get('has_pdf'):
            attachment_method = order.get('attachment_method')
            if attachment_method == 'manual':
                pdf_status = "✅ 📎 Manual"
            elif attachment_method == 'automatic':
                pdf_status = "✅ Auto"
            elif order.get('processed', False):
                pdf_status = "✅ Processed"
            else:
                pdf_status = "✅ Has PDF"
        else:
            if order.get('processed', False):
                pdf_status = "✅ Processed"
            else:
                pdf_status = "❌ No PDF"

        # Get CSV status
        csv_status = self._get_csv_status(csv_data.get('OrderNumber', ''))

        values = (
            csv_data.get('OrderNumber', ''),
            csv_data.get('Customer', ''),
            csv_data.get('JobReference', ''),
            csv_data.get('Designer', ''),
            pdf_status,
            csv_status
        )

        item_id = self.tree.insert('', tk.END, values=values)

        # Store order data for double-click
        if not hasattr(self, 'order_data_map'):
            self.order_data_map = {}
        self.order_data_map[item_id] = order

    def _get_csv_status(self, order_number: str) -> str:
        """Get CSV status from database for display"""
        if not order_number:
            return "❌ No CSV"

        try:
            if not hasattr(self, 'csv_db') or not self.csv_db:
                return "❌ No CSV"

            # Query CSV files for this order
            csv_files = self.csv_db.get_csv_files_by_order(order_number)

            if not csv_files:
                return "❌ No CSV"

            # Get the most recent CSV
            csv_file = csv_files[0]  # Already sorted by added_date DESC

            status = csv_file.get('status', 'pending')
            validation_status = csv_file.get('validation_status', 'not_validated')

            # Return formatted status
            if status == 'uploaded':
                return "✅ Uploaded"
            elif status == 'archived':
                return "📦 Archived"
            elif validation_status == 'valid':
                return "✓ Ready"
            elif validation_status == 'has_errors':
                return "❌ Has Errors"
            elif validation_status == 'has_warnings':
                return "⚠️ Warnings"
            elif validation_status == 'not_validated':
                return "⚪ Not Validated"
            else:
                return "📄 Has CSV"

        except Exception as e:
            logging.error(f"Error getting CSV status for order {order_number}: {e}")
            return "❓ Unknown"

    def on_tree_double_click(self, event):
        """Handle double-click on tree item - view PDF if available"""
        if not self.tree.selection():
            return

        item = self.tree.selection()[0]

        # Get order data from our mapping
        if not hasattr(self, 'order_data_map') or item not in self.order_data_map:
            return

        order_data = self.order_data_map[item]

        # Double-click to view PDF if available
        if order_data.get('pdf_path'):
            self.view_pdf(order_data['pdf_path'])

    def view_pdf(self, pdf_path: str):
        """Open PDF in default viewer"""
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', pdf_path))
            elif platform.system() == 'Windows':  # Windows
                os.startfile(pdf_path)
            else:  # linux variants
                subprocess.call(('xdg-open', pdf_path))
        except Exception as e:
            messagebox.showerror("Error", f"Could not open PDF:\n{str(e)}")


class ShippingScheduleView(tk.Toplevel):
    """View showing shipping schedule grouped by date required"""

    def __init__(self, parent, start_date: datetime, end_date: datetime, orders: List[Dict],
                 csv_db=None, pdf_processor=None, relationship_manager=None, title=None):
        super().__init__(parent)

        self.start_date = start_date
        self.end_date = end_date
        self.orders = orders
        self.csv_db = csv_db
        self.pdf_processor = pdf_processor
        self.relationship_manager = relationship_manager
        self.custom_title = title

        # Set window properties
        self.title(title or "Shipping Schedule")
        self.geometry("1200x800")

        # Make window modal
        self.transient(parent)
        self.grab_set()

        self.create_ui()

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def create_ui(self):
        """Create the main UI"""
        # Title bar
        title_frame = tk.Frame(self, bg='#2c3e50', height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text=self.custom_title or "Shipping Schedule",
            font=("Segoe UI", 18, "bold"),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)

        # Summary info
        summary_label = tk.Label(
            title_frame,
            text=f"Total: {len(self.orders)} orders",
            font=("Segoe UI", 12),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        summary_label.pack(side=tk.RIGHT, padx=20, pady=15)

        # Scrollable content frame
        canvas = tk.Canvas(self, bg='#ecf0f1', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='#ecf0f1')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Group orders by date
        self.create_date_sections()

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Close button at bottom
        close_frame = tk.Frame(self, bg='#ecf0f1')
        close_frame.pack(fill=tk.X, padx=10, pady=10)

        close_btn = tk.Button(
            close_frame,
            text="Close",
            command=self.destroy,
            font=("Segoe UI", 12),
            bg='#95a5a6',
            fg='white',
            border=0,
            padx=25,
            pady=8,
            cursor='hand2'
        )
        close_btn.pack(side=tk.RIGHT)

    def create_date_sections(self):
        """Create sections grouped by date"""
        # Group orders by date
        orders_by_date = defaultdict(list)

        for order in self.orders:
            date_display = order.get('date_display', 'Unknown Date')
            orders_by_date[date_display].append(order)

        # Create a section for each date
        for date_str in sorted(orders_by_date.keys()):
            date_orders = orders_by_date[date_str]

            date_section = DateSection(
                self.scrollable_frame,
                date_str,
                date_orders,
                csv_db=self.csv_db
            )
            date_section.pack(fill=tk.X, pady=(0, 10))

        # If no orders
        if not orders_by_date:
            empty_label = tk.Label(
                self.scrollable_frame,
                text="No orders found for this period",
                font=("Segoe UI", 14, "italic"),
                bg='#ecf0f1',
                fg='#7f8c8d'
            )
            empty_label.pack(pady=50)
