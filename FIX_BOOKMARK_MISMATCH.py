#!/usr/bin/env python3
"""
Quick Fix Script - Bookmark Mismatch Issue
Automatically patches word_template_processor.py to use correct bookmark names
"""

import shutil
from pathlib import Path
from datetime import datetime

def fix_bookmark_mismatch():
    """Apply the bookmark mismatch fix to word_template_processor.py"""

    print("\n" + "="*70)
    print("BOOKMARK MISMATCH FIX")
    print("="*70 + "\n")

    root_dir = Path(__file__).parent.resolve()
    processor_file = root_dir / "src" / "word_template_processor.py"

    if not processor_file.exists():
        print(f"❌ ERROR: Could not find {processor_file}")
        print("   Make sure you're running this from the Document Manager folder")
        return False

    print(f"Target file: {processor_file}")
    print()

    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = processor_file.with_suffix(f'.py.backup_{timestamp}')

    try:
        print(f"Creating backup: {backup_file.name}")
        shutil.copy2(processor_file, backup_file)
        print("✓ Backup created successfully")
        print()
    except Exception as e:
        print(f"❌ ERROR creating backup: {e}")
        return False

    # Read the file
    try:
        with open(processor_file, 'r', encoding='utf-8') as f:
            content = f.read()
            original_content = content
    except Exception as e:
        print(f"❌ ERROR reading file: {e}")
        return False

    # Apply fixes
    print("Applying fixes...\n")

    changes_made = 0

    # Fix #1: Update fill_and_print_template method (lines ~83-86)
    old_code_1 = '''self._fill_bookmark(doc, "OrderNumber", job_data.get('OrderNumber', ''))  # OrderNumber → OrderNumber
            self._fill_bookmark(doc, "Customer", job_data.get('Customer', ''))        # Customer → Customer
            self._fill_bookmark(doc, "LotSub", job_data.get('JobReference', ''))      # JobReference → LotSub
            self._fill_bookmark(doc, "Level", job_data.get('DeliveryArea', ''))       # DeliveryArea → Level'''

    new_code_1 = '''self._fill_bookmark(doc, "builder", job_data.get('Customer', ''))          # Customer → builder
            self._fill_bookmark(doc, "Lot / subdivision", job_data.get('JobReference', ''))  # JobReference → Lot / subdivision
            self._fill_bookmark(doc, "floors", job_data.get('DeliveryArea', ''))      # DeliveryArea → floors
            self._fill_bookmark(doc, "designer", job_data.get('Designer', ''))        # Designer → designer
            self._fill_bookmark(doc, "OrderNumber", job_data.get('OrderNumber', ''))  # OrderNumber → OrderNumber (optional)'''

    if old_code_1 in content:
        content = content.replace(old_code_1, new_code_1)
        changes_made += 1
        print("✓ Fixed fill_and_print_template method (lines 83-86)")
    else:
        print("⚠️  Could not find expected code in fill_and_print_template method")

    # Fix #2: Update fill_template_to_file method (lines ~340-343)
    old_code_2 = '''self._fill_bookmark(doc, "OrderNumber", job_data.get('OrderNumber', ''))  # OrderNumber → OrderNumber
            self._fill_bookmark(doc, "Customer", job_data.get('Customer', ''))        # Customer → Customer
            self._fill_bookmark(doc, "LotSub", job_data.get('JobReference', ''))      # JobReference → LotSub
            self._fill_bookmark(doc, "Level", job_data.get('DeliveryArea', ''))       # DeliveryArea → Level'''

    new_code_2 = '''self._fill_bookmark(doc, "builder", job_data.get('Customer', ''))          # Customer → builder
            self._fill_bookmark(doc, "Lot / subdivision", job_data.get('JobReference', ''))  # JobReference → Lot / subdivision
            self._fill_bookmark(doc, "floors", job_data.get('DeliveryArea', ''))      # DeliveryArea → floors
            self._fill_bookmark(doc, "designer", job_data.get('Designer', ''))        # Designer → designer
            self._fill_bookmark(doc, "OrderNumber", job_data.get('OrderNumber', ''))  # OrderNumber → OrderNumber (optional)'''

    if old_code_2 in content:
        content = content.replace(old_code_2, new_code_2)
        changes_made += 1
        print("✓ Fixed fill_template_to_file method (lines 340-343)")
    else:
        print("⚠️  Could not find expected code in fill_template_to_file method")

    print()

    if changes_made == 0:
        print("❌ No changes were made - the code may already be fixed or has been modified")
        print("   Please manually verify the bookmark names in word_template_processor.py")
        return False

    # Write the updated file
    try:
        with open(processor_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Updated {processor_file.name}")
        print()
    except Exception as e:
        print(f"❌ ERROR writing file: {e}")
        print("   Restoring backup...")
        try:
            shutil.copy2(backup_file, processor_file)
            print("   ✓ Backup restored")
        except:
            print("   ❌ Could not restore backup!")
        return False

    print("="*70)
    print("✓ FIX APPLIED SUCCESSFULLY!")
    print("="*70 + "\n")

    print("Changes made:")
    print(f"  • Updated {changes_made} method(s)")
    print(f"  • Backup saved: {backup_file.name}")
    print()

    print("Updated bookmark mapping:")
    print("  • Customer     → 'builder'")
    print("  • JobReference → 'Lot / subdivision'")
    print("  • DeliveryArea → 'floors'")
    print("  • Designer     → 'designer'")
    print("  • OrderNumber  → 'OrderNumber' (optional)")
    print()

    print("="*70)
    print("NEXT STEPS")
    print("="*70)
    print()
    print("1. Restart the Document Manager application")
    print("2. Run DIAGNOSE_LABEL_PRINTING.bat to verify the fix")
    print("3. Test print a single folder label")
    print()
    print("If something goes wrong, restore the backup:")
    print(f"   Copy: {backup_file.name}")
    print(f"   To:   word_template_processor.py")
    print()

    return True


if __name__ == "__main__":
    import sys

    print("This script will fix the bookmark mismatch issue in word_template_processor.py")
    print()
    response = input("Do you want to continue? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("Operation cancelled.")
        sys.exit(0)

    try:
        success = fix_bookmark_mismatch()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
