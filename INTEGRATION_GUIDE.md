# Integration Guide - Network Printing System

## How to Integrate the New Network Printing System into Your Application

This guide shows you how to update your main application (main_v2_3.py or similar) to use the new network printing system.

---

## Quick Start

### 1. Check if Setup is Needed

Add this code to your application startup:

```python
from network_printer_manager import NetworkPrinterManager
from printer_setup_wizard import run_setup_wizard
from tkinter import messagebox

# Initialize network printer manager
network_manager = NetworkPrinterManager()

# Check if setup needed
if network_manager.needs_setup():
    result = messagebox.askyesno(
        "Initial Setup Required",
        "Printer configuration not found. Would you like to run the setup wizard now?\n\n"
        "(Recommended for first-time setup or after printer changes)",
        icon='question'
    )

    if result:
        run_setup_wizard(root_window)  # Pass your main window
        # Reload manager after setup
        network_manager = NetworkPrinterManager()
    else:
        messagebox.showwarning(
            "Setup Skipped",
            "You can run the setup wizard later from Tools > Printer Setup"
        )
```

### 2. Update Your Print Button Handler

Replace your old print button code with this:

```python
from network_batch_print import show_print_config_dialog, execute_network_batch_print
from user_preferences import UserPreferencesManager

def on_print_button_click(self):
    """Handle print button click"""
    # Get selected orders
    selected_orders = self.get_selected_orders()  # Your existing method

    if not selected_orders:
        messagebox.showwarning("No Selection", "Please select orders to print.")
        return

    # Initialize managers
    network_manager = NetworkPrinterManager()
    user_prefs = UserPreferencesManager()

    # Check if printers configured
    if network_manager.needs_setup():
        messagebox.showwarning(
            "Setup Required",
            "Please configure printers first:\nTools > Printer Setup"
        )
        return

    # Validate printer availability
    validation = network_manager.validate_configured_printers()
    if validation['missing']:
        result = messagebox.askyesno(
            "Printers Unavailable",
            f"The following printers are not available:\n\n" +
            '\n'.join(f"  • {p}" for p in validation['missing']) +
            "\n\nDo you want to continue anyway?",
            icon='warning'
        )
        if not result:
            return

    # Show print configuration dialog
    print_config = show_print_config_dialog(
        self.window,
        network_manager,
        user_prefs,
        len(selected_orders)
    )

    if not print_config:
        return  # User cancelled

    # Execute batch print
    success = execute_network_batch_print(
        selected_orders,
        network_manager,
        print_config,
        self.window,
        mark_processed_callback=self.mark_orders_as_processed  # Your existing callback
    )

    if success:
        self.refresh_view()  # Your existing refresh method
```

### 3. Add Menu Item for Setup Wizard

Add this to your menu bar:

```python
# In your menu creation code
tools_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Tools", menu=tools_menu)

tools_menu.add_command(
    label="Printer Setup...",
    command=self.open_printer_setup
)

tools_menu.add_command(
    label="Printer Diagnostics...",
    command=self.open_printer_diagnostics
)

# Add the handler methods
def open_printer_setup(self):
    """Open printer setup wizard"""
    from printer_setup_wizard import run_setup_wizard
    network_manager = run_setup_wizard(self.window)
    # Refresh any printer-related UI if needed

def open_printer_diagnostics(self):
    """Open printer diagnostics tool"""
    import subprocess
    subprocess.Popen(['python', 'printer_diagnostics.py'])
```

---

## Complete Integration Example

Here's a complete example of integrating into an enhanced expanded view:

```python
# At top of your file, add imports
from network_printer_manager import NetworkPrinterManager
from network_batch_print import show_print_config_dialog, execute_network_batch_print
from user_preferences import UserPreferencesManager
from printer_setup_wizard import run_setup_wizard

class EnhancedExpandedView:
    def __init__(self, parent, ...):
        # ... your existing init code ...

        # Initialize network printer system
        self.network_manager = NetworkPrinterManager()
        self.user_prefs = UserPreferencesManager()

        # Check if initial setup needed (first time only)
        if self.network_manager.needs_setup():
            self.show_setup_prompt()

    def show_setup_prompt(self):
        """Show setup wizard prompt on first run"""
        result = messagebox.askyesno(
            "Printer Setup",
            "Network printer configuration not found.\n\n"
            "Would you like to configure printers now?\n\n"
            "(This only needs to be done once per installation)",
            icon='question'
        )

        if result:
            run_setup_wizard(self.window)
            # Reload manager
            self.network_manager = NetworkPrinterManager()

    def create_print_button(self, parent_frame):
        """Create the print button (updated version)"""
        print_btn = tk.Button(
            parent_frame,
            text="🖨️ Print Selected Orders",
            command=self.handle_print_orders,
            font=("Segoe UI", 12, "bold"),
            bg='#27ae60',
            fg='white',
            border=0,
            padx=30,
            pady=15
        )
        print_btn.pack(pady=20)
        return print_btn

    def handle_print_orders(self):
        """Handle printing selected orders (NEW VERSION)"""
        # Get selected orders from checkboxes
        selected_orders = []

        # Collect from each category
        for order_widget in self.green_orders_widgets:
            if order_widget['checkbox_var'].get():
                selected_orders.append(order_widget['order'])

        for order_widget in self.red_orders_widgets:
            if order_widget['checkbox_var'].get():
                selected_orders.append(order_widget['order'])

        for order_widget in self.gray_orders_widgets:
            if order_widget['checkbox_var'].get():
                selected_orders.append(order_widget['order'])

        if not selected_orders:
            messagebox.showwarning(
                "No Selection",
                "Please select at least one order to print."
            )
            return

        # Check printer configuration
        if self.network_manager.needs_setup():
            result = messagebox.askyesno(
                "Setup Required",
                "Printers are not configured yet.\n\n"
                "Would you like to run the setup wizard now?",
                icon='warning'
            )

            if result:
                run_setup_wizard(self.window)
                self.network_manager = NetworkPrinterManager()
            else:
                return

        # Validate printer availability
        validation = self.network_manager.validate_configured_printers()

        if validation['missing']:
            missing_list = '\n'.join(f"  • {p}" for p in validation['missing'])
            result = messagebox.askyesno(
                "Printers Unavailable",
                f"Warning: Some printers are not available:\n\n{missing_list}\n\n"
                "These printers may be offline or disconnected.\n\n"
                "Do you want to continue with available printers?",
                icon='warning'
            )

            if not result:
                return

        # Show print configuration dialog
        print_config = show_print_config_dialog(
            self.window,
            self.network_manager,
            self.user_prefs,
            len(selected_orders)
        )

        if not print_config:
            return  # User cancelled

        # Execute batch print with network system
        success = execute_network_batch_print(
            selected_orders,
            self.network_manager,
            print_config,
            self.window,
            mark_processed_callback=self.mark_orders_processed
        )

        if success:
            # Refresh the view to show updated status
            self.refresh_orders_display()

    def mark_orders_processed(self, orders):
        """Mark orders as processed (your existing method)"""
        # Your existing implementation
        for order in orders:
            order_number = order.get('csv_data', {}).get('OrderNumber')
            if order_number:
                self.db_manager.mark_order_processed(order_number)

        # Refresh display
        self.refresh_orders_display()
```

---

## Migration from Old Preset System

If you're currently using the old `print_presets.json` system, here's how to migrate:

### What Changed

| Old System | New System |
|------------|------------|
| `print_presets.json` | `network_printers.json` (centralized) + `user_preferences.json` (per-user) |
| User selects preset | User configures print job dynamically |
| Hardcoded printer names in presets | IT manages printer names centrally |
| No printer validation | Auto-validates printer availability |
| No setup wizard | Setup wizard + diagnostics |

### Migration Steps

1. **Keep old system running** (for backward compatibility):
   ```python
   # Try new system first, fall back to old if needed
   try:
       from network_printer_manager import NetworkPrinterManager
       network_manager = NetworkPrinterManager()

       if not network_manager.needs_setup():
           # Use new system
           use_network_printing = True
       else:
           # Fall back to old system
           use_network_printing = False
   except:
       # Old system
       use_network_printing = False
   ```

2. **Prompt users to run setup**:
   ```python
   if not use_network_printing:
       messagebox.showinfo(
           "Upgrade Available",
           "A new network printing system is available!\n\n"
           "Would you like to configure it now?\n\n"
           "Benefits:\n"
           "  • Centralized printer configuration\n"
           "  • Auto-discovery of printers\n"
           "  • Better error messages\n"
           "  • Easier IT management",
           icon='info'
       )

       # Offer to run setup wizard...
   ```

3. **Gradually phase out old system** once all users have configured new system

---

## Testing Integration

### Test Checklist

- [ ] Application starts without errors
- [ ] Setup wizard appears on first run (or when no config)
- [ ] Can complete setup wizard successfully
- [ ] Print configuration dialog shows available printers
- [ ] Can print successfully to 11×17 printer
- [ ] Can print successfully to 24×36 plotter
- [ ] Can print folder labels successfully
- [ ] Proper error messages when printer offline
- [ ] Orders marked as processed after successful print
- [ ] Diagnostics tool accessible from menu
- [ ] Setup wizard accessible from menu

### Manual Testing

1. **Fresh Install Test:**
   ```bash
   # Delete config files
   del network_printers.json
   del user_preferences.json

   # Run application
   python run_v2_3.py

   # Should prompt for setup
   ```

2. **Printer Offline Test:**
   ```bash
   # Temporarily disconnect a printer
   # Try to print
   # Should show clear error message
   ```

3. **Multi-User Test:**
   ```bash
   # Run as different users
   # Each should have own user_preferences.json
   # All should use same network_printers.json
   ```

---

## Common Integration Issues

### Issue: ImportError when importing new modules

**Solution:** Ensure all new files are in the correct location:
```
src/
├── network_printer_manager.py
├── printer_setup_wizard.py
├── network_batch_print.py
└── user_preferences.py
```

### Issue: Setup wizard doesn't show printers

**Solution:** Check pywin32 installation:
```bash
pip install --upgrade pywin32
python -c "import win32print; print(win32print.EnumPrinters(6))"
```

### Issue: Template path not found

**Solution:** Use absolute or network paths in config:
```json
{
  "template_path": "C:\\code\\Document Manager\\DESIGN FILES\\Template.docx"
}
```

Or for network:
```json
{
  "template_path": "\\\\SERVER\\Share\\DocumentManager\\Template.docx"
}
```

---

## Performance Considerations

### Lazy Loading

Load managers only when needed:

```python
class YourApp:
    def __init__(self):
        # Don't load immediately
        self._network_manager = None
        self._user_prefs = None

    @property
    def network_manager(self):
        """Lazy-load network manager"""
        if self._network_manager is None:
            self._network_manager = NetworkPrinterManager()
        return self._network_manager

    @property
    def user_prefs(self):
        """Lazy-load user preferences"""
        if self._user_prefs is None:
            self._user_prefs = UserPreferencesManager()
        return self._user_prefs
```

### Caching

Cache printer discovery results:

```python
# In your app class
self._cached_printers = None
self._cache_timestamp = None

def get_available_printers(self):
    """Get printers with caching"""
    import time

    # Cache for 5 minutes
    if (self._cached_printers is None or
        time.time() - self._cache_timestamp > 300):
        self._cached_printers = self.network_manager.discover_printers()
        self._cache_timestamp = time.time()

    return self._cached_printers
```

---

## Next Steps

1. **Test in Development**
   - Run through all test cases
   - Verify error handling
   - Test with offline printers

2. **Pilot Deployment**
   - Deploy to small group of users
   - Gather feedback
   - Monitor logs

3. **Full Rollout**
   - Deploy to all users
   - Provide training
   - Monitor for issues

4. **Ongoing Maintenance**
   - Regular diagnostics checks
   - Update printer configs as needed
   - Review error logs

---

## Support

For integration help:

1. Run diagnostics tool: `python printer_diagnostics.py`
2. Export diagnostic report
3. Check logs: `document_manager_v2.3.log`
4. Review this guide for common issues

---

**Last Updated:** October 2025
