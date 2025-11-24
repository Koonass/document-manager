#!/usr/bin/env python3
"""
Print Diagnostics - Test and diagnose print system issues
Generates a detailed report that can be copied and shared
"""

import sys
import os
import traceback
from datetime import datetime
from pathlib import Path


def generate_diagnostic_report():
    """Generate a comprehensive diagnostic report"""

    report = []
    report.append("=" * 80)
    report.append("PRINT SYSTEM DIAGNOSTIC REPORT")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    report.append("")

    # System Information
    report.append("SYSTEM INFORMATION:")
    report.append("-" * 80)
    try:
        import platform
        report.append(f"OS: {platform.system()} {platform.release()}")
        report.append(f"Python Version: {sys.version}")
        report.append(f"Machine: {platform.machine()}")
        report.append(f"Processor: {platform.processor()}")
    except Exception as e:
        report.append(f"ERROR getting system info: {e}")
    report.append("")

    # Check Required Modules
    report.append("REQUIRED MODULES:")
    report.append("-" * 80)

    modules_to_check = [
        'win32print',
        'win32api',
        'tkinter',
        'PyPDF2',
        'docx'
    ]

    for module_name in modules_to_check:
        try:
            if module_name == 'tkinter':
                import tkinter
                report.append(f"✓ {module_name}: OK (version: {tkinter.TkVersion})")
            elif module_name == 'win32print':
                import win32print
                report.append(f"✓ {module_name}: OK")
            elif module_name == 'win32api':
                import win32api
                report.append(f"✓ {module_name}: OK")
            elif module_name == 'PyPDF2':
                import PyPDF2
                report.append(f"✓ {module_name}: OK (version: {PyPDF2.__version__ if hasattr(PyPDF2, '__version__') else 'unknown'})")
            elif module_name == 'docx':
                import docx
                report.append(f"✓ {module_name}: OK")
            else:
                __import__(module_name)
                report.append(f"✓ {module_name}: OK")
        except ImportError as e:
            report.append(f"✗ {module_name}: MISSING - {e}")
        except Exception as e:
            report.append(f"✗ {module_name}: ERROR - {e}")
    report.append("")

    # Check Printer Access
    report.append("PRINTER DETECTION:")
    report.append("-" * 80)
    try:
        import win32print

        # Get available printers
        printers = win32print.EnumPrinters(
            win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        )

        if printers:
            report.append(f"Found {len(printers)} printers:")
            for idx, printer in enumerate(printers):
                printer_name = printer[2]
                report.append(f"  {idx + 1}. {printer_name}")

                # Try to get printer details
                try:
                    hprinter = win32print.OpenPrinter(printer_name)
                    try:
                        printer_info = win32print.GetPrinter(hprinter, 2)
                        driver = printer_info.get('pDriverName', 'Unknown')
                        port = printer_info.get('pPortName', 'Unknown')
                        report.append(f"     Driver: {driver}")
                        report.append(f"     Port: {port}")
                    except Exception as e:
                        report.append(f"     ERROR getting details: {e}")
                    finally:
                        win32print.ClosePrinter(hprinter)
                except Exception as e:
                    report.append(f"     ERROR opening printer: {e}")
        else:
            report.append("✗ NO PRINTERS FOUND")
            report.append("  Possible causes:")
            report.append("  - No printers installed on this system")
            report.append("  - Print spooler service not running")
            report.append("  - Permission issues")

        # Get default printer
        try:
            default_printer = win32print.GetDefaultPrinter()
            report.append(f"\nDefault Printer: {default_printer}")
        except Exception as e:
            report.append(f"\n✗ Could not get default printer: {e}")

    except ImportError:
        report.append("✗ win32print module not available")
        report.append("  Install with: pip install pywin32")
    except Exception as e:
        report.append(f"✗ ERROR accessing printers: {e}")
        report.append(f"  Traceback: {traceback.format_exc()}")
    report.append("")

    # Check Print Preset Manager
    report.append("PRINT PRESET MANAGER:")
    report.append("-" * 80)
    try:
        from print_preset_manager import PrintPresetManager

        preset_mgr = PrintPresetManager()
        presets = preset_mgr.get_all_presets()

        report.append(f"Preset file location: {preset_mgr.presets_file}")
        report.append(f"Found {len(presets)} presets:")

        for name, preset in presets.items():
            report.append(f"\n  Preset: {name}")
            report.append(f"    Default: {'Yes' if preset.is_default else 'No'}")
            report.append(f"    11x17: {'Enabled' if preset.printer_11x17_enabled else 'Disabled'}")
            if preset.printer_11x17_enabled:
                report.append(f"      Script: {preset.printer_11x17_script or '(not configured)'}")
                report.append(f"      Copies: {preset.printer_11x17_copies}")
            report.append(f"    24x36: {'Enabled' if preset.printer_24x36_enabled else 'Disabled'}")
            if preset.printer_24x36_enabled:
                report.append(f"      Script: {preset.printer_24x36_script or '(not configured)'}")
                report.append(f"      Copies: {preset.printer_24x36_copies}")
            report.append(f"    Folder Label: {'Enabled' if preset.folder_label_enabled else 'Disabled'}")
            if preset.folder_label_enabled:
                report.append(f"      Printer: {preset.folder_label_printer or '(not configured)'}")

    except ImportError as e:
        report.append(f"✗ Could not import PrintPresetManager: {e}")
    except Exception as e:
        report.append(f"✗ ERROR checking presets: {e}")
        report.append(f"  Traceback: {traceback.format_exc()}")
    report.append("")

    # Check Database
    report.append("DATABASE:")
    report.append("-" * 80)
    try:
        db_file = "document_manager_v2.1.db"
        if Path(db_file).exists():
            size = Path(db_file).stat().st_size
            report.append(f"✓ Database found: {db_file}")
            report.append(f"  Size: {size:,} bytes")

            # Try to connect
            import sqlite3
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            # Get table count
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            report.append(f"  Tables: {len(tables)}")

            # Get order count
            cursor.execute("SELECT COUNT(*) FROM relationships")
            order_count = cursor.fetchone()[0]
            report.append(f"  Total orders: {order_count}")

            conn.close()
        else:
            report.append(f"✗ Database not found: {db_file}")
    except Exception as e:
        report.append(f"✗ ERROR checking database: {e}")
    report.append("")

    # Check Template File
    report.append("TEMPLATE FILE:")
    report.append("-" * 80)
    try:
        template_paths = [
            "C:/code/Document Manager/DESIGN FILES/Template.docx",
            "DESIGN FILES/Template.docx",
            "templates/job_folder_template.docx"
        ]

        found = False
        for template_path in template_paths:
            if Path(template_path).exists():
                report.append(f"✓ Template found: {template_path}")
                size = Path(template_path).stat().st_size
                report.append(f"  Size: {size:,} bytes")
                found = True
                break

        if not found:
            report.append("✗ Template file not found")
            report.append("  Searched locations:")
            for path in template_paths:
                report.append(f"    - {path}")
    except Exception as e:
        report.append(f"✗ ERROR checking template: {e}")
    report.append("")

    # Test Print Functionality (dry run)
    report.append("PRINT FUNCTIONALITY TEST (DRY RUN):")
    report.append("-" * 80)
    try:
        from batch_print_with_presets import should_print_folder_label

        # Test folder label logic
        test_cases = [
            {"processed": False, "expected": True, "desc": "Green/Red category"},
            {"processed": True, "expected": False, "desc": "Gray (processed) category"}
        ]

        all_passed = True
        for test in test_cases:
            result = should_print_folder_label(test)
            expected = test["expected"]
            status = "✓" if result == expected else "✗"
            report.append(f"  {status} Folder label logic - {test['desc']}: {result} (expected {expected})")
            if result != expected:
                all_passed = False

        if all_passed:
            report.append("\n✓ All print logic tests passed")
        else:
            report.append("\n✗ Some print logic tests failed")

    except ImportError as e:
        report.append(f"✗ Could not import print modules: {e}")
    except Exception as e:
        report.append(f"✗ ERROR testing print functionality: {e}")
        report.append(f"  Traceback: {traceback.format_exc()}")
    report.append("")

    # Summary
    report.append("=" * 80)
    report.append("END OF DIAGNOSTIC REPORT")
    report.append("=" * 80)
    report.append("")
    report.append("INSTRUCTIONS:")
    report.append("1. Copy this entire report")
    report.append("2. Send it along with any error messages you see")
    report.append("3. Include a description of what you were trying to do when the error occurred")
    report.append("")

    return "\n".join(report)


def save_diagnostic_report(filename="print_diagnostic_report.txt"):
    """Generate and save diagnostic report to file"""
    try:
        report = generate_diagnostic_report()

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)

        return filename, report
    except Exception as e:
        return None, f"ERROR generating report: {e}\n{traceback.format_exc()}"


if __name__ == "__main__":
    print("Generating diagnostic report...\n")

    filename, report = save_diagnostic_report()

    if filename:
        print(report)
        print(f"\n\nReport saved to: {os.path.abspath(filename)}")
        print("\nYou can now:")
        print("1. Open the file and copy its contents")
        print("2. Or copy the output above")
        print("3. Send it for debugging")
    else:
        print(report)
