#!/usr/bin/env python3
"""
Calendar Widget - Weekday-only calendar display for unprocessed items
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import calendar
from typing import Dict, List, Any

class WeekdayCalendar(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.events = {}  # Date -> List of events
        self.selected_date = None

        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.setup_ui()
        self.display_current_month()

    def setup_ui(self):
        """Create the calendar interface"""
        # Header frame for navigation
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)

        # Navigation buttons
        self.prev_btn = ttk.Button(header_frame, text="< Prev", command=self.prev_month)
        self.prev_btn.grid(row=0, column=0, padx=(0, 10))

        self.month_label = ttk.Label(header_frame, text="", font=("Arial", 12, "bold"))
        self.month_label.grid(row=0, column=1)

        self.next_btn = ttk.Button(header_frame, text="Next >", command=self.next_month)
        self.next_btn.grid(row=0, column=2, padx=(10, 0))

        # Calendar frame
        self.calendar_frame = ttk.Frame(self)
        self.calendar_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure calendar grid weights
        for i in range(7):  # 7 columns for weekdays
            self.calendar_frame.columnconfigure(i, weight=1)

        # Current date tracking
        self.current_date = datetime.now().replace(day=1)

        # Create day buttons storage
        self.day_buttons = {}

    def display_current_month(self):
        """Display the current month calendar"""
        # Clear existing widgets
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        self.day_buttons.clear()

        # Update month label
        month_name = self.current_date.strftime("%B %Y")
        self.month_label.config(text=month_name)

        # Weekday headers (Monday to Friday only)
        weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
        for i, day_name in enumerate(weekdays):
            header = ttk.Label(
                self.calendar_frame,
                text=day_name,
                font=("Arial", 10, "bold"),
                anchor='center'
            )
            header.grid(row=0, column=i, padx=1, pady=1, sticky=(tk.W, tk.E))

        # Get calendar data for the month
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)

        row = 1
        for week in cal:
            # Only show Monday through Friday (weekday indices 0-4)
            for col, day in enumerate(week[:5]):  # Only first 5 days (Mon-Fri)
                if day == 0:
                    # Empty cell for days from other months
                    empty_label = ttk.Label(self.calendar_frame, text="")
                    empty_label.grid(row=row, column=col, padx=1, pady=1)
                else:
                    # Create day button
                    date_str = f"{self.current_date.year:04d}-{self.current_date.month:02d}-{day:02d}"

                    # Check if this date has events
                    event_count = len(self.events.get(date_str, []))

                    # Create button text
                    button_text = str(day)
                    if event_count > 0:
                        button_text += f"\n({event_count})"

                    # Create button with appropriate styling
                    btn = tk.Button(
                        self.calendar_frame,
                        text=button_text,
                        command=lambda d=date_str: self.select_date(d),
                        width=8,
                        height=3,
                        font=("Arial", 9)
                    )

                    # Style the button based on events
                    if event_count > 0:
                        btn.config(bg='#ffcccc', fg='black')  # Light red for events
                    else:
                        btn.config(bg='white', fg='black')

                    # Highlight today
                    today = datetime.now().strftime("%Y-%m-%d")
                    if date_str == today:
                        btn.config(relief='solid', bd=2)

                    btn.grid(row=row, column=col, padx=1, pady=1, sticky=(tk.W, tk.E, tk.N, tk.S))
                    self.day_buttons[date_str] = btn

            row += 1

        # Configure row weights for proper expansion
        for i in range(row):
            self.calendar_frame.rowconfigure(i, weight=1)

    def prev_month(self):
        """Navigate to previous month"""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.display_current_month()

    def next_month(self):
        """Navigate to next month"""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.display_current_month()

    def add_event(self, date_str: str, event_title: str, event_data: Any = None):
        """Add an event to a specific date"""
        if date_str not in self.events:
            self.events[date_str] = []

        event = {
            'title': event_title,
            'data': event_data,
            'timestamp': datetime.now()
        }
        self.events[date_str].append(event)

        # Update the display if this month is currently shown
        if self.is_date_in_current_month(date_str):
            self.display_current_month()

    def remove_event(self, date_str: str, event_title: str):
        """Remove an event from a specific date"""
        if date_str in self.events:
            self.events[date_str] = [
                event for event in self.events[date_str]
                if event['title'] != event_title
            ]

            # Remove empty date entries
            if not self.events[date_str]:
                del self.events[date_str]

            # Update display
            if self.is_date_in_current_month(date_str):
                self.display_current_month()

    def clear_events(self):
        """Clear all events"""
        self.events.clear()
        self.display_current_month()

    def get_events(self, date_str: str) -> List[Dict]:
        """Get events for a specific date"""
        return self.events.get(date_str, [])

    def select_date(self, date_str: str):
        """Handle date selection"""
        self.selected_date = date_str

        # Update button styling to show selection
        for date, button in self.day_buttons.items():
            if date == date_str:
                button.config(relief='solid', bd=3)
            else:
                # Reset to default styling
                event_count = len(self.events.get(date, []))
                if event_count > 0:
                    button.config(relief='raised', bd=1)
                else:
                    button.config(relief='raised', bd=1)

        # Show event details for selected date
        self.show_date_details(date_str)

    def show_date_details(self, date_str: str):
        """Show details for the selected date"""
        events = self.get_events(date_str)

        if events:
            # Create a popup window with event details
            details_window = tk.Toplevel(self)
            details_window.title(f"Events for {date_str}")
            details_window.geometry("400x300")

            # Create scrollable text widget
            text_frame = ttk.Frame(details_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            text_widget = tk.Text(text_frame, wrap=tk.WORD)
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)

            # Display events
            for i, event in enumerate(events, 1):
                text_widget.insert(tk.END, f"{i}. {event['title']}\n")
                if event['data']:
                    # If event has additional data, show relevant details
                    if isinstance(event['data'], dict):
                        if 'sales_order' in event['data']:
                            text_widget.insert(tk.END, f"   Sales Order: {event['data']['sales_order']}\n")
                        if 'pdf_path' in event['data']:
                            filename = event['data']['pdf_path'].split('\\')[-1].split('/')[-1]
                            text_widget.insert(tk.END, f"   PDF: {filename}\n")
                text_widget.insert(tk.END, "\n")

            text_widget.config(state=tk.DISABLED)  # Make read-only

            # Pack widgets
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Add close button
            close_btn = ttk.Button(
                details_window,
                text="Close",
                command=details_window.destroy
            )
            close_btn.pack(pady=10)

    def is_date_in_current_month(self, date_str: str) -> bool:
        """Check if a date is in the currently displayed month"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return (date_obj.year == self.current_date.year and
                    date_obj.month == self.current_date.month)
        except:
            return False

    def get_selected_date(self) -> str:
        """Get the currently selected date"""
        return self.selected_date

    def highlight_date(self, date_str: str, color: str = '#ffff99'):
        """Highlight a specific date with a color"""
        if date_str in self.day_buttons:
            self.day_buttons[date_str].config(bg=color)