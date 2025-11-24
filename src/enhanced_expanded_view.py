#!/usr/bin/env python3
"""
Enhanced Expanded View - Detailed order view with category separation and PDF actions
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
import subprocess
import platform
import os
import logging
from archive_manager import ArchiveManager
from print_preset_manager import PrintPresetManager
from print_preset_ui import PresetManagerDialog
from batch_print_with_presets import (
    PresetSelectionDialog,
    execute_batch_print_with_preset
)
from enhanced_database_manager import EnhancedDatabaseManager
from csv_validator import CSVValidator, ValidationError
from csv_processor import CSVProcessor
from pathlib import Path

class CategorySection(tk.Frame):
    def __init__(self, parent, title: str, color: str, orders: List[Dict], show_date_column: bool = False, csv_db=None, mode='pdf', **kwargs):
        super().__init__(parent, **kwargs)

        self.title = title
        self.color = color
        self.orders = orders
        self.show_date_column = show_date_column  # Whether to show date column (for week view)
        self.csv_db = csv_db  # Database for CSV status queries
        self.mode = mode  # 'pdf' or 'csv' mode
        self.on_pdf_attach = None
        self.on_refresh_needed = None

        self.setup_section()

    def setup_section(self):
        """Create the category section with header and order list"""
        # Configure main frame
        self.configure(bg='#ffffff', relief='solid', borderwidth=1)

        # Header frame
        header_frame = tk.Frame(self, bg=self.color, height=40)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Header title with count
        header_label = tk.Label(
            header_frame,
            text=f"{self.title} ({len(self.orders)})",
            font=("Segoe UI", 18, "bold"),
            bg=self.color,
            fg='white'
        )
        header_label.pack(side=tk.LEFT, padx=15, pady=10)

        # Add "Select All" checkbox for green category only
        if self.color == '#27ae60' and self.orders:
            self.select_all_var = tk.BooleanVar(value=False)
            select_all_cb = tk.Checkbutton(
                header_frame,
                text="Select All",
                variable=self.select_all_var,
                command=self.toggle_all_checkboxes,
                font=("Segoe UI", 12, "bold"),
                bg=self.color,
                fg='white',
                selectcolor=self.color,
                activebackground=self.color,
                activeforeground='white',
                cursor='hand2'
            )
            select_all_cb.pack(side=tk.RIGHT, padx=15, pady=10)

        # Orders list frame
        if self.orders:
            self.create_orders_list()
        else:
            # Empty state
            empty_label = tk.Label(
                self,
                text="No orders in this category",
                font=("Segoe UI", 11, "italic"),
                bg='#ffffff',
                fg='#7f8c8d'
            )
            empty_label.pack(pady=20)

    def create_orders_list(self):
        """Create the detailed orders list"""
        # Create treeview frame
        tree_frame = tk.Frame(self, bg='#ffffff')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Define columns based on mode
        if self.mode == 'csv':
            # CSV mode: Show CSV File column (clickable), no PDF status
            if self.show_date_column:
                columns = ('Include', 'Date', 'Order', 'Customer', 'Job Ref', 'CSV File', 'CSV Status')
            else:
                columns = ('Include', 'Order', 'Customer', 'Job Ref', 'CSV File', 'CSV Status')
        else:
            # PDF mode: Show PDF status, no CSV status
            if self.show_date_column:
                if self.color == '#27ae60':  # Green - has PDFs
                    columns = ('Include', 'Date', 'Order', 'Customer', 'Job Ref', 'PDF Status')
                else:  # Red/Gray - no PDFs or processed
                    columns = ('Include', 'Date', 'Order', 'Customer', 'Job Ref', 'Status')
            else:
                if self.color == '#27ae60':  # Green - has PDFs
                    columns = ('Include', 'Order', 'Customer', 'Job Ref', 'PDF Status')
                else:  # Red/Gray - no PDFs or processed
                    columns = ('Include', 'Order', 'Customer', 'Job Ref', 'Status')

        # Configure style for larger text
        style = ttk.Style()
        style.configure("Custom.Treeview", rowheight=28, font=("Segoe UI", 12), foreground="#000000")
        style.configure("Custom.Treeview.Heading", font=("Segoe UI", 13, "bold"))

        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=min(len(self.orders), 8), style="Custom.Treeview")

        # Configure columns
        column_widths = {
            'Include': 60,
            'Date': 80,
            'Order': 100,
            'Customer': 200,
            'Job Ref': 130,
            'PDF Status': 120,
            'CSV File': 180,
            'CSV Status': 200,
            'Status': 100
        }

        for col in columns:
            self.tree.heading(col, text=col)
            # Center align CSV Status column for better display
            if col == 'CSV Status':
                self.tree.column(col, width=column_widths.get(col, 100), anchor='center')
            else:
                self.tree.column(col, width=column_widths.get(col, 100))

        # Initialize toggle state dictionary
        self.item_toggle_state = {}  # item_id -> True/False

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Populate orders
        for order in self.orders:
            self.add_order_to_tree(order)

        # Bind events
        self.tree.bind('<Button-1>', self.on_tree_click)  # Single click for checkboxes
        self.tree.bind('<Double-1>', self.on_tree_double_click)
        self.tree.bind('<Motion>', self.on_tree_motion)
        self.tree.bind('<Button-3>', self.on_tree_right_click)  # Right-click

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def add_order_to_tree(self, order: Dict):
        """Add an order to the tree view"""
        csv_data = order.get('csv_data', {})

        # All categories show checkboxes (allows reprinting processed jobs and folder labels without PDFs)
        checkbox = "☐"
        initial_state = False

        # Get the display date if available (for week view)
        display_date = order.get('display_date', '')

        # Build values tuple based on mode
        if self.mode == 'csv':
            # CSV mode: Show CSV file name and CSV status
            csv_files = order.get('csv_files', [])
            csv_file_name = Path(csv_files[0].get('current_path', '')).name if csv_files else "No CSV"
            csv_status = self._get_csv_status(order.get('csv_data', {}).get('OrderNumber', ''))

            if self.show_date_column:
                values = (
                    checkbox,
                    display_date,
                    csv_data.get('OrderNumber', ''),
                    csv_data.get('Customer', ''),
                    csv_data.get('JobReference', ''),
                    csv_file_name,
                    csv_status
                )
            else:
                values = (
                    checkbox,
                    csv_data.get('OrderNumber', ''),
                    csv_data.get('Customer', ''),
                    csv_data.get('JobReference', ''),
                    csv_file_name,
                    csv_status
                )
        else:
            # PDF mode: Show PDF status (no CSV status)
            if self.color == '#27ae60':  # Green category - has PDFs
                # Show PDF status with attachment method indicator
                if order.get('pdf_path'):
                    attachment_method = order.get('attachment_method')
                    if attachment_method == 'manual':
                        pdf_status = "✅ 📎 Manual"
                    elif attachment_method == 'automatic':
                        pdf_status = "✅ Auto"
                    else:
                        pdf_status = "✅ Has PDF"
                else:
                    pdf_status = "❌ No PDF"

                if self.show_date_column:
                    values = (
                        checkbox,
                        display_date,
                        csv_data.get('OrderNumber', ''),
                        csv_data.get('Customer', ''),
                        csv_data.get('JobReference', ''),
                        pdf_status
                    )
                else:
                    values = (
                        checkbox,
                        csv_data.get('OrderNumber', ''),
                        csv_data.get('Customer', ''),
                        csv_data.get('JobReference', ''),
                        pdf_status
                    )
            else:  # Red/Gray category - no PDFs or processed
                status = "✅ Processed" if self.color == '#95a5a6' else "❌ No PDF"
                if self.show_date_column:
                    values = (
                        checkbox,
                        display_date,
                        csv_data.get('OrderNumber', ''),
                        csv_data.get('Customer', ''),
                        csv_data.get('JobReference', ''),
                        status
                    )
                else:
                    values = (
                        checkbox,
                        csv_data.get('OrderNumber', ''),
                        csv_data.get('Customer', ''),
                        csv_data.get('JobReference', ''),
                        status
                    )

        # Don't apply tags - we'll handle styling through column display configuration
        item_id = self.tree.insert('', tk.END, values=values)

        # Store order data in a separate dictionary
        if not hasattr(self, 'order_data_map'):
            self.order_data_map = {}
        self.order_data_map[item_id] = order

        # Initialize toggle state
        self.item_toggle_state[item_id] = initial_state

    def on_tree_click(self, event):
        """Handle single click on tree - toggle checkbox in Include column"""
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        # Check if clicked on Include column (always #1, first visible column)
        if column == '#1' and item:  # Include column
            # Toggle the checkbox
            current_state = self.item_toggle_state.get(item, False)
            new_state = not current_state
            self.item_toggle_state[item] = new_state

            # Update the checkbox display
            current_values = list(self.tree.item(item, 'values'))
            current_values[0] = "☑" if new_state else "☐"
            self.tree.item(item, values=current_values)

    def toggle_all_checkboxes(self):
        """Toggle all checkboxes in the category"""
        if not hasattr(self, 'tree') or not hasattr(self, 'item_toggle_state'):
            return

        # Get the state from the "Select All" checkbox
        select_all = self.select_all_var.get()

        # Update all items
        for item_id in self.item_toggle_state.keys():
            self.item_toggle_state[item_id] = select_all

            # Update the visual checkbox
            current_values = list(self.tree.item(item_id, 'values'))
            current_values[0] = "☑" if select_all else "☐"
            self.tree.item(item_id, values=current_values)

    def on_tree_motion(self, event):
        """Handle mouse motion over tree items for cursor changes"""
        # No special cursor handling needed since we use right-click menu
        pass

    def on_tree_double_click(self, event):
        """Handle double-click on tree item - view PDF or CSV file"""
        if not self.tree.selection():
            return

        item = self.tree.selection()[0]

        # Get order data from our mapping
        if not hasattr(self, 'order_data_map') or item not in self.order_data_map:
            return

        order_data = self.order_data_map[item]

        if self.mode == 'csv':
            # CSV mode: Open CSV file
            csv_files = order_data.get('csv_files', [])
            if csv_files:
                csv_path = csv_files[0].get('current_path')
                if csv_path and Path(csv_path).exists():
                    self.open_file(csv_path)
                else:
                    messagebox.showwarning("File Not Found", f"CSV file not found:\n{csv_path}")
        else:
            # PDF mode: View PDF if available
            if order_data.get('pdf_path'):
                self.view_pdf(order_data['pdf_path'])

    def on_tree_right_click(self, event):
        """Handle right-click on tree item to show context menu"""
        # Identify the item under the cursor
        item = self.tree.identify_row(event.y)

        if not item:
            return

        # Select the item
        self.tree.selection_set(item)

        # Get order data from our mapping
        if not hasattr(self, 'order_data_map') or item not in self.order_data_map:
            return

        order_data = self.order_data_map[item]

        # Create context menu
        context_menu = tk.Menu(self, tearoff=0)

        # Add menu items based on category
        if self.color != '#95a5a6':  # Not already in processed category
            context_menu.add_command(
                label="Mark Processed",
                command=lambda: self.mark_single_order_processed(order_data)
            )

        # Add common menu items
        if order_data.get('pdf_path'):
            context_menu.add_command(
                label="View PDF",
                command=lambda: self.view_pdf(order_data['pdf_path'])
            )

        context_menu.add_command(
            label="Attach/Replace PDF",
            command=lambda: self.browse_for_pdf(order_data, item)
        )

        # Show menu
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def mark_single_order_processed(self, order_data: Dict):
        """Mark a single order as processed"""
        order_number = order_data.get('csv_data', {}).get('OrderNumber', '')

        # Confirm action
        result = messagebox.askyesno(
            "Mark Processed",
            f"Mark order {order_number} as processed?\n\n"
            f"This will move the order to the 'Previously Processed' category."
        )

        if result:
            # Mark as processed via callback
            if hasattr(self, 'on_mark_processed'):
                self.on_mark_processed([order_data])
            else:
                # Update local data
                order_data['processed'] = True

                # Trigger refresh
                if self.on_refresh_needed:
                    self.on_refresh_needed()

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

    def open_file(self, file_path: str):
        """Open file in default application"""
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', file_path))
            elif platform.system() == 'Windows':  # Windows
                os.startfile(file_path)
            else:  # linux variants
                subprocess.call(('xdg-open', file_path))
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{str(e)}")

    def browse_for_pdf(self, order_data: Dict, tree_item):
        """Browse for PDF file to attach/replace"""
        order_number = order_data.get('csv_data', {}).get('OrderNumber', '')

        file_path = filedialog.askopenfilename(
            title=f"Select PDF for Order {order_number}",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if file_path:
            # Update order data
            order_data['pdf_path'] = file_path
            order_data['has_pdf'] = True

            # Notify parent about PDF attachment
            if self.on_pdf_attach:
                success = self.on_pdf_attach(order_data, file_path)

                if success:
                    messagebox.showinfo("Success", f"PDF attached to order {order_number}")

                    # Trigger refresh of the expanded view
                    if self.on_refresh_needed:
                        self.on_refresh_needed()
                else:
                    messagebox.showerror("Error", "Failed to attach PDF")

    def _get_csv_status(self, order_number: str) -> str:
        """Get CSV status from database for display"""
        if not order_number:
            return "❌ No CSV"

        try:
            # Get database manager (passed from parent)
            if not hasattr(self, 'csv_db'):
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

class BatchReviewWindow(tk.Toplevel):
    """Window to review and modify batch print jobs before execution"""
    def __init__(self, parent, batch_configs: Dict, execute_callback: Callable):
        super().__init__(parent)

        self.parent_window = parent
        self.batch_configs = batch_configs.copy()  # Copy so we can modify
        self.execute_callback = execute_callback

        self.setup_window()

    def setup_window(self):
        """Create the batch review window"""
        self.title("Batch Print Review")
        self.geometry("1000x700")
        self.configure(bg='#ecf0f1')
        self.transient(self.parent_window)
        self.grab_set()

        # Header
        header_frame = tk.Frame(self, bg='#34495e', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text=f"📋 Batch Print Review - {len(self.batch_configs)} Orders",
            font=("Segoe UI", 20, "bold"),
            bg='#34495e',
            fg='white'
        ).pack(expand=True)

        # Main content
        content_frame = tk.Frame(self, bg='#ecf0f1')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Instructions
        tk.Label(
            content_frame,
            text="Review batch jobs below. Delete any incorrect jobs, then click Print All to execute.",
            font=("Segoe UI", 11),
            bg='#ecf0f1',
            fg='#7f8c8d'
        ).pack(pady=(0, 15))

        # Job list frame
        list_frame = tk.Frame(content_frame, bg='#ecf0f1')
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Create treeview
        columns = ('Order', 'Customer', 'Printers', 'Delete')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=18)

        # Configure columns
        self.tree.heading('Order', text='Order #')
        self.tree.heading('Customer', text='Customer')
        self.tree.heading('Printers', text='Printers & Settings')
        self.tree.heading('Delete', text='Actions')

        self.tree.column('Order', width=120)
        self.tree.column('Customer', width=250)
        self.tree.column('Printers', width=450)
        self.tree.column('Delete', width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Populate tree
        self.populate_tree()

        # Bind double-click to delete
        self.tree.bind('<Double-1>', self.on_tree_double_click)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Summary frame
        summary_frame = tk.Frame(content_frame, bg='#ecf0f1')
        summary_frame.pack(fill=tk.X, pady=(15, 0))

        self.summary_label = tk.Label(
            summary_frame,
            text="",
            font=("Segoe UI", 11, "bold"),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        self.summary_label.pack()
        self.update_summary()

        # Buttons frame
        button_frame = tk.Frame(self, bg='#ecf0f1')
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        tk.Button(
            button_frame,
            text="Cancel",
            command=self.destroy,
            font=("Segoe UI", 12),
            bg='#95a5a6',
            fg='white',
            border=0,
            padx=25,
            pady=10
        ).pack(side=tk.RIGHT)

        tk.Button(
            button_frame,
            text="🖨️ Print All",
            command=self.execute_print,
            font=("Segoe UI", 13, "bold"),
            bg='#27ae60',
            fg='white',
            border=0,
            padx=30,
            pady=12
        ).pack(side=tk.RIGHT, padx=(0, 10))

    def populate_tree(self):
        """Populate the tree with batch jobs"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add each job
        for order_number, config in self.batch_configs.items():
            order_data = config.get('order_data', {})
            csv_data = order_data.get('csv_data', {})

            # Build printer description
            printers_desc = []
            for printer_config in config.get('printers', []):
                if printer_config['type'] == '11x17':
                    printers_desc.append(f"📄 11x17 ({printer_config['copies']}× {printer_config['color_mode']})")
                elif printer_config['type'] == '24x36':
                    printers_desc.append(f"🖨️ 24x36 ({printer_config['copies']}× {printer_config['color_mode']})")
                elif printer_config['type'] == 'folder':
                    printers_desc.append("📁 Folder Label")

            printers_text = " | ".join(printers_desc) if printers_desc else "No printers"

            self.tree.insert('', tk.END, values=(
                csv_data.get('OrderNumber', ''),
                csv_data.get('Customer', ''),
                printers_text,
                "🗑️ Delete"
            ), tags=(order_number,))

    def on_tree_double_click(self, event):
        """Handle double-click to delete job"""
        column = self.tree.identify_column(event.x)

        # Only delete if clicking on Delete column
        if column == '#4':
            selection = self.tree.selection()
            if selection:
                item = selection[0]
                tags = self.tree.item(item, 'tags')
                if tags:
                    order_number = tags[0]
                    self.delete_job(order_number)

    def delete_job(self, order_number: str):
        """Delete a job from the batch"""
        if order_number in self.batch_configs:
            result = messagebox.askyesno(
                "Delete Job",
                f"Remove order {order_number} from batch?"
            )

            if result:
                del self.batch_configs[order_number]
                self.populate_tree()
                self.update_summary()

                if not self.batch_configs:
                    messagebox.showinfo("Batch Empty", "All jobs removed from batch.")
                    self.destroy()

    def update_summary(self):
        """Update the summary statistics"""
        total_jobs = len(self.batch_configs)

        # Count total print operations
        total_prints = 0
        for config in self.batch_configs.values():
            for printer in config.get('printers', []):
                if printer['type'] in ['11x17', '24x36']:
                    total_prints += printer.get('copies', 1)
                elif printer['type'] == 'folder':
                    total_prints += 1

        summary_text = f"Total: {total_jobs} orders | Approx. {total_prints} print operations"
        self.summary_label.config(text=summary_text)

    def execute_print(self):
        """Execute the batch print"""
        if not self.batch_configs:
            messagebox.showwarning("No Jobs", "No jobs in batch to print.")
            return

        # Close this window and execute
        self.destroy()

        # Call the execute callback with the modified batch configs
        self.execute_callback(self.batch_configs)

class EnhancedExpandedView(tk.Toplevel):
    def __init__(self, parent, date: datetime, orders_data: List[Dict], pdf_processor, relationship_manager, archive_manager=None, template_path=None, settings_manager=None, title=None, show_date_column=False, mode='pdf'):
        super().__init__(parent)

        self.date = date
        self.orders_data = orders_data
        self.pdf_processor = pdf_processor
        self.relationship_manager = relationship_manager
        self.archive_manager = archive_manager
        self.mode = mode  # 'pdf' or 'csv' mode

        # Initialize CSV database manager
        if settings_manager:
            db_path = settings_manager.get("db_path")
            self.csv_db = EnhancedDatabaseManager(db_path)
        else:
            self.csv_db = None

        # Use provided template path or calculate relative path
        if template_path:
            self.template_path = template_path
        else:
            # Calculate relative template path (portable)
            import os
            script_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(script_dir)
            self.template_path = os.path.join(root_dir, "LABEL TEMPLATE", "Contract_Lumber_Label_Template.docx")

        self.settings_manager = settings_manager
        self.custom_title = title  # Store custom title if provided
        self.show_date_column = show_date_column  # Whether to show date column (for week view)

        # Initialize preset manager
        self.preset_manager = PrintPresetManager()

        # Callbacks
        self.on_statistics_refresh = None

        self.setup_dialog()

    def setup_dialog(self):
        """Create the enhanced expanded view dialog"""
        # Use custom title if provided, otherwise use default date format
        window_title = self.custom_title if self.custom_title else f"Orders for {self.date.strftime('%A, %B %d, %Y')}"
        header_title = self.custom_title if self.custom_title else self.date.strftime('%A, %B %d, %Y')

        self.title(window_title)
        self.geometry("1600x900")
        self.configure(bg='#ecf0f1')
        self.transient(self.master)
        self.grab_set()

        # Debug: Log the number of orders received
        print(f"DEBUG: Enhanced Expanded View created with {len(self.orders_data)} orders for {self.date}")
        for i, order in enumerate(self.orders_data):
            print(f"DEBUG: Order {i}: {order.get('csv_data', {}).get('OrderNumber', 'No Order Number')}")

        # Header frame
        header_frame = tk.Frame(self, bg='#34495e', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Date and statistics
        date_label = tk.Label(
            header_frame,
            text=header_title,
            font=("Segoe UI", 20, "bold"),
            bg='#34495e',
            fg='white'
        )
        date_label.pack(pady=15)

        # Summary statistics
        self.summary_label = tk.Label(
            header_frame,
            text="",
            font=("Segoe UI", 11),
            bg='#34495e',
            fg='#bdc3c7'
        )
        self.summary_label.pack()

        # Main container for content and sidebar
        main_container = tk.Frame(self, bg='#ecf0f1')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Main content area with categories
        self.content_frame = tk.Frame(main_container, bg='#ecf0f1')
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Sidebar for print configuration
        self.sidebar_frame = tk.Frame(main_container, bg='#34495e', width=320)
        self.sidebar_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))
        self.sidebar_frame.pack_propagate(False)

        # Create sidebar content
        self.create_print_sidebar()

        # Create category sections
        self.create_category_sections()

        # Close button
        close_btn = tk.Button(
            self,
            text="Close",
            command=self.destroy,
            font=("Segoe UI", 12),
            bg='#95a5a6',
            fg='white',
            border=0,
            padx=25,
            pady=8
        )
        close_btn.pack(pady=(0, 20))

    def create_category_sections(self):
        """Create the three category sections"""
        # Initialize category sections storage
        self.category_sections = {}

        # Categorize orders based on mode
        if self.mode == 'csv':
            # CSV mode: categorize by CSV validation status
            green_orders = [order for order in self.orders_data if order.get('csv_validation_status') == 'valid']
            red_orders = [order for order in self.orders_data if order.get('csv_validation_status') in ['has_errors', 'has_warnings']]
            gray_orders = [order for order in self.orders_data if order.get('csv_validation_status') == 'not_validated']

            # Update summary for CSV mode
            total = len(self.orders_data)
            summary_text = f"Total: {total} | Ready: {len(green_orders)} | Errors: {len(red_orders)} | Needs Validation: {len(gray_orders)}"
            self.summary_label.config(text=summary_text)

            # Category titles for CSV mode
            green_title = "✓ Ready to Process"
            red_title = "❌ Has Errors"
            gray_title = "⚪ Needs Validation"
        else:
            # PDF mode: categorize by PDF status
            green_orders = [order for order in self.orders_data if order.get('has_pdf', False) and not order.get('processed', False)]
            red_orders = [order for order in self.orders_data if not order.get('has_pdf', False) and not order.get('processed', False)]
            gray_orders = [order for order in self.orders_data if order.get('processed', False)]

            # Update summary for PDF mode
            total = len(self.orders_data)
            summary_text = f"Total: {total} | Ready: {len(green_orders)} | Missing PDFs: {len(red_orders)} | Processed: {len(gray_orders)}"
            self.summary_label.config(text=summary_text)

            # Category titles for PDF mode
            green_title = "✅ Ready to Print"
            red_title = "❌ Missing PDFs"
            gray_title = "📋 Previously Processed"

        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Create category sections
        if green_orders:
            green_section = CategorySection(
                self.content_frame,
                green_title,
                "#27ae60",
                green_orders,
                show_date_column=self.show_date_column,
                csv_db=self.csv_db,
                mode=self.mode
            )
            green_section.on_pdf_attach = self.handle_pdf_attachment
            green_section.on_refresh_needed = self.refresh_view
            green_section.on_mark_processed = self.mark_orders_processed
            green_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            self.category_sections['green'] = green_section

        if red_orders:
            red_section = CategorySection(
                self.content_frame,
                red_title,
                "#e74c3c",
                red_orders,
                show_date_column=self.show_date_column,
                csv_db=self.csv_db,
                mode=self.mode
            )
            red_section.on_pdf_attach = self.handle_pdf_attachment
            red_section.on_refresh_needed = self.refresh_view
            red_section.on_mark_processed = self.mark_orders_processed
            red_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            self.category_sections['red'] = red_section

        if gray_orders:
            gray_section = CategorySection(
                self.content_frame,
                gray_title,
                "#95a5a6",
                gray_orders,
                show_date_column=self.show_date_column,
                csv_db=self.csv_db,
                mode=self.mode
            )
            gray_section.on_pdf_attach = self.handle_pdf_attachment
            gray_section.on_refresh_needed = self.refresh_view
            gray_section.pack(fill=tk.BOTH, expand=True)
            self.category_sections['gray'] = gray_section

        # If no orders
        if not self.orders_data:
            empty_label = tk.Label(
                self.content_frame,
                text=f"No orders scheduled for this date\n\nDebug info:\n• Total orders received: {len(self.orders_data)}\n• Date: {self.date.strftime('%Y-%m-%d')}",
                font=("Segoe UI", 13),
                bg='#ecf0f1',
                fg='#7f8c8d',
                justify=tk.LEFT
            )
            empty_label.pack(expand=True, pady=50)

    def handle_pdf_attachment(self, order_data: Dict, pdf_path: str) -> bool:
        """Handle PDF attachment to an order"""
        try:
            order_number = order_data.get('csv_data', {}).get('OrderNumber', '')
            relationship = self.relationship_manager.get_relationship_by_order(order_number)

            if relationship:
                success = self.relationship_manager.update_relationship_pdf(
                    relationship['relationship_id'],
                    pdf_path,
                    "manual_attachment"
                )

                if success:
                    # Update local data
                    for order in self.orders_data:
                        if order.get('csv_data', {}).get('OrderNumber') == order_number:
                            order['pdf_path'] = pdf_path
                            order['has_pdf'] = True
                            break

                    logging.info(f"PDF manually attached to order {order_number}")
                    return True

            return False

        except Exception as e:
            logging.error(f"Failed to handle PDF attachment: {e}")
            return False

    def mark_orders_processed(self, orders: List[Dict]):
        """Mark orders as processed after printing and archive PDFs"""
        try:
            archived_count = 0
            failed_count = 0

            for order in orders:
                # Update local data
                order['processed'] = True

                # Update in database/relationship manager
                order_number = order.get('csv_data', {}).get('OrderNumber', '')
                pdf_path = order.get('pdf_path')

                # Mark as processed in the database
                success = self.relationship_manager.mark_order_processed(order_number)

                if success:
                    logging.info(f"Order {order_number} marked as processed after printing")

                    # Archive the PDF if available and archive manager is configured
                    if pdf_path and self.archive_manager:
                        try:
                            csv_data = order.get('csv_data', {})
                            archive_path = self.archive_manager.archive_pdf(
                                pdf_path,
                                order_number,
                                csv_data
                            )

                            # Update the PDF path in the relationship to point to archive
                            self.relationship_manager.update_relationship_pdf(
                                order.get('relationship_id'),
                                archive_path,
                                "archived_after_processing"
                            )

                            # Remove original PDF from source folder
                            self.archive_manager.remove_processed_pdf(pdf_path)

                            # Update local order data
                            order['pdf_path'] = archive_path

                            archived_count += 1
                            logging.info(f"Archived PDF for order {order_number}: {pdf_path} -> {archive_path}")

                        except Exception as archive_error:
                            failed_count += 1
                            logging.error(f"Failed to archive PDF for order {order_number}: {archive_error}")
                    elif not self.archive_manager:
                        logging.warning("Archive manager not configured - PDF not archived")

                else:
                    failed_count += 1
                    logging.warning(f"Failed to mark order {order_number} as processed in database")

            # Show archive summary if archiving was performed
            if archived_count > 0 or failed_count > 0:
                summary_msg = f"Archiving complete:\n✓ {archived_count} PDFs archived"
                if failed_count > 0:
                    summary_msg += f"\n✗ {failed_count} failed"
                logging.info(summary_msg)

        except Exception as e:
            logging.error(f"Failed to mark orders as processed: {e}")

    def refresh_view(self):
        """Refresh the expanded view"""
        self.create_category_sections()

        # Notify parent to refresh statistics
        if self.on_statistics_refresh:
            self.on_statistics_refresh()

    def set_statistics_refresh_callback(self, callback):
        """Set callback for refreshing parent statistics"""
        self.on_statistics_refresh = callback

    def create_print_sidebar(self):
        """Create the sidebar (print or CSV processing based on mode)"""
        if self.mode == 'csv':
            # CSV Processing Sidebar
            sidebar_header = tk.Label(
                self.sidebar_frame,
                text="📦 CSV Processing",
                font=("Segoe UI", 15, "bold"),
                bg='#34495e',
                fg='white'
            )
            sidebar_header.pack(pady=(20, 10), padx=10)

            # Instructions
            instructions = tk.Label(
                self.sidebar_frame,
                text="Select CSVs below\nthen validate or upload\nto BisTrack",
                font=("Segoe UI", 10),
                bg='#34495e',
                fg='#bdc3c7',
                justify=tk.CENTER
            )
            instructions.pack(pady=(0, 10), padx=10)

            # Select All button
            select_all_btn = tk.Button(
                self.sidebar_frame,
                text="☑ Select All",
                command=self.select_all_csvs,
                font=("Segoe UI", 10),
                bg='#3498db',
                fg='white',
                border=0,
                padx=15,
                pady=8,
                cursor='hand2'
            )
            select_all_btn.pack(pady=(0, 10), padx=10, fill=tk.X)

            # Info panel
            info_frame = tk.Frame(self.sidebar_frame, bg='#2c3e50', relief='solid', borderwidth=1)
            info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 15))

            info_text = tk.Label(
                info_frame,
                text="Validation checks:\n• SKU validity\n• Data quality\n• Required fields\n\n" +
                     "Upload sends validated\nCSVs to BisTrack\nimport folder.",
                font=("Segoe UI", 10),
                bg='#2c3e50',
                fg='#bdc3c7',
                justify=tk.CENTER
            )
            info_text.pack(expand=True, pady=30)
        else:
            # PDF Print Sidebar (original)
            sidebar_header = tk.Label(
                self.sidebar_frame,
                text="📄 Batch Print",
                font=("Segoe UI", 15, "bold"),
                bg='#34495e',
                fg='white'
            )
            sidebar_header.pack(pady=(20, 10), padx=10)

            # Instructions
            instructions = tk.Label(
                self.sidebar_frame,
                text="Check orders below\nthen click Create Batch\nto choose print settings",
                font=("Segoe UI", 10),
                bg='#34495e',
                fg='#bdc3c7',
                justify=tk.CENTER
            )
            instructions.pack(pady=(0, 20), padx=10)

            # Manage Presets button
            manage_presets_btn = tk.Button(
                self.sidebar_frame,
                text="⚙️ Manage Presets",
                command=self.open_preset_manager,
                font=("Segoe UI", 11),
                bg='#f39c12',
                fg='white',
                border=0,
                padx=20,
                pady=10,
                cursor='hand2'
            )
            manage_presets_btn.pack(pady=(0, 10), padx=10, fill=tk.X)

            # Info panel
            info_frame = tk.Frame(self.sidebar_frame, bg='#2c3e50', relief='solid', borderwidth=1)
            info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 15))

            info_text = tk.Label(
                info_frame,
                text="Presets allow you to save\nprinter configurations for\nquick batch printing.\n\n" +
                     "Select orders below,\nthen create a batch to\nchoose your preset.",
                font=("Segoe UI", 10),
                bg='#2c3e50',
                fg='#bdc3c7',
                justify=tk.CENTER
            )
            info_text.pack(expand=True, pady=30)

        # Action buttons (fixed at bottom)
        actions_frame = tk.Frame(self.sidebar_frame, bg='#34495e')
        actions_frame.pack(fill=tk.X, padx=10, pady=(10, 10), side=tk.BOTTOM)

        if self.mode == 'csv':
            # CSV Processing Buttons
            # Validate button
            validate_btn = tk.Button(
                actions_frame,
                text="🔍 Validate Selected",
                command=self.validate_selected_csvs,
                font=("Segoe UI", 12, "bold"),
                bg='#3498db',
                fg='white',
                border=0,
                padx=15,
                pady=12,
                cursor='hand2'
            )
            validate_btn.pack(fill=tk.X, pady=(0, 10))

            # Upload button
            upload_btn = tk.Button(
                actions_frame,
                text="📤 Upload to BisTrack",
                command=self.upload_selected_csvs,
                font=("Segoe UI", 12, "bold"),
                bg='#27ae60',
                fg='white',
                border=0,
                padx=15,
                pady=12,
                cursor='hand2'
            )
            upload_btn.pack(fill=tk.X)
        else:
            # PDF Print Button (original)
            create_batch_btn = tk.Button(
                actions_frame,
                text="📋 Create Batch",
                command=self.create_batch_with_presets,
                font=("Segoe UI", 13, "bold"),
                bg='#27ae60',
                fg='white',
                border=0,
                padx=15,
                pady=15,
                cursor='hand2'
            )
            create_batch_btn.pack(fill=tk.X)

    def get_available_printers(self):
        """Get list of available printers on the system"""
        try:
            import win32print
            printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
            return printers if printers else ["Default Printer"]
        except:
            return ["Default Printer"]

    def open_preset_manager(self):
        """Open the preset manager dialog"""
        PresetManagerDialog(self, self.preset_manager)

    def create_batch_with_presets(self):
        """Create batch using preset system"""
        # Collect checked orders from all categories
        selected_orders = []

        for category_name, category_section in self.category_sections.items():
            if not hasattr(category_section, 'tree') or not hasattr(category_section, 'item_toggle_state'):
                continue

            # Iterate through items in this category
            for item_id, is_checked in category_section.item_toggle_state.items():
                if is_checked:  # Only include checked items
                    order_data = category_section.order_data_map.get(item_id)
                    if order_data:
                        selected_orders.append(order_data)

        if not selected_orders:
            messagebox.showwarning("No Items Selected", "Please check at least one order to include in the batch.")
            return

        # Show preset selection dialog
        preset_dialog = PresetSelectionDialog(self, self.preset_manager, len(selected_orders))
        self.wait_window(preset_dialog)

        if not preset_dialog.selected_preset:
            # User cancelled
            return

        # Execute batch print with selected preset
        success = execute_batch_print_with_preset(
            selected_orders,
            preset_dialog.selected_preset,
            self.template_path,
            self,
            self.mark_orders_processed
        )

        if success:
            # Refresh the view
            self.refresh_view()

    def validate_selected_csvs(self):
        """Validate selected CSV files"""
        import tkinter.messagebox as messagebox
        from csv_batch_processor import CSVBatchProcessor

        # Get selected orders
        selected_orders = self.get_selected_orders()

        if not selected_orders:
            messagebox.showwarning("No Selection", "Please select CSVs to validate")
            return

        # Get CSV files from selected orders
        csv_paths = []
        for order in selected_orders:
            csv_files = order.get('csv_files', [])
            for csv_file in csv_files:
                csv_path = csv_file.get('current_path')
                if csv_path:
                    csv_paths.append(csv_path)

        if not csv_paths:
            messagebox.showwarning("No CSVs", "Selected orders have no CSV files")
            return

        # Initialize batch processor
        products_file = self.settings_manager.get("products_file_path") if self.settings_manager else None
        db_path = self.settings_manager.get("db_path") if self.settings_manager else None

        processor = CSVBatchProcessor(
            products_file_path=products_file,
            db_path=db_path
        )

        # Validate CSVs
        logging.info(f"Validating {len(csv_paths)} CSV files")
        results = processor.validate_batch(csv_paths)

        # Show results
        summary = processor.get_validation_summary(results)
        messagebox.showinfo("Validation Complete", summary)

        # Refresh view to show updated validation status
        self.refresh_view()

    def upload_selected_csvs(self):
        """Upload selected CSV files to BisTrack import folder"""
        import tkinter.messagebox as messagebox
        from csv_batch_processor import CSVBatchProcessor

        # Get selected orders
        selected_orders = self.get_selected_orders()

        if not selected_orders:
            messagebox.showwarning("No Selection", "Please select CSVs to upload")
            return

        # Get CSV files from selected orders (only valid ones)
        csv_paths = []
        for order in selected_orders:
            csv_files = order.get('csv_files', [])
            for csv_file in csv_files:
                # Only upload validated CSVs
                validation_status = csv_file.get('validation_status', 'not_validated')
                if validation_status == 'valid':
                    csv_path = csv_file.get('current_path')
                    if csv_path:
                        csv_paths.append(csv_path)

        if not csv_paths:
            messagebox.showwarning(
                "No Valid CSVs",
                "No validated CSVs found in selection.\n\n"
                "Please validate CSVs before uploading."
            )
            return

        # Confirm upload
        confirm = messagebox.askyesno(
            "Confirm Upload",
            f"Upload {len(csv_paths)} validated CSV(s) to BisTrack?\n\n"
            "This will copy the files to the BisTrack import folder."
        )

        if not confirm:
            return

        # Initialize batch processor
        products_file = self.settings_manager.get("products_file_path") if self.settings_manager else None
        bistrack_folder = self.settings_manager.get("bistrack_import_folder") if self.settings_manager else None
        db_path = self.settings_manager.get("db_path") if self.settings_manager else None

        if not bistrack_folder:
            messagebox.showerror(
                "Configuration Error",
                "BisTrack import folder not configured.\n\n"
                "Please configure in Settings > File Locations"
            )
            return

        processor = CSVBatchProcessor(
            products_file_path=products_file,
            bistrack_import_folder=bistrack_folder,
            db_path=db_path
        )

        # Upload CSVs (without re-validation since already validated)
        logging.info(f"Uploading {len(csv_paths)} CSV files to BisTrack")
        results = processor.upload_batch(csv_paths, validate_first=False)

        # Show results
        summary = processor.get_upload_summary(results)
        messagebox.showinfo("Upload Complete", summary)

        # Refresh view to show updated status
        self.refresh_view()

    def select_all_csvs(self):
        """Select all CSVs in all category sections"""
        if not hasattr(self, 'category_sections'):
            return

        # Toggle between select all and deselect all
        all_selected = True

        # Check if all are currently selected
        for section_name, section in self.category_sections.items():
            if hasattr(section, 'item_toggle_state'):
                for item_id, state in section.item_toggle_state.items():
                    if not state:
                        all_selected = False
                        break
            if not all_selected:
                break

        # Toggle all items
        target_state = not all_selected

        for section_name, section in self.category_sections.items():
            if hasattr(section, 'item_toggle_state') and hasattr(section, 'tree'):
                for item_id in section.item_toggle_state.keys():
                    section.item_toggle_state[item_id] = target_state
                    # Update tree display
                    current_values = list(section.tree.item(item_id, 'values'))
                    current_values[0] = "☑" if target_state else "☐"
                    section.tree.item(item_id, values=current_values)

        logging.info(f"{'Selected' if target_state else 'Deselected'} all CSV items")