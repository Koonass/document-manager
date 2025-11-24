#!/usr/bin/env python3
"""
Print Preset UI - User interface for managing print presets
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
import logging
from print_preset_manager import PrintPresetManager, PrintPreset


class PresetManagerDialog(tk.Toplevel):
    """Dialog for managing print presets"""

    def __init__(self, parent, preset_manager: PrintPresetManager):
        super().__init__(parent)
        self.parent_window = parent
        self.preset_manager = preset_manager
        self.available_printers = preset_manager.get_available_printers()

        # If no printers found, show a warning
        if not self.available_printers:
            self.available_printers = ["(No printers detected - check printer installation)"]

        self.setup_window()

    def setup_window(self):
        """Create the preset manager window"""
        self.title("Manage Print Presets")
        self.geometry("900x650")
        self.configure(bg='#ecf0f1')
        self.transient(self.parent_window)
        self.grab_set()

        # Header
        header_frame = tk.Frame(self, bg='#34495e', height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text="⚙️ Print Preset Manager",
            font=("Segoe UI", 18, "bold"),
            bg='#34495e',
            fg='white'
        ).pack(expand=True)

        # Main content
        content_frame = tk.Frame(self, bg='#ecf0f1')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left side - Preset list
        left_frame = tk.Frame(content_frame, bg='#ecf0f1')
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))

        tk.Label(
            left_frame,
            text="Saved Presets:",
            font=("Segoe UI", 12, "bold"),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(anchor=tk.W, pady=(0, 10))

        # Preset listbox
        listbox_frame = tk.Frame(left_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)

        self.preset_listbox = tk.Listbox(
            listbox_frame,
            font=("Segoe UI", 11),
            width=25,
            height=15
        )
        self.preset_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.preset_listbox.bind('<<ListboxSelect>>', self.on_preset_selected)

        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.preset_listbox.yview)
        self.preset_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Preset action buttons
        preset_btn_frame = tk.Frame(left_frame, bg='#ecf0f1')
        preset_btn_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Button(
            preset_btn_frame,
            text="➕ New Preset",
            command=self.new_preset,
            font=("Segoe UI", 10),
            bg='#27ae60',
            fg='white',
            border=0,
            padx=15,
            pady=5
        ).pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        tk.Button(
            preset_btn_frame,
            text="🗑️ Delete",
            command=self.delete_preset,
            font=("Segoe UI", 10),
            bg='#e74c3c',
            fg='white',
            border=0,
            padx=15,
            pady=5
        ).pack(side=tk.TOP, fill=tk.X)

        # Right side - Preset editor
        self.right_frame = tk.Frame(content_frame, bg='#ffffff', relief='solid', borderwidth=1)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Initially show "Select a preset" message
        self.show_empty_editor()

        # Populate preset list (must be after right_frame is created)
        self.refresh_preset_list()

        # Bottom buttons
        button_frame = tk.Frame(self, bg='#ecf0f1')
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        tk.Button(
            button_frame,
            text="Close",
            command=self.destroy,
            font=("Segoe UI", 11),
            bg='#95a5a6',
            fg='white',
            border=0,
            padx=25,
            pady=8
        ).pack(side=tk.RIGHT)

    def refresh_preset_list(self):
        """Refresh the preset listbox"""
        self.preset_listbox.delete(0, tk.END)

        for name, preset in self.preset_manager.get_all_presets().items():
            display_name = f"⭐ {name}" if preset.is_default else f"   {name}"
            self.preset_listbox.insert(tk.END, display_name)

        # Select first item
        if self.preset_listbox.size() > 0:
            self.preset_listbox.selection_set(0)
            self.on_preset_selected(None)

    def on_preset_selected(self, event):
        """Handle preset selection"""
        selection = self.preset_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        preset_names = list(self.preset_manager.get_all_presets().keys())
        preset_name = preset_names[index]
        preset = self.preset_manager.get_preset(preset_name)

        if preset:
            self.show_preset_editor(preset_name, preset)

    def show_empty_editor(self):
        """Show empty editor state"""
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.right_frame,
            text="Select a preset to edit\nor create a new one",
            font=("Segoe UI", 13, "italic"),
            bg='#ffffff',
            fg='#95a5a6'
        ).pack(expand=True)

    def show_preset_editor(self, preset_name: str, preset: PrintPreset):
        """Show preset editor"""
        # Clear right frame
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        # Editor content
        editor_frame = tk.Frame(self.right_frame, bg='#ffffff')
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Preset name
        name_frame = tk.Frame(editor_frame, bg='#ffffff')
        name_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(
            name_frame,
            text="Preset Name:",
            font=("Segoe UI", 11, "bold"),
            bg='#ffffff'
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.preset_name_var = tk.StringVar(value=preset_name)
        tk.Entry(
            name_frame,
            textvariable=self.preset_name_var,
            font=("Segoe UI", 11),
            width=30
        ).pack(side=tk.LEFT)

        # 11x17 Printer Settings
        printer1_frame = ttk.LabelFrame(editor_frame, text="11×17 Printer Settings", padding=15)
        printer1_frame.pack(fill=tk.X, pady=(0, 15))

        self.p1_enabled_var = tk.BooleanVar(value=preset.printer_11x17_enabled)
        ttk.Checkbutton(
            printer1_frame,
            text="Enabled",
            variable=self.p1_enabled_var
        ).pack(anchor=tk.W)

        tk.Label(printer1_frame, text="Printer Script:", bg='white').pack(anchor=tk.W, pady=(10, 5))
        self.p1_script_var = tk.StringVar(value=preset.printer_11x17_script)
        p1_combo = ttk.Combobox(
            printer1_frame,
            textvariable=self.p1_script_var,
            values=self.available_printers,
            width=50
        )
        p1_combo.pack(fill=tk.X)

        tk.Label(printer1_frame, text="Copies:", bg='white').pack(anchor=tk.W, pady=(10, 5))
        self.p1_copies_var = tk.IntVar(value=preset.printer_11x17_copies)
        ttk.Spinbox(
            printer1_frame,
            from_=1,
            to=10,
            textvariable=self.p1_copies_var,
            width=10
        ).pack(anchor=tk.W)

        # 24x36 Printer Settings
        printer2_frame = ttk.LabelFrame(editor_frame, text="24×36 Printer Settings", padding=15)
        printer2_frame.pack(fill=tk.X, pady=(0, 15))

        self.p2_enabled_var = tk.BooleanVar(value=preset.printer_24x36_enabled)
        ttk.Checkbutton(
            printer2_frame,
            text="Enabled",
            variable=self.p2_enabled_var
        ).pack(anchor=tk.W)

        tk.Label(printer2_frame, text="Printer Script:", bg='white').pack(anchor=tk.W, pady=(10, 5))
        self.p2_script_var = tk.StringVar(value=preset.printer_24x36_script)
        p2_combo = ttk.Combobox(
            printer2_frame,
            textvariable=self.p2_script_var,
            values=self.available_printers,
            width=50
        )
        p2_combo.pack(fill=tk.X)

        tk.Label(printer2_frame, text="Copies:", bg='white').pack(anchor=tk.W, pady=(10, 5))
        self.p2_copies_var = tk.IntVar(value=preset.printer_24x36_copies)
        ttk.Spinbox(
            printer2_frame,
            from_=1,
            to=10,
            textvariable=self.p2_copies_var,
            width=10
        ).pack(anchor=tk.W)

        # Folder Label Settings
        folder_frame = ttk.LabelFrame(editor_frame, text="Folder Label Settings", padding=15)
        folder_frame.pack(fill=tk.X, pady=(0, 15))

        self.folder_enabled_var = tk.BooleanVar(value=preset.folder_label_enabled)
        ttk.Checkbutton(
            folder_frame,
            text="Print folder labels",
            variable=self.folder_enabled_var
        ).pack(anchor=tk.W)

        tk.Label(
            folder_frame,
            text="ℹ️ Folder labels automatically skip processed orders",
            font=("Segoe UI", 9, "italic"),
            bg='white',
            fg='#7f8c8d'
        ).pack(anchor=tk.W, pady=(5, 10))

        tk.Label(folder_frame, text="Printer Script:", bg='white').pack(anchor=tk.W, pady=(0, 5))
        self.folder_printer_var = tk.StringVar(value=preset.folder_label_printer)
        folder_combo = ttk.Combobox(
            folder_frame,
            textvariable=self.folder_printer_var,
            values=self.available_printers,
            width=50
        )
        folder_combo.pack(fill=tk.X)

        # Save buttons
        save_frame = tk.Frame(editor_frame, bg='#ffffff')
        save_frame.pack(fill=tk.X, pady=(20, 0))

        if preset.is_default:
            tk.Label(
                save_frame,
                text="⭐ Default Preset",
                font=("Segoe UI", 10, "bold"),
                bg='#ffffff',
                fg='#f39c12'
            ).pack(side=tk.LEFT)
        else:
            tk.Button(
                save_frame,
                text="⭐ Set as Default",
                command=lambda: self.set_default(preset_name),
                font=("Segoe UI", 10),
                bg='#f39c12',
                fg='white',
                border=0,
                padx=15,
                pady=5
            ).pack(side=tk.LEFT)

        tk.Button(
            save_frame,
            text="💾 Save Changes",
            command=lambda: self.save_preset(preset_name),
            font=("Segoe UI", 10, "bold"),
            bg='#27ae60',
            fg='white',
            border=0,
            padx=20,
            pady=5
        ).pack(side=tk.RIGHT)

    def save_preset(self, old_name: str):
        """Save preset changes"""
        new_name = self.preset_name_var.get().strip()

        if not new_name:
            messagebox.showwarning("Invalid Name", "Preset name cannot be empty.")
            return

        # Check if renaming to existing name
        if new_name != old_name and new_name in self.preset_manager.get_preset_names():
            messagebox.showwarning("Name Exists", f"A preset named '{new_name}' already exists.")
            return

        # Build preset data
        preset_data = {
            'printer_11x17_enabled': self.p1_enabled_var.get(),
            'printer_11x17_script': self.p1_script_var.get(),
            'printer_11x17_copies': self.p1_copies_var.get(),
            'printer_24x36_enabled': self.p2_enabled_var.get(),
            'printer_24x36_script': self.p2_script_var.get(),
            'printer_24x36_copies': self.p2_copies_var.get(),
            'folder_label_enabled': self.folder_enabled_var.get(),
            'folder_label_printer': self.folder_printer_var.get(),
            'is_default': self.preset_manager.get_preset(old_name).is_default if old_name in self.preset_manager.get_preset_names() else False
        }

        # If renaming, delete old preset
        if new_name != old_name:
            self.preset_manager.delete_preset(old_name)

        # Save preset
        success = self.preset_manager.add_preset(new_name, preset_data)

        if success:
            messagebox.showinfo("Saved", f"Preset '{new_name}' saved successfully!")
            self.refresh_preset_list()
        else:
            messagebox.showerror("Error", "Failed to save preset.")

    def set_default(self, preset_name: str):
        """Set preset as default"""
        success = self.preset_manager.set_default_preset(preset_name)

        if success:
            messagebox.showinfo("Default Set", f"'{preset_name}' is now the default preset.")
            self.refresh_preset_list()
        else:
            messagebox.showerror("Error", "Failed to set default preset.")

    def new_preset(self):
        """Create a new preset"""
        name = tk.simpledialog.askstring("New Preset", "Enter preset name:", parent=self)

        if name:
            name = name.strip()
            if name in self.preset_manager.get_preset_names():
                messagebox.showwarning("Name Exists", f"A preset named '{name}' already exists.")
                return

            # Create new preset with default values
            preset_data = {
                'printer_11x17_enabled': True,
                'printer_11x17_script': '',
                'printer_11x17_copies': 1,
                'printer_24x36_enabled': True,
                'printer_24x36_script': '',
                'printer_24x36_copies': 1,
                'folder_label_enabled': True,
                'folder_label_printer': '',
                'is_default': False
            }

            success = self.preset_manager.add_preset(name, preset_data)

            if success:
                self.refresh_preset_list()
                # Select the new preset
                preset_names = self.preset_manager.get_preset_names()
                index = preset_names.index(name)
                self.preset_listbox.selection_clear(0, tk.END)
                self.preset_listbox.selection_set(index)
                self.on_preset_selected(None)
            else:
                messagebox.showerror("Error", "Failed to create preset.")

    def delete_preset(self):
        """Delete selected preset"""
        selection = self.preset_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a preset to delete.")
            return

        index = selection[0]
        preset_name = list(self.preset_manager.get_all_presets().keys())[index]

        result = messagebox.askyesno(
            "Delete Preset",
            f"Are you sure you want to delete '{preset_name}'?"
        )

        if result:
            success = self.preset_manager.delete_preset(preset_name)

            if success:
                self.refresh_preset_list()
                self.show_empty_editor()
            else:
                messagebox.showerror("Error", "Failed to delete preset.\n(Cannot delete the last preset)")


# Import at the top if needed for askstring
import tkinter.simpledialog
