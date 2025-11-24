#!/usr/bin/env python3
"""
Two-Week Calendar Widget - Displays orders in 2-week weekday grid using Date Required
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import calendar
from typing import Dict, List, Any, Optional
import uuid
import subprocess
import platform
import os

class OrderCardWidget(ttk.Frame):
    def __init__(self, parent, order_data: Dict, has_pdf: bool = False, on_select=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.order_data = order_data
        self.has_pdf = has_pdf
        self.on_select = on_select
        self.is_selected = False
        self.relationship_id = order_data.get('relationship_id', str(uuid.uuid4()))

        self.setup_card()

    def setup_card(self):
        # Configure the card styling
        self.configure(relief='raised', borderwidth=1, padding=2)

        # Make the entire card clickable
        self.bind("<Button-1>", self.on_card_click)

        # Order number (main identifier)
        order_num = self.order_data.get('OrderNumber', 'N/A')
        order_label = tk.Label(
            self,
            text=f"#{order_num}",
            font=("Arial", 8, "bold"),
            cursor="hand2"
        )
        order_label.pack(anchor=tk.W)
        order_label.bind("<Button-1>", self.on_card_click)

        # Customer name
        customer = self.order_data.get('Customer', 'N/A')
        customer_text = customer[:15] + "..." if len(customer) > 15 else customer
        customer_label = tk.Label(
            self,
            text=customer_text,
            font=("Arial", 7),
            cursor="hand2"
        )
        customer_label.pack(anchor=tk.W)
        customer_label.bind("<Button-1>", self.on_card_click)

        # Status indicator and designer
        bottom_frame = tk.Frame(self)
        bottom_frame.pack(fill=tk.X)

        # Status indicator
        status_color = "green" if self.has_pdf else "red"
        status_symbol = "✓" if self.has_pdf else "✗"
        self.status_label = tk.Label(
            bottom_frame,
            text=status_symbol,
            fg=status_color,
            font=("Arial", 10, "bold"),
            cursor="hand2"
        )
        self.status_label.pack(side=tk.LEFT)
        self.status_label.bind("<Button-1>", self.on_card_click)

        # Designer initials
        designer = self.order_data.get('Designer', 'N/A')
        designer_initials = ''.join([word[0] for word in designer.split() if word])[:3].upper()
        designer_label = tk.Label(
            bottom_frame,
            text=designer_initials,
            font=("Arial", 6),
            cursor="hand2"
        )
        designer_label.pack(side=tk.RIGHT)
        designer_label.bind("<Button-1>", self.on_card_click)

    def on_card_click(self, event=None):
        """Handle card selection"""
        if self.on_select:
            self.on_select(self)

    def set_selected(self, selected: bool):
        """Update card appearance based on selection state"""
        self.is_selected = selected
        if selected:
            self.configure(relief='solid', borderwidth=2)
        else:
            self.configure(relief='raised', borderwidth=1)

    def update_pdf_status(self, has_pdf: bool):
        """Update the PDF status indicator"""
        self.has_pdf = has_pdf
        status_color = "green" if has_pdf else "red"
        status_symbol = "✓" if has_pdf else "✗"
        self.status_label.config(text=status_symbol, fg=status_color)

class PDFActionMenu(tk.Toplevel):
    def __init__(self, parent, order_card: OrderCardWidget, pdf_path: Optional[str] = None):
        super().__init__(parent)

        self.order_card = order_card
        self.pdf_path = pdf_path
        self.order_data = order_card.order_data

        self.setup_menu()

    def setup_menu(self):
        self.title(f"PDF Actions - Order {self.order_data.get('OrderNumber', 'N/A')}")
        self.geometry("300x400")
        self.transient(self.master)
        self.grab_set()

        # Center the window
        self.geometry("+%d+%d" % (self.master.winfo_rootx() + 50, self.master.winfo_rooty() + 50))

        # Header info
        header_frame = ttk.LabelFrame(self, text="Order Information", padding=10)
        header_frame.pack(fill=tk.X, padx=10, pady=5)

        info_text = f"""Order Number: {self.order_data.get('OrderNumber', 'N/A')}
Customer: {self.order_data.get('Customer', 'N/A')}
Job Reference: {self.order_data.get('JobReference', 'N/A')}
Designer: {self.order_data.get('Designer', 'N/A')}
Date Required: {self.order_data.get('DateRequired', 'N/A')}"""

        tk.Label(header_frame, text=info_text, justify=tk.LEFT, font=("Arial", 9)).pack(anchor=tk.W)

        # PDF Status
        status_frame = ttk.LabelFrame(self, text="PDF Status", padding=10)
        status_frame.pack(fill=tk.X, padx=10, pady=5)

        pdf_status = "PDF Attached" if self.pdf_path else "No PDF Found"
        status_color = "green" if self.pdf_path else "red"

        tk.Label(status_frame, text=pdf_status, fg=status_color, font=("Arial", 9, "bold")).pack()

        if self.pdf_path:
            filename = os.path.basename(self.pdf_path)
            tk.Label(status_frame, text=f"File: {filename}", font=("Arial", 8)).pack()

        # Action Buttons
        actions_frame = ttk.LabelFrame(self, text="Available Actions", padding=10)
        actions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Configure button style
        button_style = {"width": 20, "pady": 5}

        if self.pdf_path:
            # Actions available when PDF exists
            ttk.Button(actions_frame, text="📄 View PDF", command=self.view_pdf, **button_style).pack(pady=2)
            ttk.Button(actions_frame, text="🖨️ Print PDF", command=self.print_pdf, **button_style).pack(pady=2)
            ttk.Button(actions_frame, text="📧 Email PDF", command=self.email_pdf, **button_style).pack(pady=2)
            ttk.Button(actions_frame, text="📎 Replace PDF", command=self.replace_pdf, **button_style).pack(pady=2)
            ttk.Button(actions_frame, text="💾 Save PDF As", command=self.save_pdf_as, **button_style).pack(pady=2)
        else:
            # Actions when no PDF
            ttk.Button(actions_frame, text="📎 Attach PDF", command=self.attach_pdf, **button_style).pack(pady=2)

        # Common actions
        ttk.Button(actions_frame, text="🗂️ Open PDF Folder", command=self.open_pdf_folder, **button_style).pack(pady=2)

        # Close button
        ttk.Button(self, text="Close", command=self.destroy).pack(pady=10)

    def view_pdf(self):
        """Open PDF in default viewer"""
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', self.pdf_path))
            elif platform.system() == 'Windows':  # Windows
                os.startfile(self.pdf_path)
            else:  # linux variants
                subprocess.call(('xdg-open', self.pdf_path))
        except Exception as e:
            messagebox.showerror("Error", f"Could not open PDF:\n{str(e)}")

    def print_pdf(self):
        """Print the PDF file"""
        try:
            if platform.system() == 'Windows':
                # Use Windows print command
                subprocess.run(['start', '/print', self.pdf_path], shell=True, check=True)
            else:
                messagebox.showinfo("Print", "Please use your system's print dialog to print the PDF after viewing it.")
                self.view_pdf()
        except Exception as e:
            messagebox.showerror("Error", f"Could not print PDF:\n{str(e)}")

    def email_pdf(self):
        """Open email client with PDF attached"""
        try:
            if platform.system() == 'Windows':
                # Create mailto link with attachment (may not work with all email clients)
                mailto_url = f"mailto:?subject=Order {self.order_data.get('OrderNumber', '')}&body=Please find attached PDF for order {self.order_data.get('OrderNumber', '')}"
                subprocess.run(['start', mailto_url], shell=True)
                messagebox.showinfo("Email", f"Please manually attach the PDF file:\n{self.pdf_path}")
            else:
                messagebox.showinfo("Email", f"Please manually attach this PDF to your email:\n{self.pdf_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open email client:\n{str(e)}")

    def attach_pdf(self):
        """Manually attach a PDF file"""
        file_path = filedialog.askopenfilename(
            title=f"Select PDF for Order {self.order_data.get('OrderNumber', '')}",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if file_path:
            self.pdf_path = file_path
            # Update the order card
            self.order_card.update_pdf_status(True)
            # Notify parent about the PDF attachment
            if hasattr(self.master, 'on_pdf_attached'):
                self.master.on_pdf_attached(self.order_card, file_path)
            messagebox.showinfo("Success", f"PDF attached to order {self.order_data.get('OrderNumber', '')}")
            self.destroy()

    def replace_pdf(self):
        """Replace the current PDF with a new one"""
        result = messagebox.askyesno("Replace PDF", f"Replace the current PDF for order {self.order_data.get('OrderNumber', '')}?")
        if result:
            self.attach_pdf()  # Reuse attach logic

    def save_pdf_as(self):
        """Save PDF to a different location"""
        if not self.pdf_path:
            return

        save_path = filedialog.asksaveasfilename(
            title="Save PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialname=f"Order_{self.order_data.get('OrderNumber', '')}.pdf"
        )

        if save_path:
            try:
                import shutil
                shutil.copy2(self.pdf_path, save_path)
                messagebox.showinfo("Success", f"PDF saved to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save PDF:\n{str(e)}")

    def open_pdf_folder(self):
        """Open the folder containing the PDF"""
        try:
            if self.pdf_path:
                folder_path = os.path.dirname(self.pdf_path)
            else:
                # Open the configured PDF folder
                folder_path = getattr(self.master, 'pdf_folder_path', '')

            if folder_path and os.path.exists(folder_path):
                if platform.system() == 'Windows':
                    subprocess.run(['explorer', folder_path])
                elif platform.system() == 'Darwin':
                    subprocess.run(['open', folder_path])
                else:
                    subprocess.run(['xdg-open', folder_path])
            else:
                messagebox.showwarning("Warning", "PDF folder not found or not configured")

        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{str(e)}")

class TwoWeekCalendarWidget(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.current_start_date = self.get_week_start(datetime.now())
        self.selected_card = None
        self.order_cards = {}  # date -> list of cards
        self.pdf_folder_path = ""

        self.setup_ui()

    def get_week_start(self, date: datetime) -> datetime:
        """Get the Monday of the week containing the given date"""
        days_since_monday = date.weekday()
        return date - timedelta(days=days_since_monday)

    def setup_ui(self):
        # Navigation header
        nav_frame = ttk.Frame(self)
        nav_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(nav_frame, text="◄ Previous", command=self.prev_2weeks).pack(side=tk.LEFT)

        self.date_label = ttk.Label(nav_frame, text="", font=("Arial", 12, "bold"))
        self.date_label.pack(side=tk.LEFT, expand=True)

        ttk.Button(nav_frame, text="Next ►", command=self.next_2weeks).pack(side=tk.RIGHT)

        # Calendar grid (2 weeks x 5 days = 10 boxes)
        self.calendar_frame = ttk.Frame(self, relief='sunken', borderwidth=1)
        self.calendar_frame.pack(fill=tk.BOTH, expand=True)

        self.create_calendar_grid()
        self.update_date_display()

    def create_calendar_grid(self):
        """Create the 2-week calendar grid"""
        # Clear existing widgets
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        # Configure grid weights
        for i in range(5):  # 5 columns (Mon-Fri)
            self.calendar_frame.columnconfigure(i, weight=1)
        for i in range(3):  # 3 rows (headers + 2 weeks)
            self.calendar_frame.rowconfigure(i, weight=1)

        # Weekday headers
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        for col, day_name in enumerate(weekdays):
            header = ttk.Label(
                self.calendar_frame,
                text=day_name,
                font=("Arial", 10, "bold"),
                anchor='center',
                relief='raised',
                borderwidth=1
            )
            header.grid(row=0, column=col, sticky=(tk.W, tk.E, tk.N, tk.S), padx=1, pady=1)

        # Create day frames for 2 weeks
        self.day_frames = {}
        for week in range(2):
            for day in range(5):  # Monday to Friday
                current_date = self.current_start_date + timedelta(days=(week * 7) + day)
                date_str = current_date.strftime('%Y-%m-%d')

                # Create scrollable frame for each day
                day_frame = tk.Frame(
                    self.calendar_frame,
                    relief='sunken',
                    borderwidth=1,
                    bg='white'
                )
                day_frame.grid(row=week + 1, column=day, sticky=(tk.W, tk.E, tk.N, tk.S), padx=1, pady=1)

                # Date header within day
                date_header = tk.Label(
                    day_frame,
                    text=current_date.strftime('%m/%d'),
                    font=("Arial", 8, "bold"),
                    bg='lightgray'
                )
                date_header.pack(fill=tk.X)

                # Scrollable area for cards
                canvas = tk.Canvas(day_frame, bg='white', highlightthickness=0)
                scrollbar = ttk.Scrollbar(day_frame, orient="vertical", command=canvas.yview)
                scrollable_frame = tk.Frame(canvas, bg='white')

                scrollable_frame.bind(
                    "<Configure>",
                    lambda e, c=canvas: c.configure(scrollregion=c.bbox("all"))
                )

                canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)

                canvas.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")

                self.day_frames[date_str] = scrollable_frame

    def update_date_display(self):
        """Update the date range display"""
        end_date = self.current_start_date + timedelta(days=13)  # 2 weeks - 1 day
        date_text = f"{self.current_start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
        self.date_label.config(text=date_text)

    def prev_2weeks(self):
        """Navigate to previous 2 weeks"""
        self.current_start_date -= timedelta(days=14)
        self.create_calendar_grid()
        self.update_date_display()
        self.refresh_cards()

    def next_2weeks(self):
        """Navigate to next 2 weeks"""
        self.current_start_date += timedelta(days=14)
        self.create_calendar_grid()
        self.update_date_display()
        self.refresh_cards()

    def add_order_card(self, order_data: Dict, has_pdf: bool = False, pdf_path: Optional[str] = None):
        """Add an order card to the appropriate date"""
        # Extract date from order data
        date_required = order_data.get('DateRequired', '')
        if not date_required:
            return  # Skip orders without dates

        try:
            # Parse the date (adjust format as needed for your CSV)
            import pandas as pd
            date_obj = pd.to_datetime(date_required)
            date_str = date_obj.strftime('%Y-%m-%d')

            # Check if this date is in our current 2-week view
            if date_str not in self.day_frames:
                return  # Date not in current view

            # Create the card
            card = OrderCardWidget(
                self.day_frames[date_str],
                order_data,
                has_pdf,
                on_select=self.on_card_selected
            )
            card.pdf_path = pdf_path
            card.pack(fill=tk.X, padx=2, pady=1)

            # Store card reference
            if date_str not in self.order_cards:
                self.order_cards[date_str] = []
            self.order_cards[date_str].append(card)

        except Exception as e:
            print(f"Error adding card for date {date_required}: {e}")

    def on_card_selected(self, card: OrderCardWidget):
        """Handle card selection and show action menu"""
        # Deselect previous card
        if self.selected_card:
            self.selected_card.set_selected(False)

        # Select new card
        self.selected_card = card
        card.set_selected(True)

        # Show PDF action menu
        action_menu = PDFActionMenu(self, card, getattr(card, 'pdf_path', None))

    def on_pdf_attached(self, order_card: OrderCardWidget, pdf_path: str):
        """Handle PDF attachment to an order card"""
        order_card.pdf_path = pdf_path
        order_card.update_pdf_status(True)

        # Notify parent component if needed
        if hasattr(self.master, 'on_order_pdf_updated'):
            self.master.on_order_pdf_updated(order_card.order_data, pdf_path)

    def clear_all_cards(self):
        """Clear all order cards from the calendar"""
        self.order_cards.clear()
        self.selected_card = None
        for day_frame in self.day_frames.values():
            for widget in day_frame.winfo_children():
                if isinstance(widget, OrderCardWidget):
                    widget.destroy()

    def refresh_cards(self):
        """Refresh cards for current view period"""
        # This will be called by the parent to refresh the display
        self.clear_all_cards()

    def set_pdf_folder_path(self, path: str):
        """Set the PDF folder path for actions"""
        self.pdf_folder_path = path