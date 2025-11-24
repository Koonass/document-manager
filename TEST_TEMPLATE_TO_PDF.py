#!/usr/bin/env python3
"""
Test template bookmark filling by creating a PDF
This lets you verify bookmarks are being filled correctly
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import win32com.client as win32
except ImportError:
    print("ERROR: pywin32 not installed")
    print("Run: INSTALL_FOR_JJANNEY.bat")
    input("Press Enter to exit...")
    sys.exit(1)

print("\n" + "="*70)
print("TEST TEMPLATE BOOKMARK FILLING")
print("="*70)
print("\nThis will:")
print("1. Open the Word template")
print("2. Fill it with test data")
print("3. Save as PDF")
print("4. You can verify the bookmarks were filled correctly")
print()

# Test data
test_data = {
    'Customer': 'TEST CUSTOMER NAME - ABC Construction',
    'OrderNumber': '9999999',
    'JobReference': 'TEST LOT 123 - Subdivision Name',
    'DeliveryArea': 'TEST AREA - 2nd Floor',
    'Designer': 'TEST DESIGNER - John Smith'
}

print("Test data that will be filled:")
print(f"  Customer: {test_data['Customer']}")
print(f"  Order Number: {test_data['OrderNumber']}")
print(f"  Job Reference: {test_data['JobReference']}")
print(f"  Delivery Area: {test_data['DeliveryArea']}")
print(f"  Designer: {test_data['Designer']}")
print()

# Try to find template in multiple locations
possible_paths = [
    Path(r"C:\Users\jjanney\Contract Lumber\Designers (FB) - General\BISTRACK CONNECTOR\Document Manager\LABEL TEMPLATE\Contract_Lumber_Label_Template.docx"),
    Path(__file__).parent / "LABEL TEMPLATE" / "Contract_Lumber_Label_Template.docx",
    Path("C:/code/Document Manager/LABEL TEMPLATE/Contract_Lumber_Label_Template.docx"),
]

template_path = None
for path in possible_paths:
    if path.exists():
        template_path = path
        break

if template_path is None:
    print("❌ ERROR: Could not find template in any expected location!")
    print("\nSearched in:")
    for path in possible_paths:
        print(f"  - {path}")
    print("\nPlease run DEBUG_TEMPLATE_PATH.bat to find the template")
    input("\nPress Enter to exit...")
    sys.exit(1)

print(f"Template: {template_path.name}")
print(f"Location: {template_path.parent}")
print()

if not template_path.exists():
    print(f"❌ ERROR: Template not found!")
    print(f"   Expected: {template_path}")
    input("\nPress Enter to exit...")
    sys.exit(1)

print("✓ Template found")
print()

# Output PDF path
output_pdf = Path(__file__).parent / "TEST_LABEL_OUTPUT.pdf"

print(f"Output PDF: {output_pdf.name}")
print()

word_app = None
doc = None

try:
    print("Opening Word...")
    word_app = win32.gencache.EnsureDispatch('Word.Application')
    word_app.Visible = False  # Set to True if you want to see what's happening
    word_app.DisplayAlerts = False

    print("Opening template...")
    doc = word_app.Documents.Open(str(template_path))
    print("✓ Template opened")
    print()

    # Get list of bookmarks
    bookmark_count = doc.Bookmarks.Count
    print(f"Found {bookmark_count} bookmark(s) in template:")

    existing_bookmarks = []
    for i in range(1, bookmark_count + 1):
        bookmark_name = doc.Bookmarks(i).Name
        existing_bookmarks.append(bookmark_name)
        print(f"  {i}. {bookmark_name}")

    print()
    print("="*70)
    print("Filling bookmarks...")
    print("="*70)
    print()

    # Try to fill each bookmark
    def fill_bookmark(doc, bookmark_name, value):
        """Fill a bookmark if it exists"""
        try:
            if doc.Bookmarks.Exists(bookmark_name):
                bookmark_range = doc.Bookmarks(bookmark_name).Range
                bookmark_range.Text = str(value) if value else ""
                # Recreate bookmark
                doc.Bookmarks.Add(bookmark_name, bookmark_range)
                print(f"  ✓ Filled '{bookmark_name}' = '{value}'")
                return True
            else:
                print(f"  ⚠ Bookmark '{bookmark_name}' not found in template (skipping)")
                return False
        except Exception as e:
            print(f"  ❌ Error filling '{bookmark_name}': {e}")
            return False

    # Try to fill all bookmarks (based on what we expect)
    filled_count = 0
    filled_count += fill_bookmark(doc, "Customer", test_data['Customer'])
    filled_count += fill_bookmark(doc, "OrderNumber", test_data['OrderNumber'])
    filled_count += fill_bookmark(doc, "JobReference", test_data['JobReference'])
    filled_count += fill_bookmark(doc, "DeliveryArea", test_data['DeliveryArea'])
    filled_count += fill_bookmark(doc, "Designer", test_data['Designer'])

    print()
    print(f"Successfully filled {filled_count} bookmark(s)")
    print()

    # Save as PDF
    print("="*70)
    print("Saving as PDF...")
    print("="*70)
    print()

    # PDF format constant
    wdFormatPDF = 17

    try:
        doc.SaveAs(str(output_pdf), FileFormat=wdFormatPDF)
        print(f"✓ PDF saved: {output_pdf}")
        print()
    except Exception as e:
        print(f"❌ Error saving PDF: {e}")
        print()
        print("Trying alternative method...")
        # Try ExportAsFixedFormat
        doc.ExportAsFixedFormat(str(output_pdf), ExportFormat=wdFormatPDF)
        print(f"✓ PDF saved: {output_pdf}")
        print()

    print("="*70)
    print("✅ SUCCESS!")
    print("="*70)
    print()
    print(f"PDF created: {output_pdf}")
    print()
    print("NEXT STEPS:")
    print("1. Open the PDF file")
    print("2. Verify that the test data appears in the correct places")
    print("3. Check which bookmarks were filled successfully")
    print()
    print("If some bookmarks weren't filled:")
    print("  → Those bookmarks don't exist in the template")
    print("  → You need to add them in Word (INSERT → Bookmark)")
    print()
    print("If all bookmarks filled correctly:")
    print("  → Template is working!")
    print("  → Issue is with printer configuration")
    print("  → Change printer from '\\\\vcoloprint\\FB-Labels' to 'TSC TTP-245C'")
    print()

    # Try to open the PDF
    try:
        import subprocess
        subprocess.Popen([str(output_pdf)], shell=True)
        print("Opening PDF...")
    except:
        print("(Could not auto-open PDF)")

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

print()
print("="*70)
input("\nPress Enter to exit...")
