#!/usr/bin/env python3
"""
Fix Printer Presets - Populate empty printer names in print_presets.json
This is a quick fix to make the old preset system work while you migrate to the new system
"""

import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import win32print
except ImportError:
    print("ERROR: pywin32 not installed")
    print("Install with: pip install pywin32")
    sys.exit(1)


def get_available_printers():
    """Get all available printers"""
    try:
        printers = win32print.EnumPrinters(
            win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        )
        return [printer[2] for printer in printers]
    except Exception as e:
        print(f"Error getting printers: {e}")
        return []


def categorize_printers(printers):
    """Categorize printers by type"""
    categories = {
        'large_format': [],
        'standard': [],
        'label': [],
        'other': []
    }

    large_format_keywords = [
        'designjet', 'plotter', 'wide', 'format', 'imageprograf',
        '24x36', '36', 'arch', 'cad', 'engineering', 'hp-z'
    ]

    standard_keywords = [
        '11x17', 'tabloid', 'ledger', 'legal'
    ]

    label_keywords = [
        'label', 'dymo', 'zebra', 'brother', 'ql', 'p-touch'
    ]

    for printer in printers:
        printer_lower = printer.lower()

        if any(keyword in printer_lower for keyword in large_format_keywords):
            categories['large_format'].append(printer)
        elif any(keyword in printer_lower for keyword in standard_keywords):
            categories['standard'].append(printer)
        elif any(keyword in printer_lower for keyword in label_keywords):
            categories['label'].append(printer)
        else:
            categories['other'].append(printer)

    return categories


def main():
    print("=" * 70)
    print("  Fix Printer Presets - Quick Fix Tool")
    print("=" * 70)
    print()

    # Load existing presets
    presets_file = "print_presets.json"

    if not os.path.exists(presets_file):
        print(f"ERROR: {presets_file} not found!")
        sys.exit(1)

    with open(presets_file, 'r') as f:
        presets = json.load(f)

    print(f"Loaded {len(presets)} preset(s) from {presets_file}")
    print()

    # Get available printers
    print("Discovering printers...")
    available_printers = get_available_printers()

    if not available_printers:
        print("ERROR: No printers found!")
        print("Make sure printers are installed and accessible.")
        sys.exit(1)

    print(f"Found {len(available_printers)} printer(s):")
    for printer in available_printers:
        print(f"  • {printer}")
    print()

    # Categorize printers
    categories = categorize_printers(available_printers)

    print("Categorized printers:")
    print(f"  Large Format (24×36): {len(categories['large_format'])}")
    for p in categories['large_format']:
        print(f"    - {p}")

    print(f"  Standard (11×17): {len(categories['standard'])}")
    for p in categories['standard']:
        print(f"    - {p}")

    print(f"  Label: {len(categories['label'])}")
    for p in categories['label']:
        print(f"    - {p}")

    print(f"  Other: {len(categories['other'])}")
    for p in categories['other']:
        print(f"    - {p}")
    print()

    # Let user select printers
    print("=" * 70)
    print("  Select Printers")
    print("=" * 70)
    print()

    # Select 11x17 printer
    print("Select 11×17 Printer:")
    candidates = categories['standard'] + categories['other']
    if candidates:
        for i, printer in enumerate(candidates, 1):
            print(f"  {i}. {printer}")
        print(f"  {len(candidates) + 1}. None (skip)")

        while True:
            try:
                choice = input(f"\nEnter number (1-{len(candidates) + 1}): ").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= len(candidates):
                    printer_11x17 = candidates[choice_num - 1]
                    print(f"✓ Selected: {printer_11x17}")
                    break
                elif choice_num == len(candidates) + 1:
                    printer_11x17 = ""
                    print("✓ Skipped")
                    break
            except (ValueError, IndexError):
                print("Invalid choice, try again")
    else:
        printer_11x17 = ""
        print("  No suitable printers found")

    print()

    # Select 24x36 printer
    print("Select 24×36 Large Format Printer:")
    candidates = categories['large_format'] + categories['other']
    if candidates:
        for i, printer in enumerate(candidates, 1):
            print(f"  {i}. {printer}")
        print(f"  {len(candidates) + 1}. None (skip)")

        while True:
            try:
                choice = input(f"\nEnter number (1-{len(candidates) + 1}): ").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= len(candidates):
                    printer_24x36 = candidates[choice_num - 1]
                    print(f"✓ Selected: {printer_24x36}")
                    break
                elif choice_num == len(candidates) + 1:
                    printer_24x36 = ""
                    print("✓ Skipped")
                    break
            except (ValueError, IndexError):
                print("Invalid choice, try again")
    else:
        printer_24x36 = ""
        print("  No suitable printers found")

    print()

    # Select folder label printer
    print("Select Folder Label Printer:")
    candidates = categories['label'] + categories['standard'] + categories['other']
    if candidates:
        for i, printer in enumerate(candidates, 1):
            print(f"  {i}. {printer}")
        print(f"  {len(candidates) + 1}. None (skip)")

        while True:
            try:
                choice = input(f"\nEnter number (1-{len(candidates) + 1}): ").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= len(candidates):
                    folder_printer = candidates[choice_num - 1]
                    print(f"✓ Selected: {folder_printer}")
                    break
                elif choice_num == len(candidates) + 1:
                    folder_printer = ""
                    print("✓ Skipped")
                    break
            except (ValueError, IndexError):
                print("Invalid choice, try again")
    else:
        folder_printer = ""
        print("  No suitable printers found")

    print()
    print("=" * 70)
    print("  Summary")
    print("=" * 70)
    print(f"11×17 Printer: {printer_11x17 or '(none)'}")
    print(f"24×36 Printer: {printer_24x36 or '(none)'}")
    print(f"Folder Label: {folder_printer or '(none)'}")
    print()

    # Confirm
    confirm = input("Update print_presets.json with these printers? (yes/no): ").strip().lower()

    if confirm not in ['yes', 'y']:
        print("Cancelled.")
        sys.exit(0)

    # Update all presets
    for preset_name, preset_data in presets.items():
        preset_data['printer_11x17_script'] = printer_11x17
        preset_data['printer_24x36_script'] = printer_24x36
        preset_data['folder_label_printer'] = folder_printer

    # Backup old file
    backup_file = "print_presets.json.backup"
    with open(backup_file, 'w') as f:
        with open(presets_file, 'r') as original:
            f.write(original.read())
    print(f"✓ Backed up old presets to: {backup_file}")

    # Save updated presets
    with open(presets_file, 'w') as f:
        json.dump(presets, f, indent=2)

    print(f"✓ Updated {presets_file}")
    print()
    print("=" * 70)
    print("  SUCCESS!")
    print("=" * 70)
    print()
    print("Your print_presets.json has been updated with actual printer names.")
    print("You can now use the 'Manage Presets' UI in your application.")
    print()
    print("Try printing again - both 11×17 and 24×36 should work now!")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
