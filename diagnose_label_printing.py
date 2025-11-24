#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remote Diagnostic Tool - Label Printing Issues
Generates a report that can be shared for troubleshooting
"""

import sys
import os
from pathlib import Path
import json

# ASCII-safe symbols for Windows cmd compatibility
OK = "[OK]"
FAIL = "[X]"
ERROR = "[ERROR]"
WARNING = "[WARNING]"
INFO = "[INFO]"
BULLET = " *"

def diagnose_label_printing():
    """Run all diagnostics and generate a report"""

    print("\n" + "="*70)
    print("FOLDER LABEL PRINTING DIAGNOSTIC REPORT")
    print("="*70 + "\n")

    issues_found = []
    warnings_found = []
    info_messages = []

    # Get the root directory
    root_dir = Path(__file__).parent.resolve()

    print("=" * 70)
    print("1. CHECKING FILE LOCATIONS")
    print("=" * 70 + "\n")

    # Check template files
    template_locations = [
        root_dir / "LABEL TEMPLATE" / "Contract_Lumber_Label_Template.docx",
        root_dir / "DESIGN FILES" / "Template.docx",
        root_dir / "templates" / "job_folder_template.docx"
    ]

    template_found = None
    for template_path in template_locations:
        if template_path.exists():
            print(f"{OK} Template found: {template_path}")
            print(f"  Size: {template_path.stat().st_size:,} bytes")
            if template_found is None:
                template_found = template_path
                info_messages.append(f"Primary template: {template_path}")
        else:
            print(f"{FAIL} Template NOT found: {template_path}")

    if template_found is None:
        issues_found.append("NO TEMPLATE FILE FOUND - Label printing will fail")
        print(f"\n{ERROR} CRITICAL: No template file found in any expected location!")

    print("\n" + "=" * 70)
    print("2. CHECKING PRINT PRESETS CONFIGURATION")
    print("=" * 70 + "\n")

    # Check print presets
    preset_file = root_dir / "print_presets.json"
    if preset_file.exists():
        try:
            with open(preset_file, 'r') as f:
                presets = json.load(f)

            print(f"{OK} Found print_presets.json with {len(presets)} preset(s)\n")

            folder_printing_enabled = False
            has_printer_configured = False

            for preset_name, preset_config in presets.items():
                folder_enabled = preset_config.get('folder_label_enabled', False)
                folder_printer = preset_config.get('folder_label_printer', '')

                status = OK if folder_enabled else FAIL
                print(f"{status} Preset: '{preset_name}'")
                print(f"    Folder Label Enabled: {folder_enabled}")
                print(f"    Folder Label Printer: '{folder_printer}' {'(NOT CONFIGURED)' if not folder_printer else ''}")

                if folder_enabled:
                    folder_printing_enabled = True
                    if folder_printer:
                        has_printer_configured = True
                print()

            if not folder_printing_enabled:
                warnings_found.append("Folder label printing is DISABLED in all presets")
                print(f"{WARNING} Folder label printing is disabled in all presets")

            if folder_printing_enabled and not has_printer_configured:
                issues_found.append("Folder printing enabled but NO PRINTER is configured")
                print(f"{ERROR} CRITICAL: Folder printing is enabled but no printer is configured!")

            if has_printer_configured:
                info_messages.append("Folder printer is configured in at least one preset")

        except Exception as e:
            issues_found.append(f"Failed to read print_presets.json: {e}")
            print(f"{ERROR} reading print_presets.json: {e}")
    else:
        issues_found.append("print_presets.json file not found")
        print(f"{ERROR} CRITICAL: print_presets.json not found")

    print("\n" + "=" * 70)
    print("3. CHECKING WORD TEMPLATE BOOKMARKS")
    print("=" * 70 + "\n")

    print("Attempting to verify template bookmarks...\n")

    # Try to import win32com
    try:
        import win32com.client as win32
        word_available = True
        print(f"{OK} Microsoft Word COM interface available")
    except ImportError:
        word_available = False
        warnings_found.append("pywin32 not installed - cannot verify bookmarks automatically")
        print(f"{WARNING} pywin32 module not available")
        print("   Install with: pip install pywin32")

    if word_available and template_found:
        print(f"\nChecking bookmarks in: {template_found.name}\n")

        word_app = None
        doc = None
        try:
            # Start Word
            word_app = win32.gencache.EnsureDispatch('Word.Application')
            word_app.Visible = False
            word_app.DisplayAlerts = False

            # Open template
            doc = word_app.Documents.Open(str(template_found))

            # Get bookmarks
            bookmark_count = doc.Bookmarks.Count
            existing_bookmarks = []

            if bookmark_count > 0:
                print(f"Found {bookmark_count} bookmark(s):\n")
                for i in range(1, bookmark_count + 1):
                    bookmark_name = doc.Bookmarks(i).Name
                    existing_bookmarks.append(bookmark_name)
                    print(f"{BULLET} {bookmark_name}")
            else:
                issues_found.append("Template has ZERO bookmarks - no data can be filled")
                print(f"{ERROR} CRITICAL: Template has NO bookmarks!")

            print()

            # Check what the CODE expects
            code_expects = {
                'OrderNumber': 'Order Number',
                'Customer': 'Customer/Builder name',
                'LotSub': 'Job Reference/Lot',
                'Level': 'Delivery Area/Floors'
            }

            # Check what the DOCUMENTATION says
            doc_expects = {
                'builder': 'Customer name',
                'Lot / subdivision': 'Job reference/lot',
                'floors': 'Delivery area',
                'designer': 'Designer name'
            }

            print("Checking CODE requirements (word_template_processor.py):")
            code_missing = []
            for bookmark, description in code_expects.items():
                if bookmark in existing_bookmarks:
                    print(f"  {OK} {bookmark:<15} ({description})")
                else:
                    print(f"  {FAIL} {bookmark:<15} ({description}) - MISSING")
                    code_missing.append(bookmark)

            print("\nChecking DOCUMENTATION requirements (FOLDER_PRINTING_GUIDE.md):")
            doc_missing = []
            for bookmark, description in doc_expects.items():
                if bookmark in existing_bookmarks:
                    print(f"  {OK} {bookmark:<20} ({description})")
                else:
                    print(f"  {FAIL} {bookmark:<20} ({description}) - MISSING")
                    doc_missing.append(bookmark)

            print()

            # Determine the issue
            if code_missing and not doc_missing:
                issues_found.append("BOOKMARK MISMATCH: Template uses documentation names, but code expects different names")
                print(f"{ERROR} CRITICAL ISSUE FOUND:")
                print("   Your template has the DOCUMENTATION bookmarks (builder, floors, etc.)")
                print("   But the CODE looks for DIFFERENT bookmarks (Customer, LotSub, Level)")
                print("   -> The code needs to be updated to match your template")
            elif doc_missing and not code_missing:
                info_messages.append("Template uses code bookmark names (correct)")
                print(f"{OK} Template is correctly configured with CODE bookmark names")
            elif code_missing and doc_missing:
                issues_found.append("Template is missing ALL required bookmarks")
                print(f"{ERROR} CRITICAL: Template is missing required bookmarks")
            else:
                info_messages.append("Template has all required bookmarks")
                print(f"{OK} Template has all required bookmarks!")

        except Exception as e:
            warnings_found.append(f"Could not verify template: {e}")
            print(f"{WARNING} Could not open template: {e}")
        finally:
            try:
                if doc:
                    doc.Close(SaveChanges=False)
                if word_app:
                    word_app.Quit()
            except:
                pass

    print("\n" + "=" * 70)
    print("4. CHECKING CODE CONFIGURATION")
    print("=" * 70 + "\n")

    # Check main_v2_3.py for template path
    main_file = root_dir / "src" / "main_v2_3.py"
    if main_file.exists():
        with open(main_file, 'r') as f:
            content = f.read()
            if 'LABEL TEMPLATE' in content and 'Contract_Lumber_Label_Template.docx' in content:
                print(f"{OK} main_v2_3.py is configured to use:")
                print("  'LABEL TEMPLATE/Contract_Lumber_Label_Template.docx'")
                info_messages.append("Main app configured for correct template path")
            else:
                warnings_found.append("main_v2_3.py template path may need verification")

    # Check word_template_processor.py
    processor_file = root_dir / "src" / "word_template_processor.py"
    if processor_file.exists():
        with open(processor_file, 'r') as f:
            content = f.read()

            print(f"\n{OK} word_template_processor.py found")
            print("\nBookmarks the CODE will try to fill:")

            # Extract the bookmark filling lines
            lines = content.split('\n')
            for line in lines:
                if 'self._fill_bookmark' in line and not line.strip().startswith('#'):
                    print(f"  {line.strip()}")

    print("\n" + "=" * 70)
    print("5. DIAGNOSTIC SUMMARY")
    print("=" * 70 + "\n")

    if issues_found:
        print(f"{ERROR} CRITICAL ISSUES FOUND ({len(issues_found)}):\n")
        for i, issue in enumerate(issues_found, 1):
            print(f"  {i}. {issue}")
        print()

    if warnings_found:
        print(f"{WARNING} WARNINGS ({len(warnings_found)}):\n")
        for i, warning in enumerate(warnings_found, 1):
            print(f"  {i}. {warning}")
        print()

    if not issues_found and not warnings_found:
        print(f"{OK} NO CRITICAL ISSUES FOUND")
        print("\nIf label printing still doesn't work, check:")
        print("  1. The printer is online and accessible")
        print("  2. Microsoft Word is properly installed")
        print("  3. Check the log file: document_manager_v2.3.log")
        print()

    print("=" * 70)
    print("RECOMMENDED ACTIONS")
    print("=" * 70 + "\n")

    if "BOOKMARK MISMATCH" in str(issues_found):
        print("OPTION 1: Update the CODE to match your template bookmarks")
        print("  -> Edit: src/word_template_processor.py")
        print("  -> Change lines 83-86 and 340-343")
        print("  -> Replace: OrderNumber, Customer, LotSub, Level")
        print("  -> With: OrderNumber, builder, 'Lot / subdivision', floors, designer")
        print()
        print("OPTION 2: Update your TEMPLATE to match the code")
        print("  -> Open the template in Word")
        print("  -> Add bookmarks: OrderNumber, Customer, LotSub, Level")
        print("  -> Remove old bookmarks if needed")
        print()

    if "NO PRINTER is configured" in str(issues_found):
        print("CONFIGURE A PRINTER:")
        print("  1. Run the application")
        print("  2. Go to Print Settings")
        print("  3. Enable 'Folder Printer'")
        print("  4. Select a printer from the dropdown")
        print("  5. The setting will be saved automatically")
        print()

    print("=" * 70)
    print("END OF DIAGNOSTIC REPORT")
    print("=" * 70 + "\n")

    print("Please share this report for troubleshooting assistance.")
    print("Log file location: document_manager_v2.3.log")
    print()

    # Return status code
    return 0 if not issues_found else 1


if __name__ == "__main__":
    try:
        exit_code = diagnose_label_printing()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n{ERROR} DIAGNOSTIC SCRIPT ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
