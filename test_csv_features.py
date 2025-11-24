#!/usr/bin/env python3
"""
Test script to demonstrate CSV validation features
Run this to see the CSV cleanup functionality
"""

import sys
import os
import tkinter as tk

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from csv_cleanup_dialog import show_csv_cleanup_dialog
from enhanced_database_manager import EnhancedDatabaseManager

def main():
    print("=" * 75)
    print("CSV Validation & Cleanup Test")
    print("=" * 75)
    print()
    print("This will open the CSV cleanup dialog for testing.")
    print()
    print("Features to test:")
    print("  1. CSV file scanning and order number extraction")
    print("  2. SKU validation against products file")
    print("  3. Data quality checks (quantities, fields)")
    print("  4. Auto-fix suggestions")
    print("  5. Upload to BisTrack import folder")
    print()

    # Initialize database
    db = EnhancedDatabaseManager("test_csv_features.db")

    # CSV folder (same as PDFs per your requirements)
    # Try to find sample csv folder
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sample_csv = os.path.join(base_dir, "sample csv")

    if os.path.exists(sample_csv):
        csv_folder = sample_csv
        print(f"Using sample CSV folder: {sample_csv}")
    else:
        csv_folder = r"C:\Users\m_kun\Downloads"
        print(f"Using CSV folder: {csv_folder}")

    # Products file for SKU validation
    products_file = os.path.join(sample_csv, "products_master.csv") if os.path.exists(sample_csv) else None
    if products_file and not os.path.exists(products_file):
        print()
        print("⚠️  Warning: Products file not found at:")
        print(f"   {products_file}")
        print("   SKU validation will be skipped")
        print()
        products_file = None
    else:
        print(f"Using products file: {products_file}")

    print()
    print("Opening CSV Cleanup Dialog...")
    print()

    # Create Tkinter root
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Show dialog
    show_csv_cleanup_dialog(root, db, csv_folder, products_file)

    print()
    print("Dialog closed.")
    print()
    print("Test complete!")

if __name__ == "__main__":
    main()
