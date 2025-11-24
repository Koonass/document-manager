#!/usr/bin/env python3
"""
Statistics Calendar Widget - Simplified 10-box calendar with daily statistics
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from enhanced_expanded_view import EnhancedExpandedView

class DayStatisticsBox(tk.Frame):
    def __init__(self, parent, date: datetime, on_click=None, is_today=False, **kwargs):
        super().__init__(parent, **kwargs)

        self.date = date
        self.on_click = on_click
        self.is_today = is_today

        # Statistics data
        self.successful_matches = 0
        self.no_matches = 0
        self.previously_processed = 0

        self.setup_box()

    def setup_box(self):
        """Create the day statistics box with minimalist styling"""
        # Determine background color - subtle red for today
        if self.is_today:
            bg_color = '#ffe5e5'  # Subtle light red
            border_color = '#ff9999'  # Slightly darker red for border
        else:
            bg_color = '#ffffff'
            border_color = '#d0d0d0'

        # Configure the frame styling
        self.configure(
            relief='solid',
            borderwidth=2 if self.is_today else 1,
            bg=bg_color,
            highlightbackground=border_color,
            cursor='hand2'
        )

        # Make the entire box clickable
        self.bind("<Button-1>", self.on_box_click)

        # Hover effects
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

        # Day number at top
        day_num = self.date.day
        bg_color = '#ffe5e5' if self.is_today else '#ffffff'
        self.day_label = tk.Label(
            self,
            text=str(day_num),
            font=("Segoe UI", 24, "bold"),
            bg=bg_color,
            fg='#c0392b' if self.is_today else '#2c3e50',  # Darker red text for today
            cursor='hand2'
        )
        self.day_label.pack(pady=(15, 5))
        self.day_label.bind("<Button-1>", self.on_box_click)

        # Statistics container
        stats_frame = tk.Frame(self, bg=bg_color)
        stats_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=(0, 10))

        # Header row with PDF and CSV labels
        header_frame = tk.Frame(stats_frame, bg=bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 2))

        tk.Label(header_frame, text="", width=3, bg=bg_color).pack(side=tk.LEFT)  # Space for icon
        tk.Label(
            header_frame, text="PDF", font=("Segoe UI", 10, "bold"),
            bg=bg_color, fg='#7f8c8d', width=4
        ).pack(side=tk.LEFT, padx=(5, 5))
        tk.Label(
            header_frame, text="CSV", font=("Segoe UI", 11, "bold"),
            bg=bg_color, fg='#7f8c8d', width=5
        ).pack(side=tk.LEFT, padx=(2, 0))

        # Successful matches row
        self.success_frame = self.create_dual_stat_row(
            stats_frame, "✅", "#27ae60"
        )

        # No matches row
        self.no_match_frame = self.create_dual_stat_row(
            stats_frame, "❌", "#e74c3c"
        )

        # Previously processed row
        self.processed_frame = self.create_dual_stat_row(
            stats_frame, "📋", "#95a5a6"
        )

    def create_dual_stat_row(self, parent, icon: str, color: str):
        """Create a statistics row with icon, PDF count, and CSV count"""
        bg_color = '#ffe5e5' if self.is_today else '#ffffff'
        row_frame = tk.Frame(parent, bg=bg_color)
        row_frame.pack(fill=tk.X, pady=1)

        # Icon
        icon_label = tk.Label(
            row_frame,
            text=f"{icon}",
            font=("Segoe UI", 14),
            bg=bg_color,
            fg=color,
            cursor='hand2',
            width=3
        )
        icon_label.pack(side=tk.LEFT)
        icon_label.bind("<Button-1>", self.on_box_click)

        # PDF count
        pdf_label = tk.Label(
            row_frame,
            text="0",
            font=("Segoe UI", 14, "bold"),
            bg=bg_color,
            fg=color,
            cursor='hand2',
            width=3
        )
        pdf_label.pack(side=tk.LEFT, padx=(5, 5))
        pdf_label.bind("<Button-1>", self.on_box_click)

        # CSV count
        csv_label = tk.Label(
            row_frame,
            text="0",
            font=("Segoe UI", 16, "bold"),
            bg=bg_color,
            fg=color,
            cursor='hand2',
            width=4,
            anchor='center'
        )
        csv_label.pack(side=tk.LEFT, padx=(5, 0))
        csv_label.bind("<Button-1>", self.on_box_click)

        return {'frame': row_frame, 'pdf_label': pdf_label, 'csv_label': csv_label}

    def create_stat_row(self, parent, icon: str, label: str, color: str, row: int):
        """Create a statistics row with icon, label, and number (legacy method)"""
        bg_color = '#ffe5e5' if self.is_today else '#ffffff'
        row_frame = tk.Frame(parent, bg=bg_color)
        row_frame.pack(fill=tk.X, pady=2)

        # Icon and label
        icon_label = tk.Label(
            row_frame,
            text=f"{icon}",
            font=("Segoe UI", 16),
            bg=bg_color,
            fg=color,
            cursor='hand2'
        )
        icon_label.pack(side=tk.LEFT)
        icon_label.bind("<Button-1>", self.on_box_click)

        # Number
        number_label = tk.Label(
            row_frame,
            text="0",
            font=("Segoe UI", 16, "bold"),
            bg=bg_color,
            fg=color,
            cursor='hand2'
        )
        number_label.pack(side=tk.RIGHT)
        number_label.bind("<Button-1>", self.on_box_click)

        return {'frame': row_frame, 'number_label': number_label}

    def update_statistics(self, successful: int, no_matches: int, processed: int,
                         successful_csv: int = 0, no_matches_csv: int = 0, processed_csv: int = 0):
        """Update the statistics display with PDF and CSV counts"""
        self.successful_matches = successful
        self.no_matches = no_matches
        self.previously_processed = processed

        # Update PDF counts
        self.success_frame['pdf_label'].config(text=str(successful))
        self.no_match_frame['pdf_label'].config(text=str(no_matches))
        self.processed_frame['pdf_label'].config(text=str(processed))

        # Update CSV counts
        self.success_frame['csv_label'].config(text=str(successful_csv))
        self.no_match_frame['csv_label'].config(text=str(no_matches_csv))
        self.processed_frame['csv_label'].config(text=str(processed_csv))

    def on_box_click(self, event=None):
        """Handle box click"""
        if self.on_click:
            self.on_click(self.date, self)

    def on_enter(self, event=None):
        """Handle mouse enter (hover effect)"""
        hover_color = '#ffd4d4' if self.is_today else '#f8f9fa'
        self.configure(bg=hover_color, relief='solid', borderwidth=2)
        # Update all child widgets
        for widget in self.winfo_children():
            if hasattr(widget, 'configure'):
                try:
                    widget.configure(bg=hover_color)
                except:
                    pass
            self.update_child_backgrounds(widget, hover_color)

    def on_leave(self, event=None):
        """Handle mouse leave"""
        normal_color = '#ffe5e5' if self.is_today else '#ffffff'
        border_width = 2 if self.is_today else 1
        self.configure(bg=normal_color, relief='solid', borderwidth=border_width)
        # Update all child widgets
        for widget in self.winfo_children():
            if hasattr(widget, 'configure'):
                try:
                    widget.configure(bg=normal_color)
                except:
                    pass
            self.update_child_backgrounds(widget, normal_color)

    def update_child_backgrounds(self, widget, bg_color):
        """Recursively update background colors of child widgets"""
        try:
            for child in widget.winfo_children():
                if hasattr(child, 'configure'):
                    try:
                        child.configure(bg=bg_color)
                    except:
                        pass
                self.update_child_backgrounds(child, bg_color)
        except:
            pass

class DayDetailDialog(tk.Toplevel):
    def __init__(self, parent, date: datetime, orders_data: List[Dict]):
        super().__init__(parent)

        self.date = date
        self.orders_data = orders_data

        self.setup_dialog()

    def setup_dialog(self):
        """Create the detailed day view dialog"""
        self.title(f"Orders for {self.date.strftime('%A, %B %d, %Y')}")
        self.geometry("900x600")
        self.transient(self.master)
        self.grab_set()

        # Header frame
        header_frame = tk.Frame(self, bg='#34495e', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Date display
        date_label = tk.Label(
            header_frame,
            text=self.date.strftime('%A, %B %d, %Y'),
            font=("Segoe UI", 16, "bold"),
            bg='#34495e',
            fg='white'
        )
        date_label.pack(expand=True)

        # Orders list frame
        list_frame = tk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        if not self.orders_data:
            # No orders message
            no_orders_label = tk.Label(
                list_frame,
                text="No orders scheduled for this date",
                font=("Segoe UI", 12),
                fg='#7f8c8d'
            )
            no_orders_label.pack(expand=True)
        else:
            # Create orders list
            self.create_orders_list(list_frame)

        # Close button
        close_btn = ttk.Button(self, text="Close", command=self.destroy)
        close_btn.pack(pady=10)

    def create_orders_list(self, parent):
        """Create the orders list with action buttons"""
        # Create treeview for orders
        columns = ('Order', 'Customer', 'Job Ref', 'Designer', 'PDF Status', 'Actions')

        tree_frame = tk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        # Configure columns
        column_widths = {'Order': 100, 'Customer': 200, 'Job Ref': 150, 'Designer': 120, 'PDF Status': 100, 'Actions': 120}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Populate orders
        for order in self.orders_data:
            csv_data = order.get('csv_data', {})

            # Show PDF status with attachment method indicator
            if order.get('has_pdf') or order.get('pdf_path'):
                attachment_method = order.get('attachment_method')
                if attachment_method == 'manual':
                    pdf_status = "✅ 📎 Manual"
                elif attachment_method == 'automatic':
                    pdf_status = "✅ Auto"
                else:
                    pdf_status = "✅ Has PDF"
            else:
                pdf_status = "❌ No PDF"

            item_id = self.tree.insert('', tk.END, values=(
                csv_data.get('OrderNumber', ''),
                csv_data.get('Customer', ''),
                csv_data.get('JobReference', ''),
                csv_data.get('Designer', ''),
                pdf_status,
                "Actions..."
            ))

            # Store order data with tree item
            self.tree.set(item_id, 'order_data', order)

        # Bind double-click to show actions
        self.tree.bind('<Double-1>', self.on_order_double_click)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def on_order_double_click(self, event):
        """Handle double-click on order to show actions"""
        item = self.tree.selection()[0]
        order_data = self.tree.set(item, 'order_data')

        # Here you would open the PDF action menu
        # This would integrate with the existing PDF action functionality
        print(f"Double-clicked order: {order_data}")  # Placeholder

class StatisticsCalendarWidget(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.current_start_date = self.get_week_start(datetime.now())
        self.day_boxes = {}
        self.orders_by_date = {}

        # Statistics calculation callback
        self.calculate_statistics_callback = None

        self.setup_ui()

    def get_week_start(self, date: datetime) -> datetime:
        """Get the Monday of the week containing the given date"""
        days_since_monday = date.weekday()
        return date - timedelta(days=days_since_monday)

    def setup_ui(self):
        """Create the simplified calendar interface"""
        # Configure main frame
        self.configure(bg='#ecf0f1')

        # Navigation header
        nav_frame = tk.Frame(self, bg='#ecf0f1', height=60)
        nav_frame.pack(fill=tk.X, pady=(0, 20))
        nav_frame.pack_propagate(False)

        # Navigation buttons with better styling
        nav_left_frame = tk.Frame(nav_frame, bg='#ecf0f1')
        nav_left_frame.pack(side=tk.LEFT, padx=(20, 0), pady=15)

        prev_btn = tk.Button(
            nav_left_frame,
            text="◀ Previous",
            command=self.prev_2weeks,
            font=("Segoe UI", 11),
            bg='#3498db',
            fg='white',
            border=0,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        prev_btn.pack(side=tk.LEFT)

        # Go to Today button
        today_btn = tk.Button(
            nav_left_frame,
            text="📅 Today",
            command=self.go_to_today,
            font=("Segoe UI", 11),
            bg='#e67e22',
            fg='white',
            border=0,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        today_btn.pack(side=tk.LEFT, padx=(10, 0))

        # Next button (moved to left frame for better visibility)
        next_btn = tk.Button(
            nav_left_frame,
            text="Next ▶",
            command=self.next_2weeks,
            font=("Segoe UI", 11),
            bg='#3498db',
            fg='white',
            border=0,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        next_btn.pack(side=tk.LEFT, padx=(10, 0))

        # Add search button to the same frame as other navigation buttons
        search_btn = tk.Button(
            nav_left_frame,
            text="🔍 SEARCH",
            command=self.open_search_dialog,
            font=("Segoe UI", 11, "bold"),
            bg='#e67e22',
            fg='white',
            border=0,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        search_btn.pack(side=tk.LEFT, padx=(10, 0))

        self.date_label = tk.Label(
            nav_frame,
            text="",
            font=("Segoe UI", 16, "bold"),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        self.date_label.pack(expand=True, pady=15)

        # Calendar grid container
        self.calendar_container = tk.Frame(self, bg='#ecf0f1')
        self.calendar_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        self.create_calendar_grid()
        self.update_date_display()

    def create_calendar_grid(self):
        """Create the 10-box calendar grid"""
        # Clear existing widgets
        for widget in self.calendar_container.winfo_children():
            widget.destroy()
        self.day_boxes.clear()

        # Configure grid weights for equal sizing
        for i in range(5):  # 5 columns (Mon-Fri)
            self.calendar_container.columnconfigure(i, weight=1)
        for i in range(3):  # 3 rows (header + 2 weeks)
            self.calendar_container.rowconfigure(i, weight=1)

        # Weekday headers
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        for col, day_name in enumerate(weekdays):
            header = tk.Label(
                self.calendar_container,
                text=day_name,
                font=("Segoe UI", 12, "bold"),
                bg='#34495e',
                fg='white',
                relief='flat',
                height=2
            )
            header.grid(row=0, column=col, sticky='ew', padx=2, pady=2)

        # Create day boxes for 2 weeks
        today = datetime.now().date()
        for week in range(2):
            for day in range(5):  # Monday to Friday
                current_date = self.current_start_date + timedelta(days=(week * 7) + day)

                # Check if this is today's date
                is_today = current_date.date() == today

                day_box = DayStatisticsBox(
                    self.calendar_container,
                    current_date,
                    on_click=self.on_day_clicked,
                    is_today=is_today
                )
                day_box.grid(
                    row=week + 1,
                    column=day,
                    sticky='nsew',
                    padx=2,
                    pady=2
                )

                self.day_boxes[current_date.strftime('%Y-%m-%d')] = day_box

    def update_date_display(self):
        """Update the date range display"""
        end_date = self.current_start_date + timedelta(days=13)  # 2 weeks - 1 day
        date_text = f"{self.current_start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
        self.date_label.config(text=date_text)

    def prev_2weeks(self):
        """Navigate to previous 2 weeks"""
        self.current_start_date -= timedelta(days=14)
        self.create_calendar_grid()
        self.update_date_display()
        self.refresh_statistics()

    def next_2weeks(self):
        """Navigate to next 2 weeks"""
        self.current_start_date += timedelta(days=14)
        self.create_calendar_grid()
        self.update_date_display()
        self.refresh_statistics()

    def on_day_clicked(self, date: datetime, day_box: DayStatisticsBox):
        """Handle day box click to show enhanced expanded view"""
        date_str = date.strftime('%Y-%m-%d')
        orders_for_date = self.orders_by_date.get(date_str, [])

        # Debug information
        print(f"DEBUG: Day clicked: {date_str}")
        print(f"DEBUG: Orders available for this date: {len(orders_for_date)}")
        print(f"DEBUG: Total dates with orders: {list(self.orders_by_date.keys())}")
        print(f"DEBUG: Has pdf_processor: {hasattr(self, 'pdf_processor')}")
        print(f"DEBUG: Has relationship_manager: {hasattr(self, 'relationship_manager')}")

        # Show enhanced expanded view
        if hasattr(self, 'pdf_processor') and hasattr(self, 'relationship_manager'):
            archive_manager = getattr(self, 'archive_manager', None)
            template_path = getattr(self, 'template_path', None)
            settings_manager = getattr(self, 'settings_manager', None)
            expanded_view = EnhancedExpandedView(
                self,
                date,
                orders_for_date,
                self.pdf_processor,
                self.relationship_manager,
                archive_manager,
                template_path,
                settings_manager
            )
            expanded_view.set_statistics_refresh_callback(self.refresh_statistics)
        else:
            # Fallback to simple dialog if processors not available
            print("DEBUG: Using fallback dialog")
            detail_dialog = DayDetailDialog(self, date, orders_for_date)

    def set_statistics_callback(self, callback):
        """Set callback function for calculating statistics"""
        self.calculate_statistics_callback = callback

    def update_calendar_data(self, orders_data: List[Dict]):
        """Update calendar with new orders data"""
        print(f"DEBUG: update_calendar_data called with {len(orders_data)} orders")

        # Group orders by date
        self.orders_by_date.clear()

        for i, order in enumerate(orders_data):
            csv_data = order.get('csv_data', {})
            date_required = csv_data.get('DateRequired', '')
            order_number = csv_data.get('OrderNumber', 'Unknown')

            print(f"DEBUG: Processing order {i}: {order_number}, DateRequired: {date_required}")

            if date_required:
                try:
                    import pandas as pd
                    date_obj = pd.to_datetime(date_required)
                    date_str = date_obj.strftime('%Y-%m-%d')

                    if date_str not in self.orders_by_date:
                        self.orders_by_date[date_str] = []
                    self.orders_by_date[date_str].append(order)

                    print(f"DEBUG: Added order {order_number} to date {date_str}")

                except Exception as e:
                    print(f"DEBUG: Could not parse date {date_required}: {e}")
                    logging.warning(f"Could not parse date {date_required}: {e}")
            else:
                print(f"DEBUG: Order {order_number} has no DateRequired field")

        print(f"DEBUG: Final orders_by_date keys: {list(self.orders_by_date.keys())}")

        # Update statistics for visible days
        self.refresh_statistics()

    def refresh_statistics(self):
        """Refresh statistics for all visible day boxes"""
        for date_str, day_box in self.day_boxes.items():
            orders_for_date = self.orders_by_date.get(date_str, [])

            # Calculate statistics for PDFs
            # Orders are processed if they have the 'processed' flag set to True
            # Green category: has PDF and not processed
            # Red category: no PDF and not processed
            # Gray category: processed (regardless of PDF status)
            previously_processed = sum(1 for order in orders_for_date if order.get('processed', False))
            successful_matches = sum(1 for order in orders_for_date if order.get('has_pdf', False) and not order.get('processed', False))
            no_matches = sum(1 for order in orders_for_date if not order.get('has_pdf', False) and not order.get('processed', False))

            # Calculate statistics for CSVs
            successful_csv = 0
            no_matches_csv = 0
            processed_csv = 0

            if hasattr(self, 'csv_db') and self.csv_db:
                for order in orders_for_date:
                    order_number = order.get('csv_data', {}).get('OrderNumber')
                    if order_number:
                        csv_files = self.csv_db.get_csv_files_by_order(order_number)
                        has_csv = len(csv_files) > 0

                        if order.get('processed', False):
                            if has_csv:
                                processed_csv += 1
                        elif has_csv:
                            successful_csv += 1
                        else:
                            no_matches_csv += 1

            # Update day box with PDF and CSV counts
            day_box.update_statistics(
                successful_matches, no_matches, previously_processed,
                successful_csv, no_matches_csv, processed_csv
            )

    def go_to_today(self):
        """Navigate calendar to current date"""
        today = datetime.now()
        # Get the Monday of the week containing today
        self.current_start_date = self.get_week_start(today)
        self.create_calendar_grid()
        self.update_date_display()
        self.refresh_statistics()

    def open_search_dialog(self):
        """Open search dialog with enhanced search functionality"""
        try:
            # Create a simple search dialog
            search_window = tk.Toplevel(self)
            search_window.title("Search Orders")
            search_window.geometry("500x200")
            search_window.configure(bg='#ecf0f1')
            search_window.transient(self)
            search_window.grab_set()

            # Center the window
            search_window.update_idletasks()
            x = (search_window.winfo_screenwidth() // 2) - (500 // 2)
            y = (search_window.winfo_screenheight() // 2) - (200 // 2)
            search_window.geometry(f"500x200+{x}+{y}")

            # Header
            header_frame = tk.Frame(search_window, bg='#e67e22', height=50)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)

            tk.Label(
                header_frame,
                text="🔍 Search Orders",
                font=("Segoe UI", 16, "bold"),
                bg='#e67e22',
                fg='white'
            ).pack(expand=True)

            # Search content
            content_frame = tk.Frame(search_window, bg='#ecf0f1')
            content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            tk.Label(
                content_frame,
                text="Enter search term (order number, customer, job reference, or designer):",
                font=("Segoe UI", 10),
                bg='#ecf0f1',
                fg='#2c3e50'
            ).pack(pady=(0, 10))

            search_frame = tk.Frame(content_frame, bg='#ecf0f1')
            search_frame.pack(fill=tk.X, pady=10)

            search_var = tk.StringVar()
            search_entry = tk.Entry(
                search_frame,
                textvariable=search_var,
                font=("Segoe UI", 12),
                width=40
            )
            search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
            search_entry.focus()

            def do_search():
                search_term = search_var.get().strip()
                if search_term:
                    search_window.destroy()
                    # Find the main application window and call its search method
                    root_window = self
                    while root_window.master:
                        root_window = root_window.master

                    # Look for the app instance in the root window's children
                    for child in root_window.winfo_children():
                        if hasattr(child, 'perform_search'):
                            child.search_var.set(search_term)
                            child.perform_search()
                            return

                    # Fallback: try to import and use search directly
                    try:
                        from enhanced_database_v2 import EnhancedDatabaseV2
                        from enhanced_search_view import EnhancedSearchView

                        db_manager = EnhancedDatabaseV2()
                        results = db_manager.search_relationships(search_term, 'general')

                        if results:
                            # Create enhanced search view
                            search_view = EnhancedSearchView(
                                root_window,
                                search_term,
                                results,
                                getattr(self, 'pdf_processor', None),
                                getattr(self, 'relationship_manager', None)
                            )
                        else:
                            tk.messagebox.showinfo("Search Results", f"No results found for '{search_term}'")
                    except Exception as e:
                        tk.messagebox.showerror("Search Error", f"Search failed: {str(e)}")
                else:
                    tk.messagebox.showwarning("Search", "Please enter a search term")

            search_entry.bind('<Return>', lambda e: do_search())

            button_frame = tk.Frame(content_frame, bg='#ecf0f1')
            button_frame.pack(fill=tk.X, pady=(10, 0))

            tk.Button(
                button_frame,
                text="🔍 Search",
                command=do_search,
                font=("Segoe UI", 12, "bold"),
                bg='#e67e22',
                fg='white',
                border=0,
                padx=20,
                pady=8,
                cursor='hand2'
            ).pack(side=tk.RIGHT)

            tk.Button(
                button_frame,
                text="Cancel",
                command=search_window.destroy,
                font=("Segoe UI", 10),
                bg='#95a5a6',
                fg='white',
                border=0,
                padx=15,
                pady=8,
                cursor='hand2'
            ).pack(side=tk.RIGHT, padx=(0, 10))

        except Exception as e:
            print(f"Error opening search dialog: {e}")
            tk.messagebox.showerror("Error", f"Could not open search dialog: {str(e)}")

    def set_processors(self, pdf_processor, relationship_manager, archive_manager=None, template_path=None, settings_manager=None, csv_db=None):
        """Set the PDF processor, relationship manager, archive manager, template path, settings manager, and CSV database for enhanced functionality"""
        self.pdf_processor = pdf_processor
        self.relationship_manager = relationship_manager
        self.archive_manager = archive_manager
        self.template_path = template_path
        self.settings_manager = settings_manager
        self.csv_db = csv_db

    def clear_data(self):
        """Clear all calendar data"""
        self.orders_by_date.clear()
        for day_box in self.day_boxes.values():
            day_box.update_statistics(0, 0, 0)