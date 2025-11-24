#!/usr/bin/env python3
"""
Quick script to show what bookmarks the template currently has
"""

import sys
import os

# Set path for jjanney's Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import win32com.client as win32
except ImportError:
    print("ERROR: pywin32 not installed")
    print("Run: INSTALL_FOR_JJANNEY.bat")
    input("Press Enter to exit...")
    sys.exit(1)

from pathlib import Path

def check_template():
    """Show current bookmarks in template"""

    template_path = Path(__file__).parent / "LABEL TEMPLATE" / "Contract_Lumber_Label_Template.docx"

    print("\n" + "="*70)
    print("CURRENT TEMPLATE BOOKMARKS")
    print("="*70)
    print(f"\nTemplate: {template_path}")

    if not template_path.exists():
        print(f"\n❌ ERROR: Template not found!")
        print(f"   Expected at: {template_path}")
        input("\nPress Enter to exit...")
        return

    print(f"✓ Template found")
    print(f"  Size: {template_path.stat().st_size:,} bytes\n")

    # Open Word
    print("Opening Word...")
    word_app = None
    doc = None

    try:
        word_app = win32.gencache.EnsureDispatch('Word.Application')
        word_app.Visible = False
        word_app.DisplayAlerts = False

        # Open template
        doc = word_app.Documents.Open(str(template_path.absolute()))

        # Get bookmarks
        bookmark_count = doc.Bookmarks.Count

        print(f"\n✓ Template opened successfully")
        print(f"\n" + "="*70)
        print(f"FOUND {bookmark_count} BOOKMARK(S)")
        print("="*70)

        if bookmark_count == 0:
            print("\n❌ NO BOOKMARKS FOUND IN TEMPLATE!")
            print("\nThis is why you're getting 'bookmark not found' error.")
            print("\nYou need to add bookmarks to the template.")
            print("See: ADD_BOOKMARKS_GUIDE.txt for instructions")
        else:
            print("\nCurrent bookmarks in template:")
            existing = []
            for i in range(1, bookmark_count + 1):
                name = doc.Bookmarks(i).Name
                existing.append(name)
                print(f"  {i}. {name}")

            print(f"\n" + "="*70)
            print("REQUIRED BOOKMARKS")
            print("="*70)

            required = {
                'builder': '✓' if 'builder' in existing else '❌ MISSING',
                'Lot / subdivision': '✓' if 'Lot / subdivision' in existing else '❌ MISSING',
                'floors': '✓' if 'floors' in existing else '❌ MISSING',
                'designer': '✓' if 'designer' in existing else '❌ MISSING',
            }

            print("\nRequired bookmarks:")
            for name, status in required.items():
                print(f"  {status}  {name}")

            optional = {
                'OrderNumber': '✓' if 'OrderNumber' in existing else '⚪ Not present',
                'DatePrinted': '✓' if 'DatePrinted' in existing else '⚪ Not present',
            }

            print("\nOptional bookmarks:")
            for name, status in optional.items():
                print(f"  {status}  {name}")

            # Check if all required are present
            missing = [name for name, status in required.items() if '❌' in status]

            if missing:
                print(f"\n" + "="*70)
                print("❌ TEMPLATE INCOMPLETE")
                print("="*70)
                print(f"\nMissing {len(missing)} required bookmark(s):")
                for name in missing:
                    print(f"  • {name}")
                print("\nSee: ADD_BOOKMARKS_GUIDE.txt for step-by-step instructions")
            else:
                print(f"\n" + "="*70)
                print("✅ TEMPLATE READY!")
                print("="*70)
                print("\nAll required bookmarks are present.")
                print("Folder label printing should work now.")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Close Word
        try:
            if doc:
                doc.Close(SaveChanges=False)
            if word_app:
                word_app.Quit()
        except:
            pass

    print("\n" + "="*70)
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    check_template()
