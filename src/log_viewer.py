#!/usr/bin/env python3
"""
Log Viewer - Simple UI to view error logs
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
from error_logger import get_error_logger


class LogViewerDialog(tk.Toplevel):
    """Dialog to view recent error logs"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.setup_window()

    def setup_window(self):
        """Create the log viewer window"""
        self.title("Error Log Viewer")
        self.geometry("900x600")
        self.configure(bg='#ecf0f1')
        if self.parent_window:
            self.transient(self.parent_window)

        # Header
        header_frame = tk.Frame(self, bg='#34495e', height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text="📋 Error Log Viewer",
            font=("Segoe UI", 18, "bold"),
            bg='#34495e',
            fg='white'
        ).pack(expand=True)

        # Instructions
        info_frame = tk.Frame(self, bg='#ecf0f1')
        info_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            info_frame,
            text="Recent errors from print_errors.log - Copy and send these for debugging",
            font=("Segoe UI", 10),
            bg='#ecf0f1',
            fg='#7f8c8d'
        ).pack()

        # Log display
        log_frame = tk.Frame(self, bg='#ecf0f1')
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=("Consolas", 9),
            wrap=tk.WORD,
            bg='#2c3e50',
            fg='#ecf0f1',
            insertbackground='white'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Load logs
        self.load_logs()

        # Buttons
        button_frame = tk.Frame(self, bg='#ecf0f1')
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        tk.Button(
            button_frame,
            text="🔄 Refresh",
            command=self.load_logs,
            font=("Segoe UI", 10),
            bg='#3498db',
            fg='white',
            border=0,
            padx=20,
            pady=8
        ).pack(side=tk.LEFT)

        tk.Button(
            button_frame,
            text="📋 Copy All",
            command=self.copy_all,
            font=("Segoe UI", 10),
            bg='#27ae60',
            fg='white',
            border=0,
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=(10, 0))

        tk.Button(
            button_frame,
            text="🗑️ Clear Log",
            command=self.clear_log,
            font=("Segoe UI", 10),
            bg='#e74c3c',
            fg='white',
            border=0,
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=(10, 0))

        tk.Button(
            button_frame,
            text="Close",
            command=self.destroy,
            font=("Segoe UI", 10),
            bg='#95a5a6',
            fg='white',
            border=0,
            padx=20,
            pady=8
        ).pack(side=tk.RIGHT)

    def load_logs(self):
        """Load and display recent log entries"""
        self.log_text.delete(1.0, tk.END)

        error_logger = get_error_logger()
        log_content = error_logger.get_recent_errors(lines=200)

        if "No error log file found" in log_content:
            self.log_text.insert(1.0, "No errors logged yet!\n\nThis is good news - the system is working without errors.")
        else:
            self.log_text.insert(1.0, log_content)

        # Scroll to bottom
        self.log_text.see(tk.END)

    def copy_all(self):
        """Copy all log contents to clipboard"""
        try:
            log_content = self.log_text.get(1.0, tk.END)
            self.clipboard_clear()
            self.clipboard_append(log_content)
            messagebox.showinfo("Copied", "Log contents copied to clipboard!", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy: {e}", parent=self)

    def clear_log(self):
        """Clear the error log file"""
        result = messagebox.askyesno(
            "Clear Log",
            "Are you sure you want to clear the error log?\n\nThis cannot be undone.",
            parent=self
        )

        if result:
            error_logger = get_error_logger()
            if error_logger.clear_log():
                self.load_logs()
                messagebox.showinfo("Cleared", "Error log has been cleared.", parent=self)
            else:
                messagebox.showerror("Error", "Failed to clear log file.", parent=self)


def show_log_viewer(parent=None):
    """Show the log viewer dialog"""
    LogViewerDialog(parent)
