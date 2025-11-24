#!/usr/bin/env python3
"""
Document Manager V2.4 - Application Launcher
BisTrack CSV Import Management & Validation
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from main_v2_4 import main

    if __name__ == "__main__":
        print("=" * 75)
        print("Document Manager V2.4 - BisTrack CSV Management")
        print("=" * 75)
        print()
        print("📊 EXISTING FEATURES FROM V2.3")
        print("   • Enhanced calendar view with daily statistics")
        print("   • Category-based order management (Ready/Missing/Processed)")
        print("   • Batch PDF printing with automatic archiving")
        print("   • Real-time PDF attachment and status updates")
        print()
        print("📦 NEW: BISTRACK CSV IMPORT MANAGEMENT")
        print("   • 📂 Scan CSV folder for material import files")
        print("   • 🔍 Automatic order number extraction from CSV content")
        print("   • ✓ SKU validation against products master file")
        print("   • 🔧 Data quality checks (quantities, required fields)")
        print("   • 🛠️  Auto-fix suggestions for common errors")
        print("   • 📤 Upload validated CSVs to BisTrack import folder")
        print()
        print("🎯 CSV WORKFLOW")
        print("   1. Click 'BisTrack CSVs' button in main window")
        print("   2. Review CSV files with validation status")
        print("   3. Validate files (checks SKUs, quantities, etc.)")
        print("   4. Apply auto-fixes if needed")
        print("   5. Upload clean files to BisTrack import folder")
        print()
        print("⚙️  CSV SETTINGS")
        print("   • Configure products file path for SKU validation")
        print("   • Set BisTrack import folder location")
        print("   • Access via Settings → File Locations")
        print()
        print("Starting Document Manager V2.4...")
        print()

        main()

except ImportError as e:
    print(f"Import error: {e}")
    print("Please make sure all required packages are installed:")
    print("pip install pandas PyPDF2")
    sys.exit(1)
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1)