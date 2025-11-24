#!/usr/bin/env python3
"""Check bookmarks in the OneDrive template that's actually being used"""

import sys

try:
    import win32com.client as win32
except ImportError:
    print("ERROR: pywin32 not installed")
    input("Press Enter to exit...")
    sys.exit(1)

import os
from pathlib import Path

print("\n" + "="*70)
print("CHECKING TEMPLATE BOOKMARKS")
print("="*70)

# Try to find template automatically
script_dir = Path(__file__).parent
template_filename = "Contract_Lumber_Label_Template.docx"

# Try relative path first (standard deployment)
template_path = script_dir / "LABEL TEMPLATE" / template_filename

if not template_path.exists():
    # Try OneDrive locations
    username = os.environ.get('USERNAME', '')
    possible_paths = [
        Path(f"C:/Users/{username}/Contract Lumber/Designers (FB) - General/BISTRACK CONNECTOR/Document Manager/LABEL TEMPLATE/{template_filename}"),
        Path(f"C:/Users/{username}/OneDrive/Apps/DocumentManager/LABEL TEMPLATE/{template_filename}"),
        Path(f"C:/Users/{username}/OneDrive - Contract Lumber/BISTRACK CONNECTOR/Document Manager/LABEL TEMPLATE/{template_filename}"),
    ]

    for path in possible_paths:
        if path.exists():
            template_path = path
            break
    else:
        print("\n❌ Could not automatically locate template!")
        print("\nSearched locations:")
        print(f"  1. {script_dir / 'LABEL TEMPLATE' / template_filename}")
        for i, path in enumerate(possible_paths, 2):
            print(f"  {i}. {path}")

        custom_path = input("\nEnter full path to template (or press Enter to exit): ").strip()
        if custom_path:
            template_path = Path(custom_path)
        else:
            sys.exit(1)

print(f"\nTemplate: {template_path}")

if not template_path.exists():
    print(f"\n❌ Template not found at this location!")
    print("\nThe file doesn't exist at the specified path.")
    input("\nPress Enter to exit...")
    sys.exit(1)

print(f"✓ Template found\n")

word_app = None
doc = None

try:
    print("Opening Word...")
    word_app = win32.gencache.EnsureDispatch('Word.Application')
    word_app.Visible = False
    word_app.DisplayAlerts = False

    doc = word_app.Documents.Open(template_path)

    bookmark_count = doc.Bookmarks.Count

    print(f"\n{'='*70}")
    print(f"FOUND {bookmark_count} BOOKMARK(S) IN TEMPLATE")
    print("="*70)

    if bookmark_count == 0:
        print("\n❌ NO BOOKMARKS!")
        print("This template has no bookmarks at all.")
    else:
        print("\nBookmarks in template:")
        existing = []
        for i in range(1, bookmark_count + 1):
            name = doc.Bookmarks(i).Name
            existing.append(name)
            print(f"  {i}. [{name}]")

        print(f"\n{'='*70}")
        print("REQUIRED BOOKMARKS CHECK")
        print("="*70)

        required = {
            'Customer': 'Customer/Builder name',
            'JobReference': 'Job reference/Lot',
            'DeliveryArea': 'Delivery area',
            'OrderNumber': 'Order number',
        }

        print("\nChecking required bookmarks:")
        missing = []
        for name, desc in required.items():
            if name in existing:
                print(f"  ✓ {name:<20} ({desc})")
            else:
                print(f"  ❌ {name:<20} ({desc}) - MISSING!")
                missing.append(name)

        if 'Designer' in existing:
            print(f"  ✓ Designer           (optional)")

        if missing:
            print(f"\n{'='*70}")
            print("❌ TEMPLATE INCOMPLETE")
            print("="*70)
            print(f"\nMissing {len(missing)} required bookmark(s):")
            for name in missing:
                print(f"  • {name}")
            print("\nYou need to add these bookmarks to the template.")
            print("See: ADD_BOOKMARKS_GUIDE.txt")
        else:
            print(f"\n{'='*70}")
            print("✅ TEMPLATE COMPLETE!")
            print("="*70)
            print("\nAll required bookmarks present!")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    try:
        if doc:
            doc.Close(SaveChanges=False)
        if word_app:
            word_app.Quit()
    except:
        pass

print("\n" + "="*70)
input("\nPress Enter to exit...")
