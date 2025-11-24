#!/usr/bin/env python3
"""
Utility to verify Word template bookmarks
Checks if the template has the required bookmarks for folder labels
"""

import win32com.client as win32
from pathlib import Path
import sys
import os
import shutil

def get_word_application():
    """
    Get Word application instance with automatic cache clearing on AttributeError

    This fixes the common "module 'win32com.gen_py.00020905' has no attribute" error
    by clearing the corrupted COM type library cache and using late-bound Dispatch.

    Returns:
        Word.Application COM object
    """
    try:
        # Try with gencache first (faster, early-bound)
        return win32.gencache.EnsureDispatch('Word.Application')

    except AttributeError as e:
        # Cache is corrupted - immediately use late-bound Dispatch
        # Don't try to rebuild cache as it may fail during AddModuleToCache
        print(f"⚠️  win32com cache corrupted: {str(e)}")
        print("ℹ️  Using late-bound dispatch for Word...")

        # Clear cache for next time (but don't try to rebuild now)
        try:
            gen_py_path = win32.gencache.GetGeneratePath()
            if os.path.exists(gen_py_path):
                print(f"   Clearing cache: {gen_py_path}")
                shutil.rmtree(gen_py_path, ignore_errors=True)
                print("   Cache cleared - will rebuild on next run")
        except Exception as clear_error:
            print(f"   Could not clear cache: {clear_error}")

        # Use late-bound Dispatch (works without cache)
        return win32.Dispatch('Word.Application')

    except Exception as e:
        # Other errors - try late-bound dispatch
        print(f"⚠️  Error with gencache: {str(e)}")
        print("ℹ️  Using late-bound dispatch for Word...")
        return win32.Dispatch('Word.Application')

def verify_template_bookmarks(template_path: str):
    """
    Check what bookmarks exist in a Word template

    Args:
        template_path: Path to the Word template file
    """
    word_app = None
    doc = None

    try:
        # Required bookmarks for folder labels
        required_bookmarks = {
            'builder': 'Customer name',
            'Lot / subdivision': 'Job reference/lot',
            'floors': 'Delivery area',
            'designer': 'Designer name'
        }

        optional_bookmarks = {
            'OrderNumber': 'Order number',
            'DatePrinted': 'Print timestamp'
        }

        # Check if template exists
        template_path_abs = Path(template_path).resolve()
        if not template_path_abs.exists():
            print(f"❌ Template file not found: {template_path_abs}")
            return False

        print(f"\n{'='*70}")
        print(f"Word Template Verification")
        print(f"{'='*70}")
        print(f"Template: {template_path_abs}")
        print()

        # Start Word application with automatic cache clearing
        print("Opening Word...")
        word_app = get_word_application()
        word_app.Visible = False
        word_app.DisplayAlerts = False

        # Open template
        doc = word_app.Documents.Open(str(template_path_abs))

        # Get all bookmarks
        bookmark_count = doc.Bookmarks.Count
        print(f"Found {bookmark_count} bookmark(s) in template\n")

        if bookmark_count == 0:
            print("⚠️  WARNING: No bookmarks found in template!")
            print("\nTo add bookmarks in Word:")
            print("  1. Open the template in Microsoft Word")
            print("  2. Select the text where you want the data to appear")
            print("  3. Go to Insert > Bookmark")
            print("  4. Enter the bookmark name (e.g., 'builder')")
            print("  5. Click Add")
            print()
            return False

        # List all existing bookmarks
        print("Existing bookmarks in template:")
        existing_bookmarks = []
        for i in range(1, bookmark_count + 1):
            bookmark = doc.Bookmarks(i)
            bookmark_name = bookmark.Name
            existing_bookmarks.append(bookmark_name)
            print(f"  • {bookmark_name}")

        print()

        # Check required bookmarks
        print("Required bookmarks for folder labels:")
        missing_required = []
        for bookmark_name, description in required_bookmarks.items():
            if bookmark_name in existing_bookmarks:
                print(f"  ✓ {bookmark_name:<20} ({description})")
            else:
                print(f"  ❌ {bookmark_name:<20} ({description}) - MISSING")
                missing_required.append(bookmark_name)

        print()

        # Check optional bookmarks
        print("Optional bookmarks:")
        for bookmark_name, description in optional_bookmarks.items():
            if bookmark_name in existing_bookmarks:
                print(f"  ✓ {bookmark_name:<20} ({description})")
            else:
                print(f"  ⚪ {bookmark_name:<20} ({description}) - Not present")

        print()

        # Summary
        if missing_required:
            print(f"{'='*70}")
            print("❌ TEMPLATE SETUP INCOMPLETE")
            print(f"{'='*70}")
            print(f"\nMissing {len(missing_required)} required bookmark(s):")
            for bookmark in missing_required:
                print(f"  • {bookmark}")
            print("\nPlease add these bookmarks to your template:")
            print("\n  1. Open template in Word: " + str(template_path_abs))
            print("  2. Select text where data should appear")
            print("  3. Insert > Bookmark")
            print("  4. Add bookmark with exact name (case-sensitive)")
            print()
            return False
        else:
            print(f"{'='*70}")
            print("✅ TEMPLATE SETUP COMPLETE")
            print(f"{'='*70}")
            print("\nAll required bookmarks are present!")
            print("The template is ready to use for folder label printing.")
            print()
            return True

    except Exception as e:
        print(f"\n❌ Error verifying template: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Clean up
        try:
            if doc:
                doc.Close(SaveChanges=False)
            if word_app:
                word_app.Quit()
        except:
            pass


def main():
    # Default template path
    default_template = "C:/code/Document Manager/DESIGN FILES/Template.docx"

    # Allow custom path via command line
    if len(sys.argv) > 1:
        template_path = sys.argv[1]
    else:
        template_path = default_template

    verify_template_bookmarks(template_path)


if __name__ == "__main__":
    main()
